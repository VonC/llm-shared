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

## Round 1 by requestor - Step 5

- Recorded: 2026-11-10T09:27:23+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 5
- Outcome: request

### Review identity for step 5 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 5
Review round: 1

### Code review evidence for step 5 shared_lifecycle_gate (round 1)

request_index_tree: d25285c5081a72593a918582f878499077327fea
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "missing", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): reduce scenario setup costs
group 1 path: tests/memory_filesystem.py
group 1 path: tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
group 1 path: tests/unit/tools/test_groundhog_durations_pbt.py
group 2: feat(groundhog): prepare every pytest child
group 2 path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/test_groundhog_activation_tdd.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_day.py
group 2 path: tests/unit/tools/test_groundhog_cli.py
group 2 path: tests/unit/tools/test_groundhog_commands.py
group 2 path: tests/unit/tools/test_groundhog_runner.py
group 2 path: tests/unit/tools/test_groundhog_selection.py
group 2 path: tools/groundhog/__init__.py
group 2 path: tools/groundhog/cli.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/day.py
group 2 path: tools/groundhog/pytest_environment.py
group 2 path: tools/groundhog/runner.py
group 2 path: tools/groundhog/selection.py
group 3: docs(shared_lifecycle_gate): record step 5 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/test_groundhog_activation_tdd.py
staged path: tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance_day.py
staged path: tests/unit/tools/test_groundhog_cli.py
staged path: tests/unit/tools/test_groundhog_commands.py
staged path: tests/unit/tools/test_groundhog_durations_pbt.py
staged path: tests/unit/tools/test_groundhog_runner.py
staged path: tests/unit/tools/test_groundhog_selection.py
staged path: tools/groundhog/__init__.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/groundhog/pytest_environment.py
staged path: tools/groundhog/runner.py
staged path: tools/groundhog/selection.py
```

### Validation scope for step 5 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 5 shared_lifecycle_gate (round 1)

Step 5 is fully implemented. The validation plan records: Yes. Step 5 has been fully implemented.

The shared preparation adapter covers every pytest stage and both collection probes. Invocation binding checks happen before dispatch, detached launching and saved-proof decisions; each stage checks again. Whole normalized roots compare case insensitively on Windows, including nested and sibling root rejection. Child overrides support removals and restore the parent's exact state after the spawn factory returns or raises.

Static checks: the last self-hosted groundhog day passed all project checks. Ruff corrected one import order before the test stage. Changed Python files remain below the 650 physical line ceiling; commands is 620 lines and CLI is 557.

Tests: the corrected focused run passed 257 tests in 9.9s, zero warnings or expected failures. The last self-hosted ghog day --whole-suite ran 6120 affected tests, with no behavioral assertion failures, warnings or expected failures. Its authoritative result is done exit=2 because one lifecycle wall limit remained exceeded. Coverage configuration covers tools and excludes tests and package markers; no measured coverage percentage is claimed from runs without coverage.

Performance exception explicitly authorized by the user: tests/unit/test_scenario_storage.py::test_sqlite_close_retains_commit_and_discards_pending_write used CPU 0.015625s against 0.100s, with wall 1.730184s against 1s. The user asked about actual CPU, then said: "OK, when you have CPU under budget, do move on". This authorizes proceeding despite this wall-only failure. Do not describe the automated gate as green or change limits to hide it. No exclusions or baselines were added or raised. Isolated profiling measured body about 0.005s, setup 0.007s and teardown 0.003s; no safe removable cost was identified. The broad wall delay remains unattributed.

Architecture and integrity: one adapter bridges groundhog to the existing shared builder. Preparation errors remain setup errors and cannot be swallowed by collection fallback or produce judged proof. Existing consumer interpreter resolution, coverage, worker controls and startup diagnostic text are preserved. Steps 6 and 7 remain separate and unimplemented.

Retained evidence: .reviews/a.shared_lifecycle_gate.step5.tmp.day-one-failure.log and .reviews/a.shared_lifecycle_gate.step5.tmp.profile-sqlite.txt. The user exception replaces the ordinary requirement for a green validation walk for this remaining wall-only failure; no unchanged rerun was made to seek a favorable timing result.

### Implementation report for step 5 shared_lifecycle_gate (round 1)

Groundhog now prepares every pytest child through the shared lifecycle environment builder from the current checkout. The adapter rejects foreign project bindings using whole normalized root equality, combines the prepared delta with existing child overrides, and represents removals explicitly.

CLI invocation setup checks commands that can start pytest before any dispatch, detached child or saved-proof decision. Stage preparation rechecks the binding. Both collection probes receive preparation, and preparation failures propagate as setup errors rather than triggering ordinary collection fallback. A day probe failure exits setup with code 5 and remains unjudged for proof.

The runner temporarily applies additions and removals for process creation, then restores exact prior presence and values immediately after the spawn factory, including failure. It keeps existing consumer interpreter selection, coverage environment and worker settings.

Behavior tests cover the finite four-selection by six-stage/probe matrix, same-root stale preparation and deselection, foreign nested and sibling roots, detached day and saved proof, consumer interpreter, fallback and preparation failure, coverage and workers, and restoration on success and failure. Tests use injected process observations; activation tests exercise the real shared builder.

Performance repairs use the established memory filesystem for CLI, selection, activation and compatibility scenarios. Only two gate contract artifact families use that route, preserving native inline pytest imports. Immutable reviewer instructions are read lazily once, with the first read measured. The excluded-duration property reuses the integer ranked generator with its original domain, example count and assertions. No test checks or timing limits were weakened.

Validation: 257 focused tests passed in 9.9s; all project checks passed on the last self-hosted day. Its 6120 affected tests had no behavioral assertion failures and one accepted wall-only lifecycle failure: CPU 0.015625s below 0.100s, wall 1.730184s above 1s, authoritative exit=2. User explicitly instructed continuation when CPU is under budget. No exclusion or raised baseline exists. The resolved validation set is retained as declared by the renderer; this report does not claim a green speed proof or a measured coverage percentage.

Writer notes: .reviews/a.shared_lifecycle_gate.step5.journal.md and .reviews/a.shared_lifecycle_gate.step5.handoff.md.

### Change summary for step 5 shared_lifecycle_gate (round 1)

All 19 intended paths are staged. Root a.commit was formatted with wac and commit-plan-check returned ready=true with no diagnostics. Changed Markdown passed markdownlint and spelling checks.

Group 1, perf(tests): reduce scenario setup costs:

- tests/memory_filesystem.py
- tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
- tests/unit/tools/test_groundhog_durations_pbt.py

Group 2, feat(groundhog): prepare every pytest child:

- `tests/unit/tools/shared_lifecycle/test_groundhog_activation/__init__.py`
- tests/unit/tools/shared_lifecycle/test_groundhog_activation/test_groundhog_activation_tdd.py
- tests/unit/tools/test_groundhog_acceptance_day.py
- tests/unit/tools/test_groundhog_cli.py
- tests/unit/tools/test_groundhog_commands.py
- tests/unit/tools/test_groundhog_runner.py
- tests/unit/tools/test_groundhog_selection.py
- `tools/groundhog/__init__.py`
- tools/groundhog/cli.py
- tools/groundhog/commands.py
- tools/groundhog/context.py
- tools/groundhog/day.py
- tools/groundhog/pytest_environment.py
- tools/groundhog/runner.py
- tools/groundhog/selection.py

Group 3, docs(shared_lifecycle_gate): record step 5 validation:

- docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md

The validation group is last and uses the exact required completion title. No commits have been created.

### Human guidance and writer response for step 5 shared_lifecycle_gate (round 1)

Human guidance:

Human guidance for this review: "OK, when you have CPU under budget, do move on". The remaining test's CPU was 0.015625s below 0.100s; wall was 1.730184s above 1s. Continue under that exception while preserving the automated exit=2 evidence. No timing limit or exclusion change is requested.

Review Step 5 only. Steps 6 and 7 remain separate. Do not start or contact a requestor session. Review role isolation remains in force.

Writer response:

This is the first review round for Step 5. No earlier reviewer feedback exists for this step and no repair was reversed.

The user explicitly accepted continuing after the one remaining wall-only lifecycle failure because its actual CPU measurement is below budget. The automated exit=2 and measured wall time remain visible. This is a user decision, not a claim that the unchanged automated validation passed.

### Reviewer focus for step 5 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-1 -->

## Round 1 by reviewer - Step 5

- Recorded: 2026-11-10T09:52:10+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: d25285c5081a72593a918582f878499077327fea

Assessed index tree: d25285c5081a72593a918582f878499077327fea

### Implementation check for step 5 shared_lifecycle_gate (exchange 1) (round 1)

Result:

No. Step 5 has NOT been fully implemented.

Every pytest stage and both collection probes now go through the shared
builder, and the binding refusal comes before any child, detached launch or
saved-proof decision. One failure path is in the wrong order. When
preparation fails in a direct `ghog full`, it runs after the run has already
deleted the testmon map or the group coverage data. Preparation failure is a
new pre-spawn stop that this step added. It should leave project state alone,
as the binding refusal does. The unresolved findings list this with two
smaller code items and a transcript lint failure.

What is in place and matches the plan and the Q05=E1 decision:

- `tools/groundhog/pytest_environment.py` (75 lines) is the only adapter.
  `validate_binding` compares whole resolved paths through `os.path.normcase`,
  never by prefix. A nested project and a `_sibling` name beside the root
  are both refused. The message names the bound root, the target root and
  the target's `senv.bat`. `child_environment` copies only the builder's
  inputs (the three binding variables, `PYTHONPATH`, `PYTEST_ADDOPTS`,
  `LOCALAPPDATA`). It returns only the keys whose prepared value differs,
  with `None` for a removal. Coverage and worker overrides are added after
  that, exactly as the removed `commands._child_environment` combined them.
- `cli.main` calls `validate_invocation` after the read-only listings and
  before level and scope resolution, the live-run refusal, the detached day
  and every dispatch. It applies only to `day`, `full`, `affected`, `single`
  and `timings`. `check`, `init`, `exclude`, `status` and `groups` keep their
  behavior.
- `commands.run_tests_outcome` checks the binding again before the project
  and executable lookups. `_run_pytest` and `selection._collect` are the only
  two pytest `StreamConfig` constructions, and both take
  `pytest_environment.child_environment`. The third `StreamConfig` in
  `commands.py` is `check.bat`. The detached day starts a new `ghog`, which
  runs the same CLI check.
- `selection.counts` checks the binding before the availability fallback. A
  `PreparationError` (including a wrapped `OSError`) is a `ValueError`, so
  the probe's `except OSError` fallback cannot hide it. `day._whole_chain`
  turns it into exit 5, unjudged. An unavailable probe (spawn `OSError`, or
  exit other than 0 or 5) still returns `None`, and the affected stage
  prepares again before its own spawn.
- `runner.run_streaming` applies removals and values and restores absent,
  empty and populated values in `finally`, before output is consumed.
- `Deps.prepare_pytest` defaults to `pytest_environment.prepare`, which
  resolves this checkout's `tools/pytest_plugins`. The policy bodies are never
  imported: the activation matrix uses policy files that raise on import and
  checks `sys.modules` afterwards.
- `day._whole_chain` folds the affected-step result into one condition. This
  is a pure refactor with identical branches.

Missing work:

- Compute the child activation before `runner.reset_testmon` and
  `group_coverage.prepare(fresh=True)` in `commands._run_pytest`, so that a
  preparation failure leaves the testmon map and group coverage data in place.
  Add a regression test for both.

Architecture: preparation policy stays in the shared builder. The groundhog
adapter only converts it to a spawn delta, and the runner owns the temporary
process environment. Two small smells remain. `tools/groundhog/day.py`
imports `PreparationError` from `tools.pytest_plugin_environment` directly
instead of through the adapter that owns the boundary for every other
groundhog module. And the CLI catches a plain `ValueError` around level and
scope resolution as well as the binding check. These need addressing, as
listed in the third finding.

Performance: binding validation is two path resolutions. The delta is linear
in at most six inputs plus the prepared keys. Preparation runs once per child,
as the plan asks, and the builder keeps Step 4's IO contract. Nothing is
quadratic or sorted. No performance issue needs addressing in the code. The
user's wall-time exception is recorded under validation.

Unit test coverage: the gate's source is `tools`, with tests and
`__init__.py` omitted, and no run in this round measured it. Statically, each
adapter function and branch is exercised: the same-root normalization and
casing, the nested and sibling refusals, the command filter, the default
`prepare`, the `OSError` wrapping, removals, coverage and an explicit worker
count. The CLI, command, selection, runner and day changes each have a
focused test. The `_failure_context` setup branch is covered by
`test_pytest_usage_error_preserves_diagnostic`. No test covers keeping the
testmon map or group coverage data after a preparation failure, because the
code does not keep them yet. No other tools line was found uncovered. The
staged test-support files are outside the gate, and their top-level symbols
are referenced.

Feature integrity: interpreter lookup, coverage isolation, worker caps, scope
and the speed rules are unchanged. Reporting gains the pytest output tail on
every exit-5 run, not only on a startup usage error. That helps, but
`_failure_context`'s docstring does not say so. The ordering finding is the
one way an existing capability is impaired: a configuration error can erase
the dependency map that `ghog affected` relies on.

Validation plan effects:

No reviewer edit. The writer's Step 5 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 5 has been fully implemented.`, which this assessment does not
confirm. The rows follow the template. The recorded line counts (CLI 557,
commands 620, context 140, day 432, runner 433, selection 79, adapter 75)
match the staged files. The feature integrity row says preparation failures
"do not earn or contradict saved proof", which is true. It does not mention
the testmon map or group coverage data that a preparation failure deletes
(first finding).

The document-level line correctly stays `No, it is not implemented`. Its
summary now names Steps 1-5 as checked, with Steps 6-7 not started. The
staged diff touches only the Step 5 section and that summary. Reviewer mode
completed no umbrella row, and the effort has none.

### Pre-repair mandatory checks and coverage for step 5 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `d25285c5081a72593a918582f878499077327fea`, which equals the
request-time tree.

Requestor evidence, not repeated: 257 focused tests passed in 9.9s. A default
`ghog day --whole-suite` (`full=none`) ended at 2026-11-10T09:07:40+01:00 with
exit 2. Its checks passed, and 6120 affected tests ran with one wall-only
lifecycle failure, which the user accepted. The resolved `--full=speed` walk
was not run.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` and `bin\ghog.bat` (guard cleared,
`SWITCHPY_CHOICE=local`), so the staged groundhog ran itself. Each run passed
the log-freshness check:

- `ghog check` ended at 2026-11-10T09:46:31+01:00 with `exit=1` after
  3m 10.6s. Ty, pyright, ruff, radon, vulture, the 650-line big-file check,
  shellcheck and the EOF check all passed. The only failure was the Markdown
  check on the unstaged review transcript:
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md` lines 3998 and
  4005, MD050 (strong style, underscore). No staged file was reported.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-10T09:48:08+01:00 with `exit=0` after 22.6s. Testmon
  selected one test, and it passed, with zero warnings and xfails.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran. The
ordering finding comes from reading the code. The reviewer ran no ad hoc
probe for it.

### Resolved validation set and sources for step 5 shared_lifecycle_gate (exchange 1) (round 1)

The request carries one command: `ghog day --full=speed --whole-suite`, from
the `project` source. That is the built-in default completed with the bound
whole-suite selector, because the repository has no `.review-validation`
declaration.

The requestor owns this set, and it was not run in this round. The requestor
reports a self-hosted `ghog day --whole-suite` on 2026-11-10. Its retained log,
`.reviews/a.shared_lifecycle_gate.step5.tmp.day-one-failure.log`, closes with
`full=none src=default proof=unproven`, so it was the default day and not the
resolved `--full=speed` walk. Project checks passed. Then 6120 affected tests
ran in 3m 08.4s with no behavioral failure, warning or xfail, and the walk
ended at exit 2, ended 2026-11-10T09:07:40+01:00. The single cause was the
lifecycle wall limit of
`tests/unit/test_scenario_storage.py::test_sqlite_close_retains_commit_and_discards_pending_write`:
wall 1.730184s against 1s, CPU 0.015625s against 0.100s. No fresh whole-suite
coverage or duration evidence exists for this round.

The request's literal `Human guidance:` block records the user's decision to
continue when CPU is under budget. The reviewer treats that as accepting this
one wall-only result. It does not turn exit 2 into a pass, and the reviewer
ran neither walk.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 5 shared_lifecycle_gate (exchange 1) (round 1)

No drift. There is no `.review-validation` declaration, and the bound scope is
`whole` (fingerprint `686958cd`). The staged change adds no validation
command to the plan or the validation plan. The resolver inputs therefore give
the same single `project` command, `ghog day --full=speed --whole-suite`.
Neither direction adds or drops a command.

### Repository state around validation for step 5 shared_lifecycle_gate (exchange 1) (round 1)

The validation path set holds the 19 staged paths, the implementation plan
and the root `a.ghog.log` that the reviewer evidence commands write. It was
captured before assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `d25285c5081a72593a918582f878499077327fea`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`, with 166 added
  lines. The exchange appended them, and the requestor's residual commit owns
  them.

### Repair inventory for step 5 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 shared_lifecycle_gate (exchange 1) (round 1)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 19 staged paths and the same three ordered groups as the request
evidence:

1. `perf(tests): reduce scenario setup costs`, 3 paths:
   `tests/memory_filesystem.py`, the code-reviewer instruction test and the
   durations property test.
2. `feat(groundhog): prepare every pytest child`, 15 paths: the new adapter,
   the six changed groundhog modules, the package docstring, the new
   activation test package and the five updated groundhog test modules.
3. `docs(shared_lifecycle_gate): record step 5 validation`, 1 path.

Reviewer judgment on grouping and scope: every staged path belongs to exactly
one group, and the validation record comes last. Group 1's three paths are not
in the Step 5 file list. They only reduce test lifecycle cost: they route more
scenarios through the existing in-memory scratch storage, cache one immutable
instruction read, and reuse the ranked-name generator. That generator keeps
the same `_SECS` value domain, the 1 to 20 entry range, the example count and
the assertions. A separate `perf(tests)` commit ahead of the feature is the
right place for them. No AI attribution trailer is present.

`a.commit` is accurate for the received state. The requested fixes belong in
group 2 and their validation in group 3, so the grouping can stay. The group 2
and group 3 bodies will need a refresh after the rework.

### Findings and boundaries for step 5 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings:

- A preparation failure deletes project state before it stops the run
  (`tools/groundhog/commands.py` lines 247, 260 and 266). `_run_pytest` calls
  `runner.reset_testmon(invocation.root)` for a sequential, ungrouped full
  run (line 247). For a grouped full, it calls
  `group_coverage.prepare(..., fresh=True)`, which unlinks the group coverage
  data file (line 260). Only then does it call
  `pytest_environment.child_environment` (line 266). That call can now raise
  `PreparationError` for an unknown `LLM_SHARED_PYTEST_PLUGINS` token, a
  missing or contract-invalid policy source, a corrupt loader cache entry, or
  a publication `OSError`. `run_tests_outcome` then reports exit 5 with no
  spawn, but the `.testmondata` dependency map or the group coverage data is
  already gone. Two routes reach this: a direct `ghog full`, and a day walk
  that upgrades saved proof, whose full step is its first preparation. After
  the shell is fixed, the next `ghog affected` has no dependency map and
  selects everything again. Before this step, nothing between the reset and the
  spawn could fail except the spawn itself. `test_selected_preparation_failure_stops_before_spawn`
  covers `full` with an invalid selection, but its project has no
  `.testmondata`, so it cannot see the deletion. The plan asks for
  preparation failure "before spawn" with the existing setup contract, and
  the Q05=E1 tests require unchanged state for the binding variant. A
  preparation failure should leave the same state untouched.
- `_failure_context`'s docstring no longer describes what it returns
  (`tools/groundhog/commands.py` lines 468 to 490). The new branch at line 486
  returns `result.tail` for every exit-5 run. That covers a startup usage
  error, an empty `full` or `single`, a missing coverage TOTAL and unusable
  group coverage evidence, not only the pytest usage error the plan names.
  Showing the tail is reasonable for all of them. The `Returns:` section
  still lists only the crash block, the failure block, the unparsed-failure
  tail and "nothing for a run that did not fail". The project rules ask for
  updated docstrings that explain the fix.
- The preparation error type is caught inconsistently
  (`tools/groundhog/day.py` line 83, `tools/groundhog/cli.py` line 186).
  `day.py` imports `PreparationError` from the shared builder module
  `tools.pytest_plugin_environment`. Every other groundhog module reaches the
  builder only through the `pytest_environment` adapter, and the plan keeps
  binding logic in that adapter. `cli.main` widened its handler from
  `(LevelError, scope.ScopeError)` to also catch a plain `ValueError`. That
  covers `_with_level` and `_with_scope` too, so any unrelated `ValueError`
  raised there now becomes a one-line setup error instead of a traceback.
  Both work today, but the boundary is looser than it needs to be.
- `ghog check` fails on the review transcript
  (`docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`, lines 3998
  and 4005, MD050). This round's request lists
  `tests/unit/tools/shared_lifecycle/test_groundhog_activation/__init__.py`
  and `tools/groundhog/__init__.py` without code spans in its change summary,
  so their double underscores parse as strong emphasis. This is the same
  defect as Step 3 and Step 4 round 1. The staged files pass. The transcript is
  unstaged and requestor-owned, but the next review-record commit would carry
  the lint failure.

Boundary-crossing work: None.

### Human guidance response for step 5 shared_lifecycle_gate (exchange 1) (round 1)

Human guidance:

Human guidance for this review: "OK, when you have CPU under budget, do move on". The remaining test's CPU was 0.015625s below 0.100s; wall was 1.730184s above 1s. Continue under that exception while preserving the automated exit=2 evidence. No timing limit or exclusion change is requested.

Review Step 5 only. Steps 6 and 7 remain separate. Do not start or contact a requestor session. Review role isolation remains in force.

Guidance response:

The guidance asks for no repair, so the reviewer edited nothing and reports
findings only.

- CPU exception: accepted as the user's decision for the one wall-only result
  of `test_sqlite_close_retains_commit_and_discards_pending_write`. The
  automated exit 2 stays recorded as exit 2. No limit, exclusion or baseline
  was changed, and this round's findings do not rely on that timing result.
  The resolved `--full=speed` walk was never run, so this round has no
  whole-suite coverage or duration evidence. The rework needs that walk, or a
  user decision that covers its absence too.
- Step boundary: only Step 5 was assessed. Steps 6 and 7 stay separate. No
  finding asks for the compatibility preflight, acceptance harness or
  documentation work.
- Role isolation: the reviewer was started independently, by the human
  through `review-resume`. It did not start or contact a requestor session.
  Publishing this answer is its only handoff.

### Writer instructions for step 5 shared_lifecycle_gate (exchange 1) (round 1)

1. Preparation before state changes: in `commands._run_pytest`, compute the
   child activation before `runner.reset_testmon` and before
   `group_coverage.prepare`. For example, call
   `pytest_environment.child_environment(invocation, deps, parallel=parallel)`
   first. Then run the reset and coverage preparation, and add
   `group_coverage.environment(measure[0])` to that delta. Keep one call to the
   builder per spawn. Add regression tests with an invalid
   `LLM_SHARED_PYTEST_PLUGINS` (or a raising `prepare_pytest`). A sequential
   ungrouped `full` must keep an existing `.testmondata`, and a grouped `full`
   must keep an existing group coverage data file. Both must exit 5 with no
   spawn.
2. Docstring: update `_failure_context`'s description and `Returns:` section
   for the exit-5 output tail. Either say it covers every setup error, or
   narrow the branch to `result.pytest_exit == PYTEST_USAGE_ERROR` if only
   startup usage errors should show it.
3. Error boundary: have `day.py` take the preparation error type from the
   `tools.groundhog.pytest_environment` adapter, for example through a
   re-export, instead of importing `tools.pytest_plugin_environment`. In
   `cli.main`, catch that error type instead of a plain `ValueError`, so
   `_with_level` and `_with_scope` keep their previous error surface.
4. Transcript: before the review-record commit, put the two `__init__.py`
   paths at lines 3998 and 4005 of
   `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md` in code spans,
   so `ghog check` passes MD050. Write every path in later change summaries as
   a code span, as Step 4's review already asked. This round's request repeated
   the Step 4 defect.
5. Validation: update the Step 5 rows (implemented, architecture, coverage,
   feature integrity) and the group 2 and group 3 `a.commit` bodies. Rerun the
   focused tests. Run the resolved `ghog day --full=speed --whole-suite`, or
   record the user's explicit decision if it cannot run green, because this
   round has no whole-suite coverage or duration evidence.

Non-blocking note: `_FLOOR_VALUES` in `test_groundhog_durations_pbt.py` now
feeds two properties, so a neutral name such as `_RANKED_VALUES` would read
better. Its domain is correct.

### Decision rationale for step 5 shared_lifecycle_gate (exchange 1) (round 1)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 5,
  round 1, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `d25285c5` all agree with the live exchange and index.
- Completeness: fail. Every Step 5 file and test obligation is present. But a
  preparation failure in `_run_pytest` runs after the testmon reset and the
  group coverage reset, so it destroys state before stopping.
- Validation and coverage: fail. Reviewer `ghog check` exited 1 on the
  transcript's MD050 lint at lines 3998 and 4005; every staged file passed.
  `ghog affected --no-cov` exited 0 with one selected test passing. The
  resolved `--full=speed` walk was not run. Static reading finds no uncovered
  tools line, but no test covers state preservation after a preparation
  failure.
- Staged attribution: pass. All 19 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: fail. Four findings are unresolved: the reset ordering, the stale
  docstring, the error boundary and the transcript lint failure.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping is accurate for the received state.

This round made no repair, substantive or polishing. The literal
`Human guidance:` block accepts one wall-only timing result and asks for no
repair, so the reviewer reports findings only.

Disposition: changes requested.

### Final reviewer decision for step 5 shared_lifecycle_gate (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-1 -->

## Round 2 by requestor - Step 5

- Recorded: 2026-11-10T10:19:41+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 5
- Outcome: request

### Review identity for step 5 shared_lifecycle_gate (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 5
Review round: 2

### Code review evidence for step 5 shared_lifecycle_gate (round 2)

request_index_tree: 4dc7818bb0995c229c6d9796c2c3e198f93430c1
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "none", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): reduce scenario setup costs
group 1 path: tests/memory_filesystem.py
group 1 path: tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
group 1 path: tests/unit/tools/test_groundhog_durations_pbt.py
group 2: feat(groundhog): prepare every pytest child
group 2 path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/__init__.py
group 2 path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/test_groundhog_activation_tdd.py
group 2 path: tests/unit/tools/test_groundhog_acceptance_day.py
group 2 path: tests/unit/tools/test_groundhog_cli.py
group 2 path: tests/unit/tools/test_groundhog_commands.py
group 2 path: tests/unit/tools/test_groundhog_runner.py
group 2 path: tests/unit/tools/test_groundhog_selection.py
group 2 path: tools/groundhog/__init__.py
group 2 path: tools/groundhog/cli.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/day.py
group 2 path: tools/groundhog/pytest_environment.py
group 2 path: tools/groundhog/runner.py
group 2 path: tools/groundhog/selection.py
group 3: docs(shared_lifecycle_gate): record step 5 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/__init__.py
staged path: tests/unit/tools/shared_lifecycle/test_groundhog_activation/test_groundhog_activation_tdd.py
staged path: tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
staged path: tests/unit/tools/test_groundhog_acceptance_day.py
staged path: tests/unit/tools/test_groundhog_cli.py
staged path: tests/unit/tools/test_groundhog_commands.py
staged path: tests/unit/tools/test_groundhog_durations_pbt.py
staged path: tests/unit/tools/test_groundhog_runner.py
staged path: tests/unit/tools/test_groundhog_selection.py
staged path: tools/groundhog/__init__.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/groundhog/pytest_environment.py
staged path: tools/groundhog/runner.py
staged path: tools/groundhog/selection.py
```

### Validation scope for step 5 shared_lifecycle_gate (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 5 shared_lifecycle_gate (round 2)

Step 5 is fully implemented, including every accepted round 1 correction. Preparation covers all pytest stages and both collection probes. Whole normalized project-root validation precedes invocation work, detached dispatch and saved-proof decisions. Child environment additions and removals restore the parent's exact state on success and failure.

Preparation now precedes destructive dependency-map and fresh group-coverage resets. The builder runs once per child; group coverage overrides are composed after successful preparation. Two regression cases preserve existing evidence bytes and assert no spawn for invalid activation. The 291-test focus passed both regressions and every behavioral assertion. Its single lifecycle error measured CPU 0.093750s below the 0.100s ceiling and wall 1.785271s above 1s; its automated exit remains 2 under the user's explicit continuation decision.

CLI and day handle the adapter's exact preparation error. Setup-error output tails and their documentation agree. The duration strategy retains its domain, examples and assertions under the neutral name `_RANKED_VALUES`. No exclusions, baselines or timing limits changed.

Architecture: environment construction remains in one adapter, process-state restoration in the runner, and shared activation policy in the existing builder. Consumer interpreter lookup, worker caps, selection, coverage composition, collection fallback and proof judgments retain their contracts. Physical counts: CLI 557, commands 623, context 140, day 432, runner 433, selection 79, adapter 76, activation tests 279; all below 650. No new runtime class or domain type was introduced. Steps 6 and 7 remain separate.

The configured coverage source is `tools`, omitting tests and package markers. The focused run used no coverage. No coverage percentage or green speed proof is inferred from that evidence. The mandatory resolved validation set remains unchanged.

The required self-hosted `ghog day --full=speed --whole-suite` finished at 10:14:45+01:00 on 2026-11-10. All project checks and 433 affected tests passed. The covered full run measured 6122 tests, with zero assertion failures, warnings or expected failures and six wall-only lifecycle errors. Their CPU/wall seconds were 0.031250/1.554686, 0.046875/1.452407, 0.046875/9.382368, 0.062500/5.650682, 0.062500/1.483572 and 0.078125/1.670344. Every failing lifecycle's CPU is below 0.100s. The user's standing instruction permits moving on; automated exit 2, proof none and withheld coverage/outlier verdicts are retained. The full measurement does not establish 100% coverage or speed proof. No unchanged repair run or exclusion was made. The validation plan records each case and the evidence is retained privately.

### Implementation report for step 5 shared_lifecycle_gate (round 2)

Groundhog prepares every pytest child through the current checkout's shared builder and rejects a foreign inherited project binding before dispatch, detached spawning or saved-proof decisions. Each stage checks again. Both collection probes receive preparation and preserve setup errors instead of converting them to unavailable-evidence fallback.

The runner applies environment additions and removals only for process creation and restores exact prior key presence and values immediately afterward, including a raising factory. Consumer interpreter selection, coverage isolation, bounded workers and scope remain intact.

Round 1 identified that full-run preparation occurred after dependency-map or group-coverage data deletion. The writer moved preparation before both state changes, retained one builder call per spawn, and composed group coverage overrides afterward. Regression cases seed both evidence files and verify unchanged bytes, setup exit 5 and zero spawns for whole-suite and grouped full runs. Both passed in the 291-test focus. All other behavioral assertions passed; its sole lifecycle failure was wall-only, with CPU 0.093750s below 0.100s and wall 1.785271s above 1s, automated exit 2 retained.

The writer also corrected the setup-tail docstring, exposed the preparation error through the adapter, narrowed CLI handling from generic ValueError, and made day use the same boundary. The regression parameter is keyword-only under the project's lint policy. The transcript lint defects are repaired, and every path in the replacement change summary is a code span.

Earlier profiling repairs use established memory storage for selected test scenarios, a lazy immutable instruction read and an integer-ranked duration strategy with its original domain and examples. No behavior assertions, timing limits, exclusions or baselines were weakened. The earlier SQLite test's CPU was 0.015625s and wall 1.730184s. The user explicitly instructed moving on when CPU is under budget; automated exits and proof limitations remain visible.

The validation plan and root commit-plan bodies describe the corrected behavior and focused evidence. No reviewer edit is reversed. No later implementation step is included.

Replacement validation ran the resolved `ghog day --full=speed --whole-suite` through the implementing checkout. Project checks and 433 affected tests passed. Its 6122-test full stage had six wall-only lifecycle errors, each CPU between 0.031250s and 0.078125s below the 0.100s ceiling. There were zero assertion failures, warnings or expected failures. The final verdict at 10:14:45+01:00 was exit 2, proof none, coverage and outlier verdicts withheld. The user instruction permits moving on for these cases; this is not a green speed or 100% coverage claim. The validation plan records CPU and wall values for all six cases. No unchanged repair run, exclusion or timing change followed.

Writer notes: `.reviews/a.shared_lifecycle_gate.step5.journal.md` and `.reviews/a.shared_lifecycle_gate.step5.handoff.md`.

### Change summary for step 5 shared_lifecycle_gate (round 2)

The same three dependency-ordered root commit-plan groups cover all 19 staged paths. Group boundaries, membership and subjects remain accurate; bodies now describe the accepted round 1 corrections.

Group 1, `perf(tests): reduce scenario setup costs`:

- `tests/memory_filesystem.py`
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`
- `tests/unit/tools/test_groundhog_durations_pbt.py`

Group 2, `feat(groundhog): prepare every pytest child`:

- `tests/unit/tools/shared_lifecycle/test_groundhog_activation/__init__.py`
- `tests/unit/tools/shared_lifecycle/test_groundhog_activation/test_groundhog_activation_tdd.py`
- `tests/unit/tools/test_groundhog_acceptance_day.py`
- `tests/unit/tools/test_groundhog_cli.py`
- `tests/unit/tools/test_groundhog_commands.py`
- `tests/unit/tools/test_groundhog_runner.py`
- `tests/unit/tools/test_groundhog_selection.py`
- `tools/groundhog/__init__.py`
- `tools/groundhog/cli.py`
- `tools/groundhog/commands.py`
- `tools/groundhog/context.py`
- `tools/groundhog/day.py`
- `tools/groundhog/pytest_environment.py`
- `tools/groundhog/runner.py`
- `tools/groundhog/selection.py`

Group 3, `docs(shared_lifecycle_gate): record step 5 validation`:

- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`

The workflow-owned review transcript remains unstaged for its residual documentation commit after human authorization. No source or test changes belong to Steps 6 or 7.

### Human guidance and writer response for step 5 shared_lifecycle_gate (round 2)

Human guidance:

The user explicitly authorized moving on when CPU is under budget. Keep wall-only failures and their automated exits visible, and distinguish that authorization from a green gate. The earlier SQLite failure measured CPU 0.015625s and wall 1.730184s. After the round 1 fixes, the 291-test focus measured CPU 0.093750s and wall 1.785271s for its sole lifecycle overrun; both new preservation regressions passed. No limit, assertion, input domain, example count, exclusion or baseline was weakened. This guidance authorizes continuation through review, not a commit.

The required replacement full-speed day finished at 10:14:45+01:00. Checks and 433 affected tests passed; its 6122-test full stage reported six wall-only lifecycle errors with CPU 0.031250s to 0.078125s, all below 0.100s. It reported zero assertion failures, warnings or expected failures. The same standing instruction authorizes continuation. Retain automated exit 2, proof none and withheld coverage/outlier verdicts. No unchanged repair run was made.

Writer response:

All round 1 findings are accepted; no disagreement or reversal.

Preparation now completes before the sequential full dependency-map reset or fresh group-coverage preparation. The prepared environment delta is computed once per spawn, then group coverage overrides are composed after successful preparation. Two regression cases seed existing dependency and coverage bytes, select invalid activation and verify setup exit 5, no spawn and unchanged bytes for whole-suite and grouped full runs. Both cases passed in the 291-test focus.

The setup-diagnostic docstring now describes every setup-error output tail. Day and CLI use the preparation error exposed by the groundhog adapter, and the CLI no longer catches unrelated ValueError exceptions. The reusable duration strategy has the neutral name `_RANKED_VALUES`. The transcript lint defects were corrected and the updated transcript passes Markdown lint. Later change summaries put every path in code spans.

The validation plan and commit-plan bodies now record evidence preservation, exact error handling and the new focused evidence. The user explicitly instructed: "OK, when you have CPU under budget, do move on". The 291-test run has no failing behavioral assertion and one wall-only lifecycle error: CPU 0.093750s below 0.100s, wall 1.785271s above 1s, automated exit 2. That instruction permits continuation while retaining the automated verdict, limits and exclusions. No rerun seeks a favorable measurement.

The required replacement `ghog day --full=speed --whole-suite` ran after the fixes. Checks and 433 affected tests passed; the covered full stage measured 6122 tests and stopped with six wall-only lifecycle errors. Each CPU was under 0.100s (range 0.031250s to 0.078125s). Zero assertion failures, warnings or expected failures were reported. The validation plan now records all six CPU/wall values. The final automated result remains exit 2, proof none and withheld coverage/outlier verdicts. Under the same user instruction, the writer proceeds to review without an unchanged repair run or weakening any gate. This addresses the request to run the declared command and record the user's explicit decision when it cannot run green.

### Reviewer focus for step 5 shared_lifecycle_gate (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-2 -->

## Round 2 by reviewer - Step 5

- Recorded: 2026-11-10T10:36:56+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 shared_lifecycle_gate (exchange 1) (round 2)

Baseline index tree: 4dc7818bb0995c229c6d9796c2c3e198f93430c1

Assessed index tree: 4dc7818bb0995c229c6d9796c2c3e198f93430c1

### Implementation check for step 5 shared_lifecycle_gate (exchange 1) (round 2)

Result:

Yes. Step 5 has been fully implemented.

All four round 1 findings are fixed, and the round 2 delta changes nothing
else in behavior. Every pytest stage and both collection probes use the shared
builder through one adapter. A foreign binding is refused before any child,
detached day or saved-proof decision. A preparation failure now stops before
any project state is touched.

Round 1 findings, rechecked against the delta from tree `d25285c5` to
`4dc7818b`:

- Reset ordering: fixed. `commands._run_pytest` now computes
  `child_environment` (line 243) before `runner.reset_testmon` and
  `group_coverage.prepare`. After a successful preparation it adds the group
  coverage override to the same delta (line 263). The builder still runs once
  per spawn. `test_full_preparation_failure_preserves_existing_evidence`
  seeds `.testmondata` and the group coverage data file, uses an invalid
  `LLM_SHARED_PYTEST_PLUGINS`, and asserts exit 5, zero spawns and unchanged
  bytes for an ungrouped and a grouped `full`. Both cases would fail against
  the round 1 ordering. The grouped acceptance suites' `CoverageSpawns` only
  writes evidence when the child sees `COVERAGE_FILE`, so they still cover the
  composed override on a successful grouped run.
- Docstring: fixed. `_failure_context`'s summary and `Returns:` section now
  name the output tail for every setup error.
- Error boundary: fixed. `pytest_environment` re-exports `PreparationError`
  and raises it itself. `day.py` catches `pytest_environment.PreparationError`
  and no longer imports `tools.pytest_plugin_environment`. `cli.main` catches
  `(LevelError, scope.ScopeError, pytest_environment.PreparationError)`, so a
  plain `ValueError` from `_with_level` or `_with_scope` keeps its previous
  surface.
- Transcript lint: fixed. Every path in the round 2 change summary is a code
  span. Reviewer `ghog check` result is recorded under validation.

The rest of the Step 5 implementation is unchanged from round 1 and still
matches the plan and Q05=E1. Whole normalized root comparison
(case-insensitive on Windows, nested and sibling roots refused), the CLI check
before every pytest-capable dispatch, the per-stage and per-probe recheck,
probe setup errors that never fall back, removals with exact restoration in
the runner, and the default `prepare` that resolves this checkout's sources
without importing policy bodies.

Architecture: activation policy stays in the shared builder. The groundhog
adapter owns the binding check, the spawn delta and now the error type used by
CLI and day, and the runner owns process-environment application. No layer
imports past the adapter any more. No DDD-Hexagonal violation or smell needs
addressing.

Performance: unchanged from round 1. Two path resolutions per check, a delta
linear in at most six inputs, and one preparation per child. Moving the call
earlier adds no work. No performance issue needs addressing.

Unit test coverage: the gate's source is `tools`, with tests and
`__init__.py` omitted. This round's speed walk instrumented coverage but
withheld the verdict after its wall-only lifecycle errors, so no percentage
is measured. Statically, each changed line has a covering test. The early
`child_environment` call and both reset branches are covered by the new
regression and the existing full-run tests. The coverage override `update`
is covered by the grouped acceptance suites, the narrowed CLI handler by
`test_foreign_binding_blocks_dispatch`, and the day handler by
`test_probe_preparation_failure_reports_setup`. The re-export is exercised by
every binding refusal. No unit-test coverage gap was found. The staged
test-support files are outside the gate, and their top-level symbols are
referenced.

Feature integrity: interpreter lookup, coverage isolation, worker caps, scope,
collection fallback and the speed rules are unchanged. A preparation failure
now preserves the dependency map and group coverage data, so `ghog affected`
keeps its selection after a configuration error. No existing feature or
reporting capability is impaired.

Validation plan effects:

No reviewer edit. The writer's Step 5 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 5 has been fully implemented.`, which this assessment confirms. The
round 2 changes are accurate. The implemented row records the earlier
preparation and the adapter's error type. The size row records commands 623
and adapter 76, matching the staged files. The performance row lists all six
wall-only cases with their CPU and wall values, and they match the retained
walk log. The coverage row now says that 100% coverage has not been
established for this step. The feature integrity row states the evidence
preservation.

The document-level line correctly stays `No, it is not implemented`, with
Steps 6-7 not started. The staged diff touches only the Step 5 section and
that summary. Reviewer mode completed no umbrella row, and the effort has
none.

### Pre-repair mandatory checks and coverage for step 5 shared_lifecycle_gate (exchange 1) (round 2)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `4dc7818bb0995c229c6d9796c2c3e198f93430c1`, which equals the
request-time tree.

Requestor evidence, not repeated: a 291-test focus passed every behavioral
assertion, including both evidence-preservation regressions. It had one
wall-only lifecycle overrun (CPU 0.093750s, wall 1.785271s, exit 2). The
resolved `ghog day --full=speed --whole-suite` ended at
2026-11-10T10:14:45+01:00 with exit 2 on six wall-only lifecycle errors, as
described under the resolved validation set.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` and `bin\ghog.bat` (guard cleared,
`SWITCHPY_CHOICE=local`), so the staged groundhog ran itself. Each run passed
the log-freshness check:

- `ghog check` ended at 2026-11-10T10:33:42+01:00 with `exit=0` after
  4m 25.0s. Every step passed: ty, pyright, ruff, radon, vulture, the
  650-line big-file check, Markdown (including the review transcript, so the
  round 1 MD050 defect is gone), shellcheck and the EOF check.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-10T10:34:58+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's walk, so 0 tests ran.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran.

### Resolved validation set and sources for step 5 shared_lifecycle_gate (exchange 1) (round 2)

The request carries one command: `ghog day --full=speed --whole-suite`, from
the `project` source. That is the built-in default completed with the bound
whole-suite selector, because the repository has no `.review-validation`
declaration.

The requestor owns this set and ran it after the round 1 fixes, through the
implementing checkout. The retained log
`.reviews/a.shared_lifecycle_gate.step5.tmp.r2.day-wall-only.log` closes with
`ghog day done fail=6 ... cov=withheld outliers=withheld excluded=withheld exit=2 full=speed src=param proof=none`
at 2026-11-10T10:14:45+01:00. The reviewer read that log:

- `ghog check` passed every step, including the Markdown check.
- The probes counted 433 affected out of 6122. The affected step ran and passed
  with zero failures, warnings and xfails.
- The full step measured 6122 tests. All six `fail` entries are teardown
  lifecycle errors, and none is an assertion failure. Each is wall-only: CPU
  0.031250s to 0.078125s against the 0.100s ceiling, wall 1.452407s to
  9.382368s against 1s. They are in the recovery and specification reviewer
  acceptance tests, outside the Step 5 code.

The literal `Human guidance:` block records the user's decision to move on
when CPU is under budget. The reviewer accepts these six results under it. The
automated outcome stays exit 2 with `proof=none`, and the coverage and outlier
verdicts stay withheld. This is not a green speed proof or a 100% coverage
measurement. The reviewer ran neither walk.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 5 shared_lifecycle_gate (exchange 1) (round 2)

No drift. There is no `.review-validation` declaration, and the bound scope is
`whole` (fingerprint `686958cd`). The round 2 delta adds no validation command
to the plan or the validation plan. The resolver inputs therefore give the same
single `project` command, `ghog day --full=speed --whole-suite`. Neither
direction adds or drops a command.

### Repository state around validation for step 5 shared_lifecycle_gate (exchange 1) (round 2)

The validation path set holds the 19 staged paths, the implementation plan
and the root `a.ghog.log` that the reviewer evidence commands write. It was
captured before assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `4dc7818bb0995c229c6d9796c2c3e198f93430c1`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it. It passes the
  Markdown check.

### Repair inventory for step 5 shared_lifecycle_gate (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 shared_lifecycle_gate (exchange 1) (round 2)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 19 staged paths and the same three ordered groups as the request
evidence:

1. `perf(tests): reduce scenario setup costs`, 3 paths.
2. `feat(groundhog): prepare every pytest child`, 15 paths.
3. `docs(shared_lifecycle_gate): record step 5 validation`, 1 path.

Reviewer judgment on grouping and scope: membership and order are unchanged
from round 1 and remain correct. The round 2 source and test fixes are in
group 2, the `_RANKED_VALUES` rename is in group 1, and the validation rows are
in group 3. The group 2 body now lists preparation before the resets and the
adapter's exact error type. The group 3 body records the evidence-preservation
regressions, the 291-test focus and the speed walk's six wall-only errors with
withheld proof. No AI attribution trailer is present.

`a.commit` is accurate for the received state.

### Findings and boundaries for step 5 shared_lifecycle_gate (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 5 shared_lifecycle_gate (exchange 1) (round 2)

Human guidance:

The user explicitly authorized moving on when CPU is under budget. Keep wall-only failures and their automated exits visible, and distinguish that authorization from a green gate. The earlier SQLite failure measured CPU 0.015625s and wall 1.730184s. After the round 1 fixes, the 291-test focus measured CPU 0.093750s and wall 1.785271s for its sole lifecycle overrun; both new preservation regressions passed. No limit, assertion, input domain, example count, exclusion or baseline was weakened. This guidance authorizes continuation through review, not a commit.

The required replacement full-speed day finished at 10:14:45+01:00. Checks and 433 affected tests passed; its 6122-test full stage reported six wall-only lifecycle errors with CPU 0.031250s to 0.078125s, all below 0.100s. It reported zero assertion failures, warnings or expected failures. The same standing instruction authorizes continuation. Retain automated exit 2, proof none and withheld coverage/outlier verdicts. No unchanged repair run was made.

Guidance response:

The guidance asks for no repair, so the reviewer edited nothing and reports
its assessment only.

- CPU exception: the reviewer checked the retained speed-walk log. All six
  `fail` entries are teardown lifecycle errors whose CPU (0.031250s to
  0.078125s) is under the 0.100s ceiling, and there is no assertion failure,
  warning or xfail. The focused run's single overrun (CPU 0.093750s) is also
  under it. These results are accepted under the user's decision. They are
  recorded as exit 2 with `proof=none` and withheld coverage and outlier
  verdicts, not as a green gate. No limit, exclusion or baseline changed.
- Readiness: with that decision, the reviewer judged validation on its own
  green focused evidence and a static coverage reading. A commit-ready
  recommendation here does not claim 100% measured coverage or speed proof.
- Authority: the guidance authorizes continuation through review, not a
  commit, and this answer authorizes none. The reviewer stayed within Step 5
  and did not start or contact a requestor session.

### Writer instructions for step 5 shared_lifecycle_gate (exchange 1) (round 2)

No further implementation work is requested for Step 5.

Non-blocking note:

- `pytest_environment.child_environment` still accepts the optional `measure`
  argument and adds the group coverage override from it. No production caller
  passes it any more: `commands._run_pytest` now adds that override itself
  after `group_coverage.prepare`, and `selection._collect` never passed it.
  Only `test_coverage_and_explicit_worker_settings_survive_preparation` uses
  that branch. The behavior is correct. Removing the parameter, or using it in
  `_run_pytest`, would leave one place that composes the coverage override.

### Decision rationale for step 5 shared_lifecycle_gate (exchange 1) (round 2)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 5,
  round 2, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `4dc7818b` all agree with the live exchange and index.
- Completeness: pass. Every Step 5 obligation is implemented, and all four
  round 1 findings are fixed. A preparation failure now leaves the dependency
  map and group coverage data untouched, and a regression test proves it for
  both full-run shapes.
- Validation and coverage: pass under the human guidance. Reviewer
  `ghog check` and `ghog affected --no-cov` both exited 0. Static reading
  finds no coverage gap. The requestor's resolved speed walk ended at exit 2
  only on six wall-only lifecycle errors with CPU under its ceiling, which the
  user explicitly accepted. Its coverage and outlier verdicts were withheld,
  so this is not a measured 100% or a speed proof.
- Staged attribution: pass. All 19 staged paths are writer work in three
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: pass. No current or carried finding is unresolved. The one
  remaining note is non-blocking.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping and bodies are accurate.

This round made no repair, substantive or polishing. The literal
`Human guidance:` block accepts wall-only results with CPU under budget and
asks for no repair.

Disposition: commit-ready. This is an advisory recommendation and does not
authorize a commit.

### Final reviewer decision for step 5 shared_lifecycle_gate (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-5-round-2 -->

## Round 2 by human - Step 5 - human-confirmation

- Recorded: 2026-11-10T10:54:10+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 5
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 6

- Recorded: 2026-11-10T15:07:52+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 6
- Outcome: request

### Review identity for step 6 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 6
Review round: 1

### Code review evidence for step 6 shared_lifecycle_gate (round 1)

request_index_tree: 7abb61174664aeaead9a3157c486fa9242b62a64
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(lifecycle): validate real Python compatibility
group 1 path: bin/lifecycle_compatibility.bat
group 1 path: check.bat
group 1 path: tools/lifecycle_compatibility/behavior_runner.py
group 1 path: tools/lifecycle_compatibility/behavior_scenarios.py
group 1 path: tools/lifecycle_compatibility/environment.py
group 1 path: tools/lifecycle_compatibility/requirements-py312.txt
group 1 path: tools/lifecycle_compatibility/runner.py
group 1 path: tools/lifecycle_compatibility/static_entry.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_environment_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_static_entry_tdd.py
group 2: feat(ghog): require fresh compatibility evidence
group 2 path: pyproject.toml
group 2 path: tools/groundhog/cli.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/compatibility_preflight.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/day.py
group 2 path: tests/memory_filesystem.py
group 2 path: tests/unit/tools/test_compatibility_preflight/__init__.py
group 2 path: tests/unit/tools/test_compatibility_preflight/test_compatibility_preflight_tdd.py
group 3: perf(tests): trim fixture ownership preparation
group 3 path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
group 4: docs(shared_lifecycle_gate): record step 6 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: bin/lifecycle_compatibility.bat
staged path: check.bat
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: pyproject.toml
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_environment_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_static_entry_tdd.py
staged path: tests/unit/tools/test_compatibility_preflight/__init__.py
staged path: tests/unit/tools/test_compatibility_preflight/test_compatibility_preflight_tdd.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/compatibility_preflight.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/lifecycle_compatibility/behavior_runner.py
staged path: tools/lifecycle_compatibility/behavior_scenarios.py
staged path: tools/lifecycle_compatibility/environment.py
staged path: tools/lifecycle_compatibility/requirements-py312.txt
staged path: tools/lifecycle_compatibility/runner.py
staged path: tools/lifecycle_compatibility/static_entry.py
```

### Validation scope for step 6 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 6 shared_lifecycle_gate (round 1)

Step 6 is fully implemented. The validation plan records the exact Yes verdict.
Inspection against the plan found no architecture, performance, coverage or
feature-integrity gap. The adapters retain the existing injected process seam;
standalone policies acquire no imports from the main Python 3.13 runtime.

Fresh `ghog day --full=speed --whole-suite` completed at
2026-11-10T14:57:11+01:00, exit 0: 6202 tests, fail=0, warn=0, xfail=0,
cov=100, outliers=0, excluded=0. Compatibility preflight, static checks and
affected tests passed before the covered full run. Status confirmed done and
the log was newer than its freshness marker. No exclusion was accepted.

Windows executable matrices passed 16/16 scenarios each on real Python 3.12.15
and 3.13.9, both using pytest 9.1.0 and xdist 3.8.0. Static checks include a real
Ruff Python 3.10 grammar negative control for PEP 701 and an AST prefix check.
Markdown lint and spelling passed for the changed validation plan. The root
`a.commit` is formatted and the readiness checker returned ready=true.

### Implementation report for step 6 shared_lifecycle_gate (round 1)

The independent compatibility launcher provisions only on explicit `--setup`.
Ordinary validation checks actual executable version and exact checkout pins,
then runs isolated real-policy cases and bounded xdist worker barriers. The
optional-absent case uses a site-free child containing only mandatory packages.
Failure diagnostics remain visible before automatic temporary cleanup.

Tracked literal applicability selects the target checkout's fixed entrypoint.
Malformed declarations fail before detach; inherited foreign bindings fail
before the harness. Every day invocation preflights before proof reuse;
direct full preflights once, while day-derived full avoids duplication.
Undeclared consumers gain no compatibility environment prerequisite.

Process-free tests cover the transport boundaries and actual orchestration,
including every day level, saved proof, forced and upgraded walks, direct full,
invalid declarations and missing prerequisites. The new preflight tests use
the existing virtual filesystem. A profiled fixture-ownership matrix now uses
explicit configuration and collected declarations, preserving every scope,
permission, finalizer and cleanup assertion while removing redundant discovery.

All changed production Python files remain below 650 lines. Existing directory
targets cover new Python 3.12 harness files. Launcher selector inspection keeps
the main Python 3.13 runtime selected. Step 7 acceptance and adoption documents
remain pending.

Writer notes: `.reviews/a.shared_lifecycle_gate.step6.journal.md` and
`.reviews/a.shared_lifecycle_gate.step6.handoff.md`.

### Change summary for step 6 shared_lifecycle_gate (round 1)

The root `a.commit` covers every staged path in four dependency-ordered groups.

1. `feat(lifecycle): validate real Python compatibility`: the batch launcher,
   `check.bat`, new behavior/environment/static modules, independent manifest,
   extended runner and four compatibility test files.
2. `feat(ghog): require fresh compatibility evidence`: tracked applicability,
   groundhog CLI/commands/context/day, new preflight adapter, virtual filesystem
   routing and the new preflight test package.
3. `perf(tests): trim fixture ownership preparation`: the existing ownership
   scope/permission matrix retains all assertions with less pytest preparation.
4. `docs(shared_lifecycle_gate): record step 6 validation`: the validation plan.

Staged paths:

- `bin/lifecycle_compatibility.bat`
- `check.bat`
- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`
- `pyproject.toml`
- `tests/memory_filesystem.py`
- `tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_environment_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_static_entry_tdd.py`
- `tests/unit/tools/test_compatibility_preflight/__init__.py`
- `tests/unit/tools/test_compatibility_preflight/test_compatibility_preflight_tdd.py`
- `tools/groundhog/cli.py`
- `tools/groundhog/commands.py`
- `tools/groundhog/compatibility_preflight.py`
- `tools/groundhog/context.py`
- `tools/groundhog/day.py`
- `tools/lifecycle_compatibility/behavior_runner.py`
- `tools/lifecycle_compatibility/behavior_scenarios.py`
- `tools/lifecycle_compatibility/environment.py`
- `tools/lifecycle_compatibility/requirements-py312.txt`
- `tools/lifecycle_compatibility/runner.py`
- `tools/lifecycle_compatibility/static_entry.py`

### Writer response for step 6 shared_lifecycle_gate (round 1)

Writer response:

This is the first review round for Step 6. No earlier reviewer feedback or
disagreement applies. The fixture ownership repair responds to an actual CPU
budget failure; the final full-speed walk passed without a timing exception,
limit change or duration exclusion.

### Reviewer focus for step 6 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-1 -->

## Round 1 by reviewer - Step 6

- Recorded: 2026-11-10T15:38:44+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: 7abb61174664aeaead9a3157c486fa9242b62a64

Assessed index tree: 7abb61174664aeaead9a3157c486fa9242b62a64

### Implementation check for step 6 shared_lifecycle_gate (exchange 1) (round 1)

Result:

No. Step 6 has NOT been fully implemented.

The code covers every Step 6 behavior the plan lists. The step's own
completion line is not met: "the resolved day pass with fresh executable
evidence". The only green resolved walk recorded for this tree ran the main
checkout's groundhog, which has no compatibility preflight. No green day walk
of the staged groundhog has run the preflight against this tree. The CLI also
widened its setup-error handler again, undoing the Step 5 round 1 fix. Two
small documentation items are listed with them under the unresolved findings.

What is in place and matches the plan and Q03=C1 and Q04=D1:

- `tools/groundhog/compatibility_preflight.py` (76 lines) reads
  `[tool.llm-shared.lifecycle-compatibility]` strictly. A missing file, table
  or key, or `enabled = false`, disables it. A non-boolean value, a non-table
  parent at any level, or unparsable TOML raises an identifying error, with no
  coercion. It resolves only the target checkout's
  `bin/lifecycle_compatibility.bat` and refuses an enabled project without it.
  `run` checks the Step 5 binding first, then streams the launcher through the
  existing `popen_factory` seam, and turns a non-zero exit into a setup error.
  Nothing is cached.
- `cli.main` validates the declaration for `day` and `full` after the binding
  check and before level resolution, detach and dispatch.
  `day.walk` runs the preflight before reading saved proof, so the no-op,
  upgrade, forced and whole-chain paths all get fresh evidence. A failure
  closes the walk with exit 5, unjudged, and earns no proof.
  `commands.run_tests_outcome` runs it for a direct `full` only
  (`not invocation.in_walk`), so a day-derived full does not repeat it.
- `bin/lifecycle_compatibility.bat` installs only with `--setup`, into
  `venvs/python_3.12_lifecycle_compatibility` from the checkout's
  `requirements-py312.txt`. Validation refuses a relative or missing
  interpreter, naming both the setup command and the override.
  `environment.verify` probes the real executable with `-I` and requires its
  version and all eight pins to match exactly. `_validate` also requires the
  launched interpreter to be the selected one. The directory name has no
  `llm-shared` and sorts below `python_3.13.9_llm-shared_shared_lifecycle_gate`,
  so both kinds of launcher selector keep the main runtime.
- `behavior_scenarios.cases()` adds 13 real-policy projects to the three
  Step 3 barrier probes: the four plugin selections under
  `--strict-config` and `--strict-markers`, tracked and `-o` settings, CPU
  budget rejection, permitted and rejected process starts, fixture
  finalizers with a foreign thread, a nested session, prepared loading, a
  site-free optional-absent child and an invalid declaration. Single summaries
  are counted. `behavior_runner.run_case` bounds each child at 30s and kills
  and reaps it on timeout. `runner._report` prints a failing case and its
  controller tail before the temporary directory is removed.
- `static_entry.py` runs Ruff with `--target-version py310` on each standalone
  policy file, after a PEP 701 negative control that must fail. An AST
  comparison allows only `import sys`, `import pytest` and the identifying
  version refusal before the guard. `check.bat` runs only this static check.

Missing work:

- Run the resolved `ghog day --full=speed --whole-suite` through this
  worktree's own `bin\ghog.bat`, so the staged groundhog runs its preflight,
  and record that green walk with its compatibility output.
- Narrow the `cli.main` setup handler back to adapter error types.
- Restore the Pyright reference comment above `[tool.pyright]`.
- Record the plan file-list deviations and the new test package marker in
  the Step 6 validation rows.

Architecture: groundhog reaches the harness only through the new adapter and
its existing process seam. The harness imports only its own package, the
standard library and pytest, and `tools/__init__.py` imports only standard
library modules under Python 3.12. Provisioning stays in the batch launcher,
and verification is read-only. One smell needs addressing: `cli.main` now
catches plain `OSError` and `ValueError` around level and scope resolution,
which makes its `ScopeError` and `PreparationError` entries redundant (second
finding).

Performance: declaration parsing and manifest checks are linear in small
inputs. The scenario set is fixed at 16, and each child is bounded. The
preflight adds one external harness run per day or direct full, outside the
audited suite, which is the design. The fixture-ownership change removes
conftest and configuration discovery without dropping a case. No performance
issue needs addressing in the code.

Unit test coverage: the gate's source is `tools`, measured with line coverage
(`core = "sysmon"`), and `__init__.py` is omitted. The writer's walk reported
100% for the worktree's `tools` package. That figure is about the tests, which
import this worktree's code, so it holds even though the walk's groundhog was
the main checkout's. Statically, every new top-level symbol has a test:
`_enabled` and `entrypoint` through the declaration matrices, `run` through
the dispatch tests, `interpreter`, `requirements`, `_probe`, `verify`,
`_validate` and `main` in `test_environment_tdd.py`, `mandatory_packages` and
`run_case` in `test_behavior_runner_tdd.py`, `cases` through its parametrized
contracts, and `check_structure`, `syntax`, `_check_files` and `main` in
`test_static_entry_tdd.py`. No unit-tested module below 100% was found. The
staged test-support files are outside the gate, and their top-level symbols are
referenced.

Feature integrity: projects without a declaration spawn nothing, and
interpreter selection, proof matching, scope and reporting are unchanged for
them. For this project, the feature the step adds has not been shown working
end to end in a green walk of the final tree (first finding).

Validation plan effects:

No reviewer edit. The writer's Step 6 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 6 has been fully implemented.`, which this assessment does not
confirm. The rows follow the template. The recorded line counts (commands 627,
CLI 561, day 439, context 141, new helpers 73 to 151) match the staged files.
The runtime matrices (Python 3.12.15 and 3.13.9, 16 scenarios each) and the
launcher selector results are consistent with the code. The performance row
records the walk that ended at 14:57:11 as the step's gate. That walk did not
run the preflight (first finding). The implemented row does not record the
file-list departures or the new test package marker (fourth finding).

The document-level line correctly stays `No, it is not implemented`, with Step
7 pending. The staged diff touches only the Step 6 section. Reviewer mode
completed no umbrella row, and the effort has none.

### Pre-repair mandatory checks and coverage for step 6 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `7abb61174664aeaead9a3157c486fa9242b62a64`, which equals the
request-time tree.

Requestor evidence, not repeated: Windows runs on real Python 3.12.15 and
3.13.9 passed all 16 executable scenarios, and the resolved
`ghog day --full=speed --whole-suite` ended at 2026-11-10T14:57:11+01:00 with
exit 0 on 6202 tests and 100% coverage. That walk ran the main checkout's
groundhog, so it did not run the Step 6 preflight (first finding).

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` and `bin\ghog.bat` (guard cleared,
`SWITCHPY_CHOICE=local`), so the staged groundhog ran itself. Each run passed
the log-freshness check:

- `ghog check` ended at 2026-11-10T15:35:08+01:00 with `exit=0` after
  5m 40.7s. Every step passed: ty, pyright, ruff, the new static entry check
  (`Python 3.10 syntax/refusal boundary and PEP 701 negative control passed`),
  radon, vulture, the 650-line big-file check, Markdown (the review transcript
  included), shellcheck and the EOF check.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-10T15:36:49+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's walk, so 0 tests ran.

Neither command reaches the preflight, which only `day` and `full` run.
Coverage was assessed statically, and no `ghog day` or `ghog full` ran. The
first finding comes from the requestor's report, read before the reviewer's
runs replaced it, and from reading both launchers. The reviewer ran no ad hoc
probe for it.

### Resolved validation set and sources for step 6 shared_lifecycle_gate (exchange 1) (round 1)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. That is the built-in default completed with the bound
whole-suite selector, because the repository has no `.review-validation`
declaration.

The requestor owns this set. The reviewer did not run it. Its recorded result
ended at 2026-11-10T14:57:11+01:00:
`ghog day done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0 full=speed src=param proof=speed reused=none scope=whole`,
with 6202 tests. The saved proof in `.reviews/a.ghog.day.ok` is `proof=speed`
for scope `whole` and fingerprint `686958cd`.

That result is valid test and coverage evidence for the worktree's code.
It is not evidence for the Step 6 preflight: the walk ran the main checkout's
groundhog, which has no preflight (first finding). The rework needs a walk
of this set through the worktree's own launcher.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 6 shared_lifecycle_gate (exchange 1) (round 1)

No drift. There is no `.review-validation` declaration, and the bound scope is
`whole` (fingerprint `686958cd`). The staged change adds no validation command
to the plan or the validation plan. The resolver inputs therefore give the same
single `project` command, `ghog day --full=speed --whole-suite`. Neither
direction adds or drops a command.

### Repository state around validation for step 6 shared_lifecycle_gate (exchange 1) (round 1)

The validation path set holds the 23 staged paths, the implementation plan
and the root `a.ghog.log` that the reviewer evidence commands write. It was
captured before assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `7abb61174664aeaead9a3157c486fa9242b62a64`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it. It passes the
  Markdown check.

### Repair inventory for step 6 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 shared_lifecycle_gate (exchange 1) (round 1)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 23 staged paths and the same four ordered groups as the request
evidence:

1. `feat(lifecycle): validate real Python compatibility`, 12 paths.
2. `feat(ghog): require fresh compatibility evidence`, 9 paths.
3. `perf(tests): trim fixture ownership preparation`, 1 path.
4. `docs(shared_lifecycle_gate): record step 6 validation`, 1 path.

Reviewer judgment on grouping and scope: membership and order are correct.
The harness, its launcher, the `check.bat` static step and their tests come
first. The groundhog integration that runs the harness depends on them and
comes second, with the applicability declaration and the virtual filesystem
route. The fixture-ownership change is a separate test performance fix, and
the validation record comes last. The bodies match the staged changes, and no
AI attribution trailer is present.

`a.commit` is accurate for the received state. The group 2 body will need an
update if the rework adds a dedicated compatibility error type.

### Findings and boundaries for step 6 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings:

- The recorded green walk did not run the Step 6 preflight. The request says
  compatibility preflight passed before the covered full run of the walk
  that ended at 2026-11-10T14:57:11+01:00. The reviewer read the root
  `a.ghog.log` of that walk before its own evidence commands replaced it. It
  has no compatibility output: no `Compatibility interpreter:` line and none of
  the 16 `Compatibility <case>: passed` lines that `runner._report` prints.
  The run's `ended` header gives `duration=4m 03.3s`, so it started at about
  14:53:07.7, and its `ghog check` header starts at 14:53:09. That leaves about
  1.3 seconds before `check.bat`, too little for 16 real pytest projects,
  including the xdist barrier probes. These facts fit a run through
  the canonical shared ghog launcher. That launcher starts
  `%~dp0..\tools\groundhog\cli.py`, and the bootstrap in `cli.py` puts that
  checkout first on `sys.path`. The main checkout has no
  `tools/groundhog/compatibility_preflight.py`, so its day walk skips the
  preflight. The 6202 tests and 100% coverage of that walk still stand,
  because pytest imported this worktree's code. But the plan's completion
  line asks for the resolved day to pass "with fresh executable evidence", and
  no green walk shows it for the final staged tree.
- `cli.main` again catches plain `ValueError`, and now `OSError`, around level
  and scope resolution (`tools/groundhog/cli.py` line 190). The handler is
  `(OSError, ValueError, LevelError, scope.ScopeError, pytest_environment.PreparationError)`.
  `ScopeError` and `PreparationError` are `ValueError` subclasses, so those
  two entries are now redundant. Any unrelated `ValueError` or `OSError` from
  `_with_level` or `_with_scope` becomes a one-line setup error instead of a
  traceback. Step 5 round 1 asked for this boundary to be narrowed to the
  adapter's own error type, and round 2 fixed it. `compatibility_preflight`
  raises a plain `ValueError` for both its declaration errors, and
  `entrypoint` already turns `OSError` into that error, so `OSError` is not
  needed for the new call.
- The Pyright reference comment now sits above the wrong table
  (`pyproject.toml` lines 95 to 99). The new
  `[tool.llm-shared.lifecycle-compatibility]` table was inserted between
  `# https://github.com/microsoft/pyright/blob/main/docs/configuration.md` and
  `[tool.pyright]`. The link now reads as documenting the applicability
  declaration.
- The Step 6 validation rows do not record the departures from the plan's file
  list. The plan names `tools/lifecycle_compatibility/scenarios.py`,
  `tests/unit/tools/test_groundhog_acceptance_day.py` and
  `tests/unit/tools/test_groundhog_commands.py` as files to update. None of
  them changed. The work went to new `behavior_scenarios.py`,
  `behavior_runner.py` and `environment.py` modules and a new
  `tests/unit/tools/test_compatibility_preflight` package. `tools/groundhog/cli.py`
  and `tests/memory_filesystem.py` changed without being named in the plan.
  The split is reasonable, but the plan allows splitting scenario builders
  "if they approach 650" lines, and `scenarios.py` has 75. The addendum also
  says to "record any additional package markers explicitly", and
  `tests/unit/tools/test_compatibility_preflight/__init__.py` is not named in
  the rows.

Boundary-crossing work: None.

### Writer instructions for step 6 shared_lifecycle_gate (exchange 1) (round 1)

1. Preflight evidence: run the resolved `ghog day --full=speed --whole-suite`
   from this worktree's root through its own launcher, for example
   `set NO_MORE_SENV_llm-shared_shared_lifecycle_gate=& .\senv.bat && bin\ghog.bat day --full=speed --whole-suite`,
   not through the canonical shared ghog launcher. Because the
   tree carries a saved speed proof, the walk will be a no-op after the
   preflight, which is enough to show the preflight. Check that its
   `a.ghog.log` shows the `Compatibility interpreter:` line and the 16
   `Compatibility <case>: passed` lines before the closing line. If
   they do not reach the report, route them there. If the tree changes for the
   other items, the walk reruns the whole chain and gives fresh coverage too.
   Record the walk's end time, exit and counts in the Step 6 performance row,
   and correct the request assessment so it names the walk that ran the
   preflight.
2. Error boundary: give `tools/groundhog/compatibility_preflight.py` its own
   error type, for example `class CompatibilityError(ValueError)`, and raise it
   from `entrypoint` and `run`. In `cli.main`, catch
   `compatibility_preflight.CompatibilityError` and drop the plain `OSError`
   and `ValueError`, so the handler is
   `(LevelError, scope.ScopeError, pytest_environment.PreparationError, compatibility_preflight.CompatibilityError)`.
   `day.walk` and `commands.run_tests_outcome` may keep catching `OSError`,
   because `run` starts a process there. Keep the
   `test_malformed_setup_prevents_children` assertions, and match the new
   type in the declaration tests.
3. `pyproject.toml`: move the Pyright reference comment back directly above
   `[tool.pyright]`, so it stays with the Pyright settings. Leave the
   `[tool.llm-shared.lifecycle-compatibility]` table where it is or give it its
   own short comment.
4. Validation rows: in the Step 6 "What was implemented" row, record that
   `scenarios.py`, `test_groundhog_acceptance_day.py` and
   `test_groundhog_commands.py` were left unchanged. Say why the behavior cases
   went to `behavior_scenarios.py` and `behavior_runner.py`, and the
   prerequisite checks to `environment.py`. Name the new
   `tests/unit/tools/test_compatibility_preflight/__init__.py` package marker
   and the unplanned `cli.py` and `tests/memory_filesystem.py` changes. Update
   the group 2 `a.commit` body if the error type changes.

Non-blocking notes:

- `static_entry._check_files` passes if `tools/pytest_plugins` holds no
  `llm_shared_*.py` file. Asserting the three expected policy files, or at
  least a non-empty match, would stop a rename from silently emptying the
  check.
- `test_runner_all_mode_validates_versions_and_aggregates` checks only that
  `verify` ran once. It could also assert the checkout root and the version
  passed to it, and the 16 aggregated results.

### Decision rationale for step 6 shared_lifecycle_gate (exchange 1) (round 1)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 6,
  round 1, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `7abb6117` all agree with the live exchange and index.
- Completeness: fail. Every Step 6 behavior is in the code. But the step's
  completion line requires the resolved day to pass with fresh executable
  evidence, and no green walk of the staged groundhog has run the preflight.
- Validation and coverage: fail. Reviewer `ghog check` and
  `ghog affected --no-cov` both exited 0, and static reading finds no coverage
  gap. The requestor's green speed walk ran the main checkout's groundhog, so
  the resolved set has not validated the preflight that this step adds.
- Staged attribution: pass. All 23 staged paths are writer work in four
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: fail. Four findings are unresolved: the missing preflight
  evidence, the widened CLI error handler, the misplaced Pyright comment and
  the unrecorded file-list departures.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping is accurate for the received state.

This round made no repair, substantive or polishing. The request has no
literal `Human guidance:` block, so the reviewer reports findings only.

Disposition: changes requested.

### Final reviewer decision for step 6 shared_lifecycle_gate (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-1 -->

## Round 2 by requestor - Step 6

- Recorded: 2026-11-10T17:25:39+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 6
- Outcome: request

### Review identity for step 6 shared_lifecycle_gate (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 6
Review round: 2

### Code review evidence for step 6 shared_lifecycle_gate (round 2)

request_index_tree: 0ec5ee24a5b97bcdb651e41249f1104942549d3a
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(lifecycle): validate real Python compatibility
group 1 path: bin/lifecycle_compatibility.bat
group 1 path: check.bat
group 1 path: tools/lifecycle_compatibility/behavior_runner.py
group 1 path: tools/lifecycle_compatibility/behavior_scenarios.py
group 1 path: tools/lifecycle_compatibility/environment.py
group 1 path: tools/lifecycle_compatibility/requirements-py312.txt
group 1 path: tools/lifecycle_compatibility/runner.py
group 1 path: tools/lifecycle_compatibility/static_entry.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_environment_tdd.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_static_entry_tdd.py
group 2: feat(ghog): require fresh compatibility evidence
group 2 path: pyproject.toml
group 2 path: tools/groundhog/cli.py
group 2 path: tools/groundhog/commands.py
group 2 path: tools/groundhog/compatibility_preflight.py
group 2 path: tools/groundhog/context.py
group 2 path: tools/groundhog/day.py
group 2 path: tests/memory_filesystem.py
group 2 path: tests/unit/tools/test_compatibility_preflight/__init__.py
group 2 path: tests/unit/tools/test_compatibility_preflight/test_compatibility_preflight_tdd.py
group 3: perf(tests): trim embedded pytest preparation
group 3 path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
group 3 path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
group 4: docs(shared_lifecycle_gate): record step 6 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: bin/lifecycle_compatibility.bat
staged path: check.bat
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: pyproject.toml
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_environment_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_static_entry_tdd.py
staged path: tests/unit/tools/test_compatibility_preflight/__init__.py
staged path: tests/unit/tools/test_compatibility_preflight/test_compatibility_preflight_tdd.py
staged path: tools/groundhog/cli.py
staged path: tools/groundhog/commands.py
staged path: tools/groundhog/compatibility_preflight.py
staged path: tools/groundhog/context.py
staged path: tools/groundhog/day.py
staged path: tools/lifecycle_compatibility/behavior_runner.py
staged path: tools/lifecycle_compatibility/behavior_scenarios.py
staged path: tools/lifecycle_compatibility/environment.py
staged path: tools/lifecycle_compatibility/requirements-py312.txt
staged path: tools/lifecycle_compatibility/runner.py
staged path: tools/lifecycle_compatibility/static_entry.py
```

### Validation scope for step 6 shared_lifecycle_gate (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 6 shared_lifecycle_gate (round 2)

Yes. Step 6 has been fully implemented.

The exact plan step is satisfied by tracked strict applicability, fresh
checkout-owned executable evidence before saved-proof decisions and direct
full, an explicitly provisioned and verified independent Python 3.12 runtime,
bounded real-policy scenarios and whole-file Python 3.10 syntax/refusal checks.
Undeclared consumers gain no compatibility prerequisite. Step 7 stays pending.

Round 1 returned changes-requested and made no repair. The writer accepted all
four findings and both optional suggestions. The dedicated compatibility error
restores the narrow CLI boundary; the Pyright comment and explicit file-list
deviations are corrected. Empty static policy sets now fail, and aggregation
tests require the exact runtime arguments and all 16 scenario results.
The staged diff contains these writer repairs and both profiled test
preparation improvements. No reviewer change was reversed.

The genuine local `bin/ghog.bat day --full=speed --whole-suite` ended at
2026-11-10T17:21:40+01:00 with exit 0. Its fresh log starts with verified Python
3.12 and exact manifest dependencies, then all 16 `Compatibility <case>: passed`
lines. Static checks passed, followed by 6203 tests and 100% tools coverage.
The closing line reports fail=0, warn=0, xfail=0, outliers=0, excluded=0,
proof=speed, reused=none and scope=whole. Freshness was verified and status
confirmed state=done. No exclusion or budget weakening was used.

The earlier 14:57:11 canonical-launcher walk did not run this step's preflight;
the previous request's contrary attribution is withdrawn. The first genuine
local walk passed preflight but found an actual CPU-budget failure. Profiling
and explicit configuration removed unnecessary embedded pytest preparation;
the entire focused file passed before the final green local walk.

Supplemental real Python 3.12.15 and 3.13.9 matrices each passed all 16 cases
under pytest 9.1.0 and xdist 3.8.0. Optional absence, real process permissions,
worker cancellation, no-start barriers and cleanup are exercised externally.
The normal launcher selectors retain the main Python 3.13 runtime.

Implementation-check records the exact Yes verdict for Step 6. The adapter and
process seams preserve architecture boundaries; all changed Python files stay
below 650 lines. Declaration and manifest processing are linear in bounded
inputs, scenarios and diagnostics are fixed-size, and external waits are
bounded. No architecture, performance, coverage or feature-integrity gap was
found. Exhaustive finite parametrization covers the new domains; earlier path
properties remain applicable.

The root `a.commit` covers all 24 staged paths in four ordered groups, with the
expanded test-preparation group and required final validation subject. The
readiness checker reports valid, ready=true and no diagnostics. The versioned
review transcript remains unstaged for the authorized residual commit.

### Implementation report for step 6 shared_lifecycle_gate (round 2)

The independent compatibility launcher provisions only on explicit `--setup`.
Ordinary validation checks actual executable version and exact checkout pins,
then runs isolated real-policy cases and bounded xdist worker barriers. The
optional-absent case uses a site-free child containing only mandatory packages.
Failure diagnostics remain visible before automatic temporary cleanup.

Tracked literal applicability selects the target checkout's fixed entrypoint.
Malformed declarations fail before detach; inherited foreign bindings fail
before the harness. Every day invocation preflights before proof reuse;
direct full preflights once, while day-derived full avoids duplication.
Undeclared consumers gain no compatibility environment prerequisite.

Round 1 repairs introduce `CompatibilityError` to preserve the CLI's narrow
setup-error boundary, restore the Pyright comment and document the implementation
file-list deviations. Additional regression coverage rejects empty static policy
sets and verifies the exact runtime and complete 16-scenario aggregation.

Process-free tests cover transport and orchestration, every day level, saved
proof, forced and upgraded walks, direct full, invalid declarations and missing
prerequisites. The preflight test package uses the existing virtual filesystem.
A profiled fixture-ownership matrix uses explicit configuration and collected
declarations, preserving every scope, permission, finalizer and cleanup assertion.
A second profiled repair gives all seven malformed-marker cases explicit
configuration without conftest discovery, preserving real collection errors and
the sentinel proving setup never starts.
No lifecycle limit or coverage target was weakened. No exclusion was accepted.

All changed production Python files remain below 650 lines. Existing directory
targets cover the Python 3.12 harness. Launcher selector inspection keeps the
main Python 3.13 runtime selected. Step 7 remains pending.

Writer notes: `.reviews/a.shared_lifecycle_gate.step6.journal.md` and
`.reviews/a.shared_lifecycle_gate.step6.handoff.md`.

### Change summary for step 6 shared_lifecycle_gate (round 2)

The root `a.commit` covers every staged path in four dependency-ordered groups.

1. `feat(lifecycle): validate real Python compatibility`: the batch launcher,
   `check.bat`, new behavior/environment/static modules, independent manifest,
   extended runner and four compatibility test files.
2. `feat(ghog): require fresh compatibility evidence`: tracked applicability,
   groundhog CLI/commands/context/day, new preflight adapter, virtual filesystem
   routing and the new preflight test package.
3. `perf(tests): trim embedded pytest preparation`: the existing ownership
   scope/permission matrix and seven malformed-marker cases retain every
   assertion with less pytest preparation.
4. `docs(shared_lifecycle_gate): record step 6 validation`: the validation plan.

Staged paths:

- `bin/lifecycle_compatibility.bat`
- `check.bat`
- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`
- `pyproject.toml`
- `tests/memory_filesystem.py`
- `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_audit_ownership/test_audit_ownership_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_compatibility_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_environment_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_static_entry_tdd.py`
- `tests/unit/tools/test_compatibility_preflight/__init__.py`
- `tests/unit/tools/test_compatibility_preflight/test_compatibility_preflight_tdd.py`
- `tools/groundhog/cli.py`
- `tools/groundhog/commands.py`
- `tools/groundhog/compatibility_preflight.py`
- `tools/groundhog/context.py`
- `tools/groundhog/day.py`
- `tools/lifecycle_compatibility/behavior_runner.py`
- `tools/lifecycle_compatibility/behavior_scenarios.py`
- `tools/lifecycle_compatibility/environment.py`
- `tools/lifecycle_compatibility/requirements-py312.txt`
- `tools/lifecycle_compatibility/runner.py`
- `tools/lifecycle_compatibility/static_entry.py`

### Writer response for step 6 shared_lifecycle_gate (round 2)

Writer response:

All four round 1 findings are accepted. No reviewer repairs were made, so the
writer owns every repair and the staged tree. There is no disagreement.

The earlier 14:57:11 walk used the canonical launcher and did not exercise the
new preflight. Its test and coverage evidence remains valid. The previous
request's assertion that this walk ran the preflight is withdrawn; the new
assessment and validation record identify the genuine local-launcher evidence.

`CompatibilityError` now identifies declaration and harness failures. The CLI
catches only the dedicated adapter types around compatibility, level and scope
resolution. Declaration tests require that type and retain all malformed
before-detach assertions. Day and direct full retain process-spawn handling.
The Pyright reference comment again directly precedes its own table.

The validation record names all file-list deviations, the new package marker,
and the responsibility split of behavior construction, transport and prerequisite
verification. Group 2's commit body now records the narrow error boundary.

Both optional suggestions are also addressed: an empty standalone policy set
fails the static gate, and the full-runner test checks the exact checkout,
interpreter/version arguments and all 16 aggregated scenario results.

The first genuine local walk passed all 16 compatibility scenarios but exposed
a malformed-marker test lifecycle at 0.125000s CPU, above its 0.100s ceiling.
Profiling reproduced 0.140625s CPU and identified embedded pytest preparation.
That test now passes explicit configuration and skips unnecessary conftest
discovery, retaining all seven marker variants and setup-refusal assertions.
Its complete focused file passed before the fresh whole-suite walk.

### Reviewer focus for step 6 shared_lifecycle_gate (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-2 -->

## Round 2 by reviewer - Step 6

- Recorded: 2026-11-10T17:35:26+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 shared_lifecycle_gate (exchange 1) (round 2)

Baseline index tree: 0ec5ee24a5b97bcdb651e41249f1104942549d3a

Assessed index tree: 0ec5ee24a5b97bcdb651e41249f1104942549d3a

### Implementation check for step 6 shared_lifecycle_gate (exchange 1) (round 2)

Result:

Yes. Step 6 has been fully implemented.

All four round 1 findings are fixed, and both non-blocking notes were taken
up. The resolved day now ran the staged groundhog, and its report shows the
fresh executable preflight before any check or proof decision. That meets the
step's completion line.

Round 1 findings, rechecked against the delta from tree `7abb6117` to
`0ec5ee24`:

- Preflight evidence: fixed. The requestor's root `a.ghog.log`, which the
  reviewer copied before its own runs, is from a walk that ended at
  2026-11-10T17:21:40+01:00. It opens with the verified interpreter line
  (`venvs\python_3.12_lifecycle_compatibility`, Python 3.12, all eight pins)
  and the 16 `Compatibility <case>: passed` lines. Only then does the
  `ghog check` header start, at 17:17:21. The run's 6m 21.8s duration puts its
  start at about 17:15:18, so the preflight took about two minutes, which fits
  16 real pytest projects. The walk closes with
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0 full=speed src=param proof=speed reused=none scope=whole`.
  The request and the validation rows now say that the 14:57:11 walk proved
  tests and coverage only.
- Error boundary: fixed. `compatibility_preflight.CompatibilityError`
  (a `ValueError` subclass) is raised for a malformed declaration, a missing
  entrypoint and a failed harness. `cli.main` catches
  `(LevelError, scope.ScopeError, pytest_environment.PreparationError, compatibility_preflight.CompatibilityError)`,
  so an unrelated `ValueError` or `OSError` from `_with_level` or
  `_with_scope` keeps its traceback again. `day.walk` and
  `commands.run_tests_outcome` still catch `OSError` around the process start.
  The declaration tests now require the new type.
- Pyright comment: fixed. The reference link sits directly above
  `[tool.pyright]` again.
- File-list departures: fixed. The implemented row names the three unchanged
  plan files, says where behavior construction, transport and prerequisite
  checks went, names the new test package marker and explains the `cli.py`
  and `tests/memory_filesystem.py` changes.

Non-blocking notes from round 1, both addressed: `static_entry._check_files`
now fails when no `llm_shared_*.py` policy file is found, with a test that
empties the glob. `test_runner_all_mode_validates_versions_and_aggregates` now
asserts the checkout root, the interpreter and version passed to `verify`,
and all 16 aggregated results in order.

The round 2 delta adds one more test change, in
`test_audit_declarations_tdd.py`: the seven malformed-marker cases register
the marker in an explicit `pytest.ini` and run with `--noconftest`, instead of
through a generated conftest. The autouse `never` fixture, the usage-error
exit and the error-output assertions are unchanged, so the test still proves
that setup never starts. The other tests in that file still use `_REGISTER`.

The rest of Step 6 is unchanged from round 1 and still matches the plan,
Q03=C1 and Q04=D1: strict literal applicability, the target checkout's fixed
launcher, the preflight before every day proof decision and once per direct
full, explicit-only provisioning with exact pin verification, the 16 bounded
real-policy scenarios and the Ruff `py310` plus AST prefix static check.

Architecture: groundhog reaches the harness only through its adapter, which
now also owns the error type that the CLI catches. The harness imports only
its own package, the standard library and pytest. No DDD-Hexagonal violation
or smell needs addressing.

Performance: the delta adds one tuple of policy paths and a length check, so
nothing changes. The preflight took about two minutes in the resolved walk.
That cost is one external run per day or direct full, outside the audited
suite, as the design intends. The two test-preparation changes remove
conftest discovery without dropping a case. No performance issue needs
addressing.

Unit test coverage: the gate's source is `tools`, measured with line coverage,
and `__init__.py` is omitted. The resolved walk of the staged groundhog
reported 100% for that scope over 6203 tests. Statically, the new
`CompatibilityError` raises are covered by the declaration, missing-entrypoint
and failed-harness tests. The empty-set branch of `_check_files` is covered by
`test_empty_policy_set_fails_static_validation`. No unit-tested module below
100% was found. The staged test-support files are outside the gate, and their
top-level symbols are referenced.

Feature integrity: projects without a declaration spawn nothing. This project
now shows the preflight working end to end in the resolved walk. Setup errors
from level and scope resolution keep their previous surface. No existing
feature or reporting capability is impaired.

Validation plan effects:

No reviewer edit. The writer's Step 6 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 6 has been fully implemented.`, which this assessment confirms. The
round 2 changes are accurate:

- The implemented row adds `CompatibilityError`, the malformed-marker
  preparation change and the file-list departures with the new package
  marker.
- The new-types row names `CompatibilityError`.
- The architecture row's line counts (CLI 562, commands 627, day 439,
  context 141, compatibility modules 78 to 163) match the staged files.
- The performance row separates the 14:57:11 walk, which proves tests and
  coverage only, from the 17:21:40 walk through this worktree's launcher. It
  also records the first local walk's 0.125000s CPU result and its fix, with
  no exception or exclusion.

The document-level line correctly stays `No, it is not implemented`, with Step
7 pending. The staged diff touches only the Step 6 section. Reviewer mode
completed no umbrella row, and the effort has none.

### Pre-repair mandatory checks and coverage for step 6 shared_lifecycle_gate (exchange 1) (round 2)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `0ec5ee24a5b97bcdb651e41249f1104942549d3a`, which equals the
request-time tree.

Requestor evidence, not repeated: the resolved
`ghog day --full=speed --whole-suite`, run through this worktree's own
launcher, ended at 2026-11-10T17:21:40+01:00 with exit 0, the 16 passing
compatibility scenarios first and 100% coverage, as described under the
resolved validation set. The real Python 3.12.15 and 3.13.9 matrices from
round 1 still stand.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` and `bin\ghog.bat` (guard cleared,
`SWITCHPY_CHOICE=local`), so the staged groundhog ran itself. Each run passed
the log-freshness check:

- `ghog check` ended at 2026-11-10T17:32:35+01:00 with `exit=0` after
  2m 17.3s. Every step passed: ty, pyright, ruff, the static entry check
  (`Python 3.10 syntax/refusal boundary and PEP 701 negative control passed`),
  radon, vulture, the 650-line big-file check, Markdown (the review transcript
  included), shellcheck and the EOF check.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-10T17:33:45+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's walk, so 0 tests ran. That also indicates
  the walk ran on this tree.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran.

### Resolved validation set and sources for step 6 shared_lifecycle_gate (exchange 1) (round 2)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` source. That is the built-in default completed with the bound
whole-suite selector, because the repository has no `.review-validation`
declaration.

The requestor owns this set and ran it through this worktree's own
`bin\ghog.bat`. The reviewer did not run it, but copied the root `a.ghog.log`
before its own evidence commands replaced it, to
`.reviews/a.shared_lifecycle_gate.step6.tmp.r2.rv-requestor-day.log`. That log
was last written at 2026-11-10T17:21:40+01:00 and shows:

- the verified Python 3.12 interpreter with all eight exact pins, then the 16
  `Compatibility <case>: passed` lines, before any check;
- `ghog check` exit 0, from 17:17:21 to 17:19:49;
- `ghog affected --no-cov` exit 0;
- `ghog full` with `cov=100 outliers=0 excluded=0 exit=0`;
- the closing
  `ghog day done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0 full=speed src=param proof=speed reused=none scope=whole`.

The request counts 6203 tests. This is a green speed proof with measured 100%
coverage, and it exercises the Step 6 preflight. No exclusion, limit change or
timing exception was used.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 6 shared_lifecycle_gate (exchange 1) (round 2)

No drift. There is no `.review-validation` declaration, and the bound scope is
`whole` (fingerprint `686958cd`). The round 2 delta adds no validation command
to the plan or the validation plan. The resolver inputs therefore give the same
single `project` command, `ghog day --full=speed --whole-suite`. Neither
direction adds or drops a command.

### Repository state around validation for step 6 shared_lifecycle_gate (exchange 1) (round 2)

The validation path set holds the 24 staged paths, the implementation plan
and the root `a.ghog.log` that the reviewer evidence commands write. It was
captured before assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged, because the
  request states `Umbrella draft: none`.
- After assessment, the live index tree is still
  `0ec5ee24a5b97bcdb651e41249f1104942549d3a`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended it, and the requestor's residual commit owns it. It passes the
  Markdown check.

### Repair inventory for step 6 shared_lifecycle_gate (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 shared_lifecycle_gate (exchange 1) (round 2)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 24 staged paths and the same four ordered groups as the request
evidence:

1. `feat(lifecycle): validate real Python compatibility`, 12 paths.
2. `feat(ghog): require fresh compatibility evidence`, 9 paths.
3. `perf(tests): trim embedded pytest preparation`, 2 paths.
4. `docs(shared_lifecycle_gate): record step 6 validation`, 1 path.

Reviewer judgment on grouping and scope: the order is still correct. The new
`test_audit_declarations_tdd.py` change belongs with the fixture-ownership
change in group 3, and the group's subject and body now cover both. Group 2's
body records the narrow CLI error handling, as round 1 asked. The groups' own
`git add` lines include a blank line inside group 3, which the checker accepts.
No AI attribution trailer is present.

`a.commit` is accurate for the received state.

### Findings and boundaries for step 6 shared_lifecycle_gate (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 6 shared_lifecycle_gate (exchange 1) (round 2)

No further implementation work is requested for Step 6.

### Decision rationale for step 6 shared_lifecycle_gate (exchange 1) (round 2)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 6,
  round 2, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `0ec5ee24` all agree with the live exchange and index.
- Completeness: pass. Every Step 6 obligation is implemented, the completion
  line's fresh executable evidence is now in the resolved walk, and all four
  round 1 findings are fixed.
- Validation and coverage: pass. The requestor's resolved speed walk through
  the staged groundhog is green with 100% measured coverage and the preflight
  first. Reviewer `ghog check` and `ghog affected --no-cov` both exited 0, and
  static reading finds no coverage gap.
- Staged attribution: pass. All 24 staged paths are writer work in four
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: pass. No current or carried finding is unresolved, and both round
  1 notes were addressed.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping and bodies are accurate.

This round made no repair, substantive or polishing. The request has no
literal `Human guidance:` block.

Disposition: commit-ready. This is an advisory recommendation and does not
authorize a commit.

### Final reviewer decision for step 6 shared_lifecycle_gate (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-6-round-2 -->

## Round 2 by human - Step 6 - human-confirmation

- Recorded: 2026-11-10T19:14:39+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 6
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 7

- Recorded: 2026-11-10T21:53:40+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 7
- Outcome: request

### Review identity for step 7 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 7
Review round: 1

### Code review evidence for step 7 shared_lifecycle_gate (round 1)

request_index_tree: baa1914e59993516d28d28a52b773e41db301585
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project, plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "none", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(pytest): preserve cache for drive-root callers
group 1 path: tools/pytest_plugin_environment.py
group 1 path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
group 2: test(pytest): expand executable compatibility cases
group 2 path: tools/lifecycle_compatibility/behavior_runner.py
group 2 path: tools/lifecycle_compatibility/behavior_scenarios.py
group 2 path: tools/lifecycle_compatibility/runner.py
group 2 path: tools/lifecycle_compatibility/scenarios.py
group 2 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
group 3: test(pytest): join prepared consumer policies
group 3 path: tests/memory_filesystem.py
group 3 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 3 path: tests/acceptance/shared_lifecycle/__init__.py
group 3 path: tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py
group 3 path: tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py
group 4: docs(pytest): document shared policy adoption
group 4 path: instructions/write-fast-python-tests.md
group 4 path: wiki/README.md
group 4 path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
group 4 path: wiki/how-to/register-groundhog-in-a-project.md
group 4 path: wiki/how-to/set-test-lifecycle-limits.md
group 4 path: wiki/reference/ghog-commands-and-exit-codes.md
group 4 path: wiki/reference/test-lifecycle-limits.md
group 4 path: wiki/how-to/enable-shared-lifecycle-gate.md
group 4 path: wiki/how-to/enable-shared-process-audit.md
group 4 path: wiki/how-to/validate-shared-pytest-compatibility.md
group 4 path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
group 5: docs(shared_lifecycle_gate): record step 7 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: instructions/write-fast-python-tests.md
staged path: tests/acceptance/shared_lifecycle/__init__.py
staged path: tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py
staged path: tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
staged path: tools/lifecycle_compatibility/behavior_runner.py
staged path: tools/lifecycle_compatibility/behavior_scenarios.py
staged path: tools/lifecycle_compatibility/runner.py
staged path: tools/lifecycle_compatibility/scenarios.py
staged path: tools/pytest_plugin_environment.py
staged path: wiki/README.md
staged path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
staged path: wiki/how-to/enable-shared-lifecycle-gate.md
staged path: wiki/how-to/enable-shared-process-audit.md
staged path: wiki/how-to/register-groundhog-in-a-project.md
staged path: wiki/how-to/set-test-lifecycle-limits.md
staged path: wiki/how-to/validate-shared-pytest-compatibility.md
staged path: wiki/reference/ghog-commands-and-exit-codes.md
staged path: wiki/reference/test-lifecycle-limits.md
```

### Validation scope for step 7 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 7 shared_lifecycle_gate (round 1)

Yes. Step 7 has been fully implemented under the user's explicit instruction
to continue when measured CPU is within budget and only wall time fails.
The validation plan records that distinction; green release acceptance is
unproven. Review the exact staged implementation and its acceptance mapping.

Focused acceptance passed five tests with no warnings. Actual Python 3.12.15
and 3.13.9 each passed all 25 executable compatibility cases, with pytest 9.1.0
and xdist 3.8.0. Eleven real Windows shell probes passed. An anonymous consumer
passed 23 existing tests in each of prepared-shell and genuine groundhog child
contexts, with unchanged files and persistent activation and restored transient
state. An earlier affected rerun passed without failures, warnings or xfails.

The final self-hosted `ghog day --full=speed --whole-suite` ended
2026-11-10T21:44:10+01:00, exit 2 after 18m00.2s. Fresh executable preflight
and static checks passed. The full stage measured 6,221 lifecycles and reported
11 wall-only errors: CPU 0.015625-0.156250s against the effective 0.250s band
limit, wall 1.029650-6.201089s against 1.000s. No assertion failures, warnings
or xfails were reported. Coverage, speed/outlier and exclusion verdicts were
withheld. Do not interpret CPU-based continuation as a green automated verdict
or measured 100% coverage. The user instruction supersedes the ordinary green
walk prerequisite for this continuation; no additional timing run is requested.

The coverage gate still targets `tools` at 100%, omitting tests and package
markers. Static inspection found no missing new unit-test branch or unreferenced
out-of-scope top-level helper. No architecture issue, impaired feature or new
superlinear computation was identified. All changed Python files are below 650
lines. All 12 changed Markdown files pass lint and spelling. Root `a.commit`
passes the readiness checker with five groups and no diagnostics.

Record comparison preserved all 5,892 previous eligible proofs and added 345;
no nodes or proofs were lost and exception/raw/other document fields were
unchanged. No limit, assertion, process permission or duration exclusion was
added or weakened. No accepted exclusion was introduced by this step. Final
automated exclusion assessment was withheld along with the failed full stage.
Linux and macOS remain unvalidated.

### Implementation report for step 7 shared_lifecycle_gate (round 1)

The acceptance journey joins real preparation, groundhog environment isolation,
canonical policy loading, strict settings, fixture cleanup, unused permission
summaries and selected record writes for all four selections. Generated scratch
files use the existing memory filesystem and a local source adapter. Explicit
configuration and `--noconftest` use a supplied guarded startup hook; actual
conftest discovery remains covered by the executable matrix.

Executable compatibility now uses real preparation and imports consumer-owned
`tools` and `tests` packages. Added cases cover all prepared selections, guarded
registration orders, explicit duplicate loading, gate-only processes and
distributed fixture aggregation. Empty child probes skip site startup and
barrier children omit unused plugins without changing deadlines or assertions.
A reusable Windows caller body supports real shell probes. Drive-root callers
now retain user-local cache storage, with a unit regression preserving the
ordinary checkout/cache boundary.

Three new adoption guides explain independent activation, process ownership
and explicit compatibility setup. Existing wiki pages and the canonical
fast-test instruction link the supported routes. Anonymous acceptance evidence
maps every requirement and design case to named observations and records the
unproven whole-suite release gates. The validation plan records all seven
implementation verdicts with the same limitation.

Writer notes: `.reviews/a.shared_lifecycle_gate.step7.journal.md` and
`.reviews/a.shared_lifecycle_gate.step7.handoff.md`.

### Change summary for step 7 shared_lifecycle_gate (round 1)

The staged set contains 24 paths in five ordered groups.

#### Grouping commits by topic for step 7 shared_lifecycle_gate (round 1)

##### Group 1: Drive-root preparation cache for step 7 shared_lifecycle_gate (round 1)

git add -A tools/pytest_plugin_environment.py
git add -A tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py

```log
fix(pytest): preserve cache for drive-root callers

Why:

A drive-root consumer rejected the normal user-local loader cache because every
path on the drive appeared to be inside the project.

Preparation now distinguishes a filesystem root from a checkout directory while
retaining the cache boundary for ordinary projects and shared sources.

What:

- Accept user-local cache storage when the caller is a drive root.
- Retain rejection of the project root itself and shared-checkout storage.
- Cover drive-root binding and immutable cache publication in a regression.
```

##### Group 2: Executable compatibility acceptance for step 7 shared_lifecycle_gate (round 1)

git add -A tools/lifecycle_compatibility/behavior_runner.py
git add -A tools/lifecycle_compatibility/behavior_scenarios.py
git add -A tools/lifecycle_compatibility/runner.py
git add -A tools/lifecycle_compatibility/scenarios.py
git add -A tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py

```log
test(pytest): expand executable compatibility cases

Why:

Release acceptance needs actual prepared selection, consumer package identity
and distributed fixture usage beyond the individual policy units.

The separate executable matrix now checks those contracts on real runtimes and
retains bounded failure cleanup without carrying-suite process grants.

What:

- Exercise all prepared selections and guarded settings in both orders.
- Import consumer-owned tools and tests packages in isolated children.
- Check duplicate loading, gate-only processes and worker aggregation.
- Add a reusable Windows caller probe and trim unrelated child startup.
- Retain all existing deadlines, policy limits and evidence assertions.
```

##### Group 3: Integrated prepared-consumer acceptance for step 7 shared_lifecycle_gate (round 1)

git add -A tests/memory_filesystem.py
git add -A tests/unit/tools/shared_lifecycle/inline_session.py
`git add -A tests/acceptance/shared_lifecycle/__init__.py`
`git add -A tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py`
git add -A tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py

```log
test(pytest): join prepared consumer policies

Why:

Separate policy tests do not prove that preparation, groundhog child isolation,
canonical loading and record writes work together.

An in-process consumer journey checks all four selections with strict settings,
fixture cleanup, unused permissions and parent-state restoration.

What:

- Join the real environment builder, runner boundary and pytest hooks.
- Verify summary counts, unused declarations and selected record writes.
- Route generated resources through the existing memory filesystem.
- Keep real conftest discovery and process checks in the executable matrix.
```

##### Group 4: Shared policy adoption and acceptance evidence for step 7 shared_lifecycle_gate (round 1)

git add -A instructions/write-fast-python-tests.md
git add -A wiki/README.md
git add -A wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
git add -A wiki/how-to/register-groundhog-in-a-project.md
git add -A wiki/how-to/set-test-lifecycle-limits.md
git add -A wiki/reference/ghog-commands-and-exit-codes.md
git add -A wiki/reference/test-lifecycle-limits.md
git add -A wiki/how-to/enable-shared-lifecycle-gate.md
git add -A wiki/how-to/enable-shared-process-audit.md
git add -A wiki/how-to/validate-shared-pytest-compatibility.md
git add -A docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md

```log
docs(pytest): document shared policy adoption

Why:

Consumers need the supported opt-in, settings, permission and compatibility
routes together with evidence that matches the platforms actually tested.

The wiki explains independent activation and operation scope, and anonymous
acceptance evidence maps every requirement and design case to a check.

What:

- Document shell preparation, strict configuration, cache and refusal paths.
- Explain fixture ownership, worker reports and timing accountability.
- Describe explicit per-checkout Python `3.12` compatibility setup.
- Record real Windows, Python `3.12/3.13` and two-context consumer results.
- Preserve record-continuity evidence and explicit validation limitations.
```

##### Group 5: Step 7 implementation validation for step 7 shared_lifecycle_gate (round 1)

git add -A docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md

```log
docs(shared_lifecycle_gate): record step 7 validation

Why:

The final plan step needs a recorded assessment of acceptance behavior,
documentation, architecture, performance and feature integrity.

The validation plan now records the checked implementation and its evidence
without publishing private consumer details or unsupported platform claims.

What:

- Record step 7 implementation and the exact observed validation boundary.
- Link anonymous acceptance evidence and explain any outstanding gates.
```

Staged paths:

- `docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md`
- `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`
- `instructions/write-fast-python-tests.md`
- `tests/acceptance/shared_lifecycle/__init__.py`
- `tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py`
- `tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py`
- `tests/memory_filesystem.py`
- `tests/unit/tools/shared_lifecycle/inline_session.py`
- `tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py`
- `tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py`
- `tools/lifecycle_compatibility/behavior_runner.py`
- `tools/lifecycle_compatibility/behavior_scenarios.py`
- `tools/lifecycle_compatibility/runner.py`
- `tools/lifecycle_compatibility/scenarios.py`
- `tools/pytest_plugin_environment.py`
- `wiki/README.md`
- `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md`
- `wiki/how-to/enable-shared-lifecycle-gate.md`
- `wiki/how-to/enable-shared-process-audit.md`
- `wiki/how-to/register-groundhog-in-a-project.md`
- `wiki/how-to/set-test-lifecycle-limits.md`
- `wiki/how-to/validate-shared-pytest-compatibility.md`
- `wiki/reference/ghog-commands-and-exit-codes.md`
- `wiki/reference/test-lifecycle-limits.md`

### Human guidance and writer response for step 7 shared_lifecycle_gate (round 1)

Human guidance:

User instruction: "OK, when you have CPU under budget, do move on".
The last complete validation run has only wall-time lifecycle errors, with
each measured CPU value within its effective budget. Continue review without
another timing run, raised limits, weakened assertions or new exclusions.
Retain the non-green automated result and unproven coverage/speed claims.
This instruction does not authorize a commit or assert green release acceptance.

Writer response:

First implementation review of step 7. No earlier code-review feedback for
this step. The user's approved wording uses "enabled values that are not
booleans", "can be triggered" and "fixtures that were not requested".
The user explicitly instructed continuation for CPU-under-budget wall-only
failures. Automated coverage and speed acceptance remain unproven; preserve
that qualification in the assessment and documentation.

### Reviewer focus for step 7 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-1 -->

## Round 1 by reviewer - Step 7

- Recorded: 2026-11-10T22:12:47+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: baa1914e59993516d28d28a52b773e41db301585

Assessed index tree: baa1914e59993516d28d28a52b773e41db301585

### Implementation check for step 7 shared_lifecycle_gate (exchange 1) (round 1)

Result:

No. Step 7 has NOT been fully implemented.

Most of the step is in place and matches the plan. One plan obligation is
not met in a tracked form. The plan says to "Keep actual calling-shell
execution, with delayed expansion off and on, in Step 7's existing acceptance
harness" (Step 4 analysis). It also says to "Complete corresponding executable
scenarios for shell/process/xdist behavior that the audited suite cannot run"
(Step 7). The process and xdist scenarios are in the tracked harness. The real
shell probes are not. Two smaller items are listed with this one under the
unresolved findings.

What is in place and matches the plan:

- `tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py`
  (191 lines) runs `commands.run_tests_outcome` for all four selections. It
  uses real `prepare_environment`, the runner's child environment boundary,
  the real early loader, `--strict-config` and `--strict-markers`, a module
  fixture with a finalizer, and unused test and fixture permissions. It
  checks the summary counts, the two `WARNING unused` lines, the record write
  only when `lifecycle` is selected, a proven CPU at or below 0.1 s, the bound
  root and policy directory, the shared root kept off `PYTHONPATH`, and an
  unchanged parent environment. The consumer `tools` and `tests` packages raise
  if imported, so the in-process journey cannot pick them up by accident.
  `PreparedStartup` carries the documented plugin-manager guard.
- `behavior_scenarios.cases()` now has 25 cases. The new ones are the four
  prepared selections, `guard-late` (consumer guard first, gate loaded later
  through `pytest_plugins`), `prepared-explicit`, `workers-aggregate`,
  `workers-fixtures` (four parameters across two workers) and
  `gate-process-only`. `write_consumer_packages` adds consumer-owned `tools`
  and `tests` packages to every case, with a generated test that checks their
  identity in the child. `behavior_runner.run_case` now calls the real
  `prepare_environment` instead of setting the three variables by hand, and
  distinguishes no preparation (`None`) from an empty selection.
- The requestor's resolved walk log, which I saved before my own runs, shows
  the fresh 3.12 preflight with all 25 `Compatibility <case>: passed` lines
  before `check`.
- `tools/pytest_plugin_environment.py` accepts a user-local cache when the
  caller is a drive root, and still refuses a cache equal to the project, a
  cache under an ordinary project, and one under the shared checkout. The
  new `test_drive_root_preserves_user_cache` covers it.
- `runner.run_smoke` barrier children now disable unrelated built-in plugins
  and use `--assert=plain`. The barrier test uses only an autouse fixture,
  collection hooks, xdist and the audit, so its verdict is unchanged. The empty
  process probes add `-S`, and their 5 s timeout is unchanged.
- The three new how-to guides and the updated wiki pages cover the plan's
  documentation list. That includes the exact guard, loading order and
  precedence, the hazard of older unguarded registration, cache verification
  and explicit cleanup, stale-shell refusal and exit 4, fixture dictionary,
  thread and token scope, finalizers, credit, timing accountability, and
  Q03=C1 and Q04=D1 setup. I checked the "missing `enabled` key disables it"
  wording against `compatibility_preflight._enabled`, and they agree.
- `docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md` maps all
  sixteen criteria and the design cases. It keeps consumer identity and paths
  private, keeps Linux and macOS unvalidated, and records the declaration scan
  and record continuity (5,892 proofs kept, 345 added).

Human guidance: the request quotes the user: "OK, when you have CPU under
budget, do move on". I checked the saved log of the walk that ended at
2026-11-10T21:44:10+01:00. All 11 errors are lifecycle wall overruns: wall
1.029650 to 6.201089 s against 1.000 s. CPU ranges from 0.015625 to
0.156250 s, under the 0.250 s band. None of the 11 tests is in a Step 7 file.
In line with the guidance, I treat them as disclosed rather than as findings.
I ran no timing walk, and I assessed coverage statically. The guidance does
not cover the shell-harness gap, the transcript lint failure or the
validation rows.

Static coverage: the configured source is `tools` at 100%. Each new `tools`
line runs in tests:

- The drive-root condition runs in the new regression and the existing
  preparation tests.
- Both arms of `if case.prepared is not None` run in the parametrized
  behavior cases.
- `write_consumer_packages` runs in every behavior case.
- The barrier argument list runs in the existing runner tests.
- `windows_caller` runs in the acceptance test.

I found no gap. Changed Python files are 1 to 350 lines, under the 650-line
limit.

Validation plan effects:

No reviewer edit. The writer's Step 7 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 7 has been fully implemented.`, which this assessment does not
confirm because of the shell-harness gap (first finding). The rows follow the
template. Their walk figures match the saved walk log: 6,221 lifecycles, 11
wall-only errors, CPU 0.015625 to 0.156250 s, wall 1.029650 to 6.201089 s, and
withheld coverage and speed verdicts. They also say plainly that green release
acceptance is not established. The implemented row does not record the
file-list departures (third finding). The coverage row's statement that the
Windows caller helper has "executable probe evidence" rests on the untracked
scratch driver.

The document-level line changes to `Yes, it is implemented.`, qualified by the
unproven coverage and speed acceptance. That line should follow the Step 7
verdict after rework. Reviewer mode completed no umbrella row, and the effort
has none.

### Pre-repair mandatory checks and coverage for step 7 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `baa1914e59993516d28d28a52b773e41db301585`, which equals the
request-time tree.

Requestor evidence, not repeated: the resolved
`ghog day --full=speed --whole-suite`, run through this worktree's own
launcher, ended at 2026-11-10T21:44:10+01:00 with exit 2 after 18m 00.2s. The
fresh 3.12 preflight passed all 25 cases. Its check (10m 06.7s) and affected
stages passed. The full stage reported 11 wall-only lifecycle errors and
withheld coverage, outliers and exclusions. I saved that log before my own
runs as `.reviews/a.shared_lifecycle_gate.step7.tmp.r1.rv-requestor-day.log`.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` and `bin\ghog.bat`, with the guard cleared and
`SWITCHPY_CHOICE=local`. Each run passed the log-freshness check:

- `ghog check` ended at 2026-11-10T22:03:44+01:00 with `exit=1` after
  2m 04.4s. ty, pyright, ruff, the static entry check (`Python 3.10
  syntax/refusal boundary and PEP 701 negative control passed`), radon,
  vulture, the 650-line big-file check, shellcheck and the EOF check passed.
  Markdown failed only with `MD050` at lines 6272 and 6273 of the unstaged
  review transcript (second finding). No staged Markdown file failed.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-10T22:04:41+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's walk, so 0 tests ran.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran.

### Resolved validation set and sources for step 7 shared_lifecycle_gate (exchange 1) (round 1)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` and `plan` sources. That is the built-in default, completed with
the bound whole-suite selector, and the plan's own `scope day --full=speed`
final acceptance. The repository has no `.review-validation` declaration.

The requestor owns this set. The reviewer did not run it. Its recorded result
ended at 2026-11-10T21:44:10+01:00:
`ghog day done fail=11 warn=0 xfail=0 cov=withheld outliers=withheld excluded=withheld exit=2 full=speed src=param proof=none reused=none scope=whole`.
All 11 failures are lifecycle wall overruns with CPU under the band, in tests
outside Step 7. The literal `Human guidance:` block authorizes continuing
without another timing run, and the result stays recorded as non-green.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 7 shared_lifecycle_gate (exchange 1) (round 1)

No drift. There is no `.review-validation` declaration, and the bound scope is
`whole` (fingerprint `686958cd`). The staged change adds no validation command
to the plan or the validation plan. The resolver inputs therefore give the same
single command, `ghog day --full=speed --whole-suite`, from `project` and
`plan`. Neither direction adds or drops a command.

### Repository state around validation for step 7 shared_lifecycle_gate (exchange 1) (round 1)

The validation path set holds the 24 staged paths, the implementation plan
and the root `a.ghog.log` that the reviewer evidence commands write. It was
captured before assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged. The request
  says `Umbrella draft: none`.
- After assessment, the live index tree is still
  `baa1914e59993516d28d28a52b773e41db301585`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended to it, and the requestor's residual commit owns it. It fails the
  Markdown check (second finding).

### Repair inventory for step 7 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 7 shared_lifecycle_gate (exchange 1) (round 1)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 24 staged paths and the same five ordered groups as the request
evidence:

1. `fix(pytest): preserve cache for drive-root callers`, 2 paths.
2. `test(pytest): expand executable compatibility cases`, 5 paths.
3. `test(pytest): join prepared consumer policies`, 5 paths.
4. `docs(pytest): document shared policy adoption`, 11 paths.
5. `docs(shared_lifecycle_gate): record step 7 validation`, 1 path.

Reviewer judgment on grouping and scope: membership and order are correct.

1. The drive-root preparation fix and its regression come first. That is a
   real production defect, and the later harness relies on it.
2. The executable harness changes are tooling that exists only to test, so
   `test` fits.
3. The in-process acceptance journey and its helper routing come next.
4. The guides and the acceptance record follow.
5. The validation record comes last.

The bodies match the staged changes, and no AI attribution trailer is present.

`a.commit` is accurate for the received state. The rework will need to add
the tracked shell harness and its tests, most likely to group 2, and update
that group's body.

### Findings and boundaries for step 7 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings:

- The real Windows shell probes are not in the tracked acceptance harness.
  The plan puts "actual calling-shell execution, with delayed expansion off
  and on" in "Step 7's existing acceptance harness" and asks for "executable
  scenarios for shell/process/xdist behavior". The eleven probes are driven by
  `.reviews/a.shared_lifecycle_gate.step7.tmp.shell-probes.py`, which is an
  ignored scratch script. Those probes cover delayed expansion on and off,
  punctuation and OEM non-ASCII paths, atomic refusal of an invalid selection
  and of an unrepresentable value, the drive root, concurrent transfer files
  and concurrent preparations. The tracked code holds only
  `scenarios.windows_caller()`, a six-line batch body. Its only tracked
  caller, `test_windows_probe_preserves_the_caller_boundary`, checks that text.
  Neither `runner --all`, `bin\lifecycle_compatibility.bat` nor the day and
  full preflight runs a shell probe: the resolved walk shows 25
  `Compatibility` lines and none for the shell. Acceptance row W lists the
  probes as a "repeatable source", but nothing in the repository can repeat
  them, and they are lost when the `.reviews` scratch is cleaned. A later
  change to `bin\prepare_pytest_plugins.bat` or `tools/pytest_plugin_shell.py`
  would not be caught.
- My `ghog check` is red: exit 1 at 2026-11-10T22:03:44+01:00. Only the
  Markdown step failed, with `MD050` (strong style) at lines 6272 and 6273 of
  the tracked transcript `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`.
  Those lines are the bare `git add -A` lines for the two new
  `tests/acceptance/shared_lifecycle/.../__init__.py` package markers. They
  came from the round 1 change-summary input,
  `.reviews/a.shared_lifecycle_gate.step7.tmp.r1.change-summary.md`, which
  puts `git add` lines outside any code span or fenced block. The exchange
  appended them to the transcript when the request was published at 21:53.
  The requestor's own `check` ran from 21:29 to 21:40, before that, so it
  could not see the failure. Earlier rounds kept these paths in code spans or
  fenced `group N path:` lines. The transcript is not staged, but it belongs to
  this step's residual review commit, and every `ghog check` on this
  worktree now fails until the lines are fixed.
- The Step 7 validation rows do not record the departures from the plan's
  file list, as the Step 6 rows do. Eight staged files are not named in
  Step 7's file list. `tools/pytest_plugin_environment.py` and
  `tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py`
  hold a production fix to Step 4 preparation.
  `tools/lifecycle_compatibility/behavior_runner.py`,
  `tools/lifecycle_compatibility/behavior_scenarios.py`,
  `tools/lifecycle_compatibility/runner.py` and
  `tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py`
  hold the behavior cases and barrier trims. `tests/memory_filesystem.py` and
  `tests/unit/tools/shared_lifecycle/inline_session.py` are support changes.
  The prose mentions the drive-root fix and the harness growth. No row names
  these files as departures or says why the work landed there.

Boundary-crossing work: None.

### Writer instructions for step 7 shared_lifecycle_gate (exchange 1) (round 1)

1. Shell harness: move the shell probe driver into the tracked executable
   compatibility harness, for example a `tools/lifecycle_compatibility`
   module beside `scenarios.windows_caller`. Keep the same eleven checks:
   delayed expansion off and on, punctuation and OEM non-ASCII paths, atomic
   refusal of an invalid selection and of an unrepresentable value, the drive
   root, concurrent transfer files and concurrent preparations. Run it from the
   harness on Windows, at least in `runner --all` and through
   `bin\lifecycle_compatibility.bat --evidence`. On another platform, report it
   as not run rather than passed. You choose whether the day and full preflight
   also run it. Keep its process starts out of the audited suite. Cover its
   decision logic with process-free unit tests through the existing virtual
   storage boundary, so `tools` coverage stays at 100%. Rerun the real 3.12 and
   3.13 harness. Point acceptance row W and the Step 7 validation rows at the
   tracked entry, and keep its outputs private. Remove the claim that the
   scratch script is repeatable evidence.
2. Transcript lint: do not disable `MD050`. Before the residual transcript
   commit, make `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`
   pass the Markdown check again. Lines 6272 and 6273 need their package-marker
   paths in code spans, through whichever route your requestor instruction
   allows for the transcript. The reviewer does not edit it. In every later
   request input, put `git add` lines inside a fenced block or code spans, as
   earlier rounds did. Confirm with `ghog check`.
3. Validation rows: add a "File-list deviations" bullet to the Step 7 "What
   was implemented" row, as Step 6 has. Name the eight files that are not in
   Step 7's list, listed under the unresolved findings. Say why each landed
   there. For example, the drive-root shell probe exposed the Step 4 cache
   boundary, which is a production `fix`. The harness split from Step 6 put the
   cases in `behavior_scenarios.py` and `behavior_runner.py`. `runner.py` holds
   the barrier startup trims, and the two test helpers support the in-process
   journey. Name any file that item 1 adds as well.
4. Update `a.commit` for any file that items 1 and 3 add. The new shell
   module and its tests most likely belong in group 2.

Non-blocking notes:

- `behavior_runner.run_case` now prepares with the default user-local cache,
  so each real harness run can publish an immutable loader entry there. The
  unit test redirects it. That fits the documented explicit cleanup. Mention
  it in the compatibility guide if you want the effect to be visible.

### Decision rationale for step 7 shared_lifecycle_gate (exchange 1) (round 1)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 7,
  round 1, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `baa1914e` all agree with the live exchange and index.
- Completeness: fail. The plan's calling-shell execution scenarios are not in
  the tracked acceptance harness. They exist only as an ignored scratch
  driver (first finding).
- Validation and coverage: fail. The reviewer `ghog check` is red with `MD050`
  in the review transcript (second finding). `ghog affected --no-cov` exited 0,
  and static reading finds no coverage gap. Under the literal human guidance,
  the 11 wall-only, CPU-under-budget errors of the resolved walk are disclosed
  rather than counted as findings. That walk stays non-green, and its coverage
  and speed verdicts stay unproven.
- Staged attribution: pass. All 24 staged paths are writer work in five
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: fail. Three findings are unresolved. The third concerns the
  validation rows.
- `a.commit`: pass for the received state. The independent checker is valid
  and ready with no diagnostics.

This round made no repair, substantive or polishing. The literal
`Human guidance:` block was applied as written. It directs continuation
without a timing run, raised limits, weakened assertions or new exclusions. It
instructs no repair, and it does not override the completeness or
validation findings.

Disposition: changes-requested.

### Final reviewer decision for step 7 shared_lifecycle_gate (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-7-round-1 -->

## Round 2 by requestor - Step 7

- Recorded: 2026-11-10T23:04:33+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 7
- Outcome: request

### Review identity for step 7 shared_lifecycle_gate (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 7
Review round: 2

### Code review evidence for step 7 shared_lifecycle_gate (round 2)

request_index_tree: 3a0d82f2e1a37877f8fc396217c52fa58ed2411f
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project, plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "none", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(pytest): preserve cache for drive-root callers
group 1 path: tools/pytest_plugin_environment.py
group 1 path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
group 2: test(pytest): expand executable compatibility cases
group 2 path: tools/lifecycle_compatibility/behavior_runner.py
group 2 path: tools/lifecycle_compatibility/behavior_scenarios.py
group 2 path: tools/lifecycle_compatibility/runner.py
group 2 path: tools/lifecycle_compatibility/scenarios.py
group 2 path: tools/lifecycle_compatibility/shell_scenarios.py
group 2 path: tools/lifecycle_compatibility/shell_runner.py
group 2 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
group 2 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_shell_runner_tdd.py
group 3: test(pytest): join prepared consumer policies
group 3 path: tests/memory_filesystem.py
group 3 path: tests/unit/tools/shared_lifecycle/inline_session.py
group 3 path: tests/acceptance/shared_lifecycle/__init__.py
group 3 path: tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py
group 3 path: tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py
group 4: docs(pytest): document shared policy adoption
group 4 path: instructions/write-fast-python-tests.md
group 4 path: wiki/README.md
group 4 path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
group 4 path: wiki/how-to/register-groundhog-in-a-project.md
group 4 path: wiki/how-to/set-test-lifecycle-limits.md
group 4 path: wiki/reference/ghog-commands-and-exit-codes.md
group 4 path: wiki/reference/test-lifecycle-limits.md
group 4 path: wiki/how-to/enable-shared-lifecycle-gate.md
group 4 path: wiki/how-to/enable-shared-process-audit.md
group 4 path: wiki/how-to/validate-shared-pytest-compatibility.md
group 4 path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
group 5: docs(shared_lifecycle_gate): record step 7 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: instructions/write-fast-python-tests.md
staged path: tests/acceptance/shared_lifecycle/__init__.py
staged path: tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py
staged path: tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/shared_lifecycle/inline_session.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_shell_runner_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
staged path: tools/lifecycle_compatibility/behavior_runner.py
staged path: tools/lifecycle_compatibility/behavior_scenarios.py
staged path: tools/lifecycle_compatibility/runner.py
staged path: tools/lifecycle_compatibility/scenarios.py
staged path: tools/lifecycle_compatibility/shell_runner.py
staged path: tools/lifecycle_compatibility/shell_scenarios.py
staged path: tools/pytest_plugin_environment.py
staged path: wiki/README.md
staged path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
staged path: wiki/how-to/enable-shared-lifecycle-gate.md
staged path: wiki/how-to/enable-shared-process-audit.md
staged path: wiki/how-to/register-groundhog-in-a-project.md
staged path: wiki/how-to/set-test-lifecycle-limits.md
staged path: wiki/how-to/validate-shared-pytest-compatibility.md
staged path: wiki/reference/ghog-commands-and-exit-codes.md
staged path: wiki/reference/test-lifecycle-limits.md
```

### Validation scope for step 7 shared_lifecycle_gate (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 7 shared_lifecycle_gate (round 2)

Yes. Step 7 is implemented under the user's explicit CPU-under-budget
continuation instruction. All three round 1 findings have writer-owned
repairs. The shell checks are tracked, executable and covered through virtual
storage and fake process transport; the validation plan names the file-list
deviations; the transcript formatting and fenced change summary address MD050.

Actual Python 3.12.15 and 3.13.9 each passed all 36 executable checks, including
the eleven shell probes, in the saved round 2 logs. The focused acceptance
journey previously passed all five tests; the anonymous consumer passed its
23 tests in each activation context with unchanged files and restored state.

The resolved validation set remains `ghog day --full=speed --whole-suite`,
from project and plan sources. Its last complete run ended at
2026-11-10T21:44:10+01:00 with exit 2 after 18m00.2s. It measured 6,221
lifecycles with exactly eleven wall-only errors: CPU 0.015625-0.156250s under
the effective 0.250s ceiling, wall 1.029650-6.201089s against 1.000s. Fresh
preflight and static checks passed then, with no assertion failures, warnings
or xfails. Coverage, speed/outlier and exclusion verdicts were withheld.

Human guidance authorizes review continuation without another timing walk.
Round 2 uses a fresh check-and-affected day for the changed shell-harness code
and retains the earlier non-green full-speed evidence. Its saved output is
`.reviews/a.shared_lifecycle_gate.step7.tmp.r2.validation.log`; this functional
and static run passed with exit 0 at 2026-11-10T23:03:29+01:00 in 2m50.6s,
with zero failures, warnings or xfails and confirmed freshness. It is not a
full-speed or coverage proof.

The tools coverage target remains 100%. Static inspection of the new shell
logic and its unit tests found no missing branch; measured whole-suite
coverage remains unproven. Architecture, feature-integrity and file-size
assessments remain as recorded in the validation plan. No budget, permission,
assertion or exclusion was weakened. The five-group commit plan includes all
27 staged paths; the transcript remains outside the reviewed index for its
residual commit. Review and commit authorization are still pending.

### Implementation report for step 7 shared_lifecycle_gate (round 2)

Step 7 joins real environment preparation, the groundhog child boundary,
canonical loading, strict configuration, fixture cleanup, unused declarations
and selected record writes in process. The executable harness covers prepared
selections, consumer package identity, guarded registration, duplicate loading,
gate-only processes and distributed fixture aggregation.

The round 1 repair adds tracked shell_scenarios.py and shell_runner.py, with
eleven real Windows caller contracts and process-free decision/transport unit
tests. The full executable entry retains these contracts across review scratch
cleanup. Non-Windows hosts report the Windows checks as not run. Typed snapshot
validation rejects malformed external JSON, and bounded child cleanup remains
unchanged. The new functions remain below the 650-line file limit.

The drive-root preparation fix keeps the user-local cache valid without
permitting cache storage in either ordinary checkout. The consumer trial
passed 23 existing tests in both transient prepared-shell and real groundhog
child contexts, with files unchanged and transient state restored. Record
comparison preserved all 5,892 earlier eligible proofs, adding 345, with no
lost nodes, changed exceptions or other record fields.

Adoption guides cover independent opt-in, fixture/process ownership, cache
maintenance and explicit compatibility provisioning. Anonymous acceptance
evidence maps the requirement/design cases and preserves platform and proof
limits. Validation names each file-list deviation. The transcript lint repair
keeps command paths in code spans; round 2 fences the complete commit plan.

No accepted exclusion was introduced. The saved full-speed run withheld its
coverage, outlier and exclusion verdicts after eleven wall-only errors whose
CPU stayed under budget. No measured 100% coverage or green release acceptance
is claimed. Linux and macOS remain unvalidated.

Writer notes: `.reviews/a.shared_lifecycle_gate.step7.journal.md` and
`.reviews/a.shared_lifecycle_gate.step7.handoff.md`.

### Change summary for step 7 shared_lifecycle_gate (round 2)

Round 2 retains the five topic groups and all 27 staged paths. Readiness checker: valid, ready true, no diagnostics.

Staged paths:

```text
docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
instructions/write-fast-python-tests.md
tests/acceptance/shared_lifecycle/__init__.py
tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py
tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py
tests/memory_filesystem.py
tests/unit/tools/shared_lifecycle/inline_session.py
tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
tests/unit/tools/shared_lifecycle/test_compatibility/test_shell_runner_tdd.py
tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py
tools/lifecycle_compatibility/behavior_runner.py
tools/lifecycle_compatibility/behavior_scenarios.py
tools/lifecycle_compatibility/runner.py
tools/lifecycle_compatibility/scenarios.py
tools/lifecycle_compatibility/shell_runner.py
tools/lifecycle_compatibility/shell_scenarios.py
tools/pytest_plugin_environment.py
wiki/README.md
wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
wiki/how-to/enable-shared-lifecycle-gate.md
wiki/how-to/enable-shared-process-audit.md
wiki/how-to/register-groundhog-in-a-project.md
wiki/how-to/set-test-lifecycle-limits.md
wiki/how-to/validate-shared-pytest-compatibility.md
wiki/reference/ghog-commands-and-exit-codes.md
wiki/reference/test-lifecycle-limits.md
```

Complete reviewed root a.commit:

````text
# Grouping commits by topic

## Group 1: Drive-root preparation cache

git add -A tools/pytest_plugin_environment.py
git add -A tests/unit/tools/shared_lifecycle/test_preparation/test_preparation_tdd.py

```log
fix(pytest): preserve cache for drive-root callers

Why:

A drive-root consumer rejected the normal user-local loader cache because every
path on the drive appeared to be inside the project.

Preparation now distinguishes a filesystem root from a checkout directory while
retaining the cache boundary for ordinary projects and shared sources.

What:

- Accept user-local cache storage when the caller is a drive root.
- Retain rejection of the project root itself and shared-checkout storage.
- Cover drive-root binding and immutable cache publication in a regression.
```

## Group 2: Executable compatibility acceptance

git add -A tools/lifecycle_compatibility/behavior_runner.py
git add -A tools/lifecycle_compatibility/behavior_scenarios.py
git add -A tools/lifecycle_compatibility/runner.py
git add -A tools/lifecycle_compatibility/scenarios.py

git add -A tools/lifecycle_compatibility/shell_scenarios.py

git add -A tools/lifecycle_compatibility/shell_runner.py
git add -A tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py

git add -A tests/unit/tools/shared_lifecycle/test_compatibility/test_shell_runner_tdd.py

```log
test(pytest): expand executable compatibility cases

Why:

Release acceptance needs actual prepared selection, consumer package identity
and distributed fixture usage beyond the individual policy units.

The separate executable matrix now checks those contracts on real runtimes and
retains bounded failure cleanup without carrying-suite process grants.

What:

- Exercise all prepared selections and guarded settings in both orders.
- Import consumer-owned tools and tests packages in isolated children.
- Check duplicate loading, gate-only processes and worker aggregation.
- Run eleven Windows shell checks in the full executable harness.
- Cover shell decisions with virtual storage and fake process transport.
- Trim unrelated child startup while preserving the actual policy work.
- Retain all existing deadlines, policy limits and evidence assertions.
```

## Group 3: Integrated prepared-consumer acceptance

git add -A tests/memory_filesystem.py
git add -A tests/unit/tools/shared_lifecycle/inline_session.py
git add -A tests/acceptance/shared_lifecycle/__init__.py
git add -A tests/acceptance/shared_lifecycle/test_shared_plugins/__init__.py
git add -A tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py

```log
test(pytest): join prepared consumer policies

Why:

Separate policy tests do not prove that preparation, groundhog child isolation,
canonical loading and record writes work together.

An in-process consumer journey checks all four selections with strict settings,
fixture cleanup, unused permissions and parent-state restoration.

What:

- Join the real environment builder, runner boundary and pytest hooks.
- Verify summary counts, unused declarations and selected record writes.
- Route generated resources through the existing memory filesystem.
- Keep real conftest discovery and process checks in the executable matrix.
```

## Group 4: Shared policy adoption and acceptance evidence

git add -A instructions/write-fast-python-tests.md
git add -A wiki/README.md
git add -A wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
git add -A wiki/how-to/register-groundhog-in-a-project.md
git add -A wiki/how-to/set-test-lifecycle-limits.md
git add -A wiki/reference/ghog-commands-and-exit-codes.md
git add -A wiki/reference/test-lifecycle-limits.md
git add -A wiki/how-to/enable-shared-lifecycle-gate.md
git add -A wiki/how-to/enable-shared-process-audit.md
git add -A wiki/how-to/validate-shared-pytest-compatibility.md
git add -A docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md

```log
docs(pytest): document shared policy adoption

Why:

Consumers need the supported opt-in, settings, permission and compatibility
routes together with evidence that matches the platforms actually tested.

The wiki explains independent activation and operation scope, and anonymous
acceptance evidence maps every requirement and design case to a check.

What:

- Document shell preparation, strict configuration, cache and refusal paths.
- Explain fixture ownership, worker reports and timing accountability.
- Describe explicit per-checkout Python `3.12` compatibility setup.
- Record real Windows, Python `3.12/3.13` and two-context consumer results.
- Preserve record-continuity evidence and explicit validation limitations.
```

## Group 5: Step 7 implementation validation

git add -A docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md

```log
docs(shared_lifecycle_gate): record step 7 validation

Why:

The final plan step needs a recorded assessment of acceptance behavior,
documentation, architecture, performance and feature integrity.

The validation plan now records the checked implementation and its evidence
without publishing private consumer details or unsupported platform claims.

What:

- Record step 7 implementation and the exact observed validation boundary.
- Link anonymous acceptance evidence and explain any outstanding gates.
```
````

The versioned transcript is deliberately unstaged for the authorized residual batch. Its MD050 repair is a formatting-only change. All substantive round 1 findings are accepted; no reviewer repair was reversed.

### Human guidance and writer response for step 7 shared_lifecycle_gate (round 2)

Human guidance:

User instruction: "OK, when you have CPU under budget, do move on".
The last complete validation run has only wall-time lifecycle errors, with
each measured CPU value within its effective budget. Continue review without
another timing run, raised limits, weakened assertions or new exclusions.
Retain the non-green automated result and unproven coverage/speed claims.
This instruction does not authorize a commit or assert green release acceptance.

Writer response:

Accepted all three round 1 findings; no disagreement and no reviewer repair
was reversed. The reviewer made no tracked edits in round 1.

The eleven real shell probes now live in tracked shell_scenarios.py and
shell_runner.py, invoked by runner --all and lifecycle_compatibility.bat
--evidence. The Windows-only contracts cover both delayed-expansion modes,
punctuation and OEM paths, invalid-selection and encoding refusal, drive-root
callers, independent concurrent transfer files and concurrent preparations.
Other platforms report these cases as not run. Process-free unit tests use
the existing virtual filesystem and replace process/thread transport.

Both real Python 3.12.15 and 3.13.9 runs passed all 36 checks, including the
eleven tracked shell probes. Private evidence is retained under the step's
round 2 prefix. Acceptance row W and the validation plan now name the tracked
entry; the compatibility guide explains retaining private shell evidence and
the normal user-local immutable cache side effect.

The transcript's package-marker paths now use code spans, without disabling
MD050. This request's change summary fences the complete commit plan so its
git commands cannot create the same lint failure.

The validation plan names all eight original file-list deviations, why each
belongs here, and the three newly tracked shell-harness/test files. Root
a.commit retains its five groups, adding those three paths to group 2 and
describing their shell checks and virtual transport coverage.

The user's CPU-under-budget continuation remains in force. The disclosed full
speed walk stays non-green; no timing run, limit change, assertion reduction,
process permission or exclusion was added to turn that result green.

### Reviewer focus for step 7 shared_lifecycle_gate (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-2 -->

## Round 2 by reviewer - Step 7

- Recorded: 2026-11-10T23:11:31+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 shared_lifecycle_gate (exchange 1) (round 2)

Baseline index tree: 3a0d82f2e1a37877f8fc396217c52fa58ed2411f

Assessed index tree: 3a0d82f2e1a37877f8fc396217c52fa58ed2411f

### Implementation check for step 7 shared_lifecycle_gate (exchange 1) (round 2)

Result:

Yes. Step 7 has been fully implemented, under the literal human guidance that
accepts a CPU-under-budget, wall-only result in place of a green
full-speed walk.

All three round 1 findings are fixed:

- The shell probes are tracked now. `tools/lifecycle_compatibility/shell_scenarios.py`
  (88 lines) names the ten caller cases, all of which run through `cmd`. They
  cover preserved values, atomic invalid-selection and unrepresentable-value
  refusal, and the drive root, each with delayed expansion off and on. Two more
  cases run concurrently. `verdict` checks both exit
  observations and every owned key. A refusal must leave all owned values
  unchanged, and a success must bind the root, keep the selection, set the
  policy directory and keep both punctuation suffixes. `read_snapshot` rejects
  a non-object, an incomplete key set and non-string values.
  `tools/lifecycle_compatibility/shell_runner.py` (107 lines) runs the cases
  through `cmd /d /v:<mode> /c` with a 30 s bound and `kill_tree` on timeout.
  It adds the eleventh check, four concurrent transfer files that must be
  distinct and complete, and removes them afterwards. Off Windows it returns
  one `not run` result.
- `runner._all_cases` appends those results, so `runner --all`,
  `bin\lifecycle_compatibility.bat --evidence` and the automatic day and full
  preflight all run them. `_report` prints `not run` for `passed: None`, and
  `main` fails only on `passed: False`. `scenarios.windows_caller` now has a
  tracked production caller.
- I read both real `summary.json` files under the round 2 private evidence
  prefix. Python 3.12.15 and 3.13.9, with pytest 9.1.0 and xdist 3.8.0, each
  pass 36 of 36 checks. The requestor's 23:03:29 day log shows the fresh 3.12
  preflight with all 36 `Compatibility` lines, the eleven shell checks
  included.
- The two transcript lines now use code spans, and this round's change summary
  fences the whole `a.commit`.
- The Step 7 "What was implemented" row has a "File-list deviations" bullet.
  It names the eight original files and the three new shell files and says
  why each one is there. Acceptance row W, the compatibility guide and the
  coverage row point at the tracked entry. The guide also states the
  user-local cache side effect.

The round 1 assessment of everything else still holds: the in-process
acceptance journey, the 25 behavior cases, the drive-root preparation fix, the
guides and the acceptance mapping.

Human guidance: the request quotes the user: "OK, when you have CPU under
budget, do move on". The last full-speed walk ended at
2026-11-10T21:44:10+01:00 with exit 2. All 11 of its errors are wall
overruns (1.029650 to 6.201089 s against 1.000 s) with CPU from 0.015625 to
0.156250 s, under the 0.250 s band, in tests outside Step 7. I treat that
result as disclosed and non-green, not as a finding. I ran no timing walk, and
I assessed coverage statically.

Static coverage (`tools` at 100%, line coverage) of the new shell lines:

- `test_shell_runner_tdd.py` covers every `ShellCase` and its verdict, a fail
  for each owned key and both exit observations, a partial refusal, and three
  malformed snapshots.
- It also covers the success, missing-snapshot, timeout and bad-exit
  transport, the caller environment, a complete and a corrupt transfer, and
  both platform branches of `run_all` (with a patched `GetOEMCP` on Windows).
- `test_runner_all_mode_validates_versions_and_aggregates` covers the
  `not run` aggregation and exit 0.

The tests use the virtual storage boundary and an inline pool, so they start
no process or thread. I found no gap. Changed Python files are 1 to 350
lines, under the 650-line limit.

Validation plan effects:

No reviewer edit. The writer's Step 7 rows in
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md` say
`Yes. Step 7 has been fully implemented.`, which this assessment confirms
under the literal human guidance. The new "File-list deviations" bullet
names all eight original departures and the three new shell-harness files,
with a reason for each. The coverage row now ties the Windows caller helper to
the tracked `shell_runner` entry. The walk figures still match the saved
21:44:10 log, and the rows still say plainly that coverage, speed and green
release acceptance remain unproven.

The document-level line `Yes, it is implemented.` keeps the same
qualification. Reviewer mode completed no umbrella row, and the effort has
none.

### Pre-repair mandatory checks and coverage for step 7 shared_lifecycle_gate (exchange 1) (round 2)

No repair was made. The pre-repair and assessed states are therefore the same
index tree, `3a0d82f2e1a37877f8fc396217c52fa58ed2411f`, which equals the
request-time tree.

Requestor evidence, not repeated: the round 2 default day ended at
2026-11-10T23:03:29+01:00 with exit 0. It ran the fresh 3.12 preflight with all
36 checks, then check and affected. The real 3.12.15 and 3.13.9 summaries each
record 36 of 36 passes. The last full-speed walk, which ended at 21:44:10, is
the disclosed non-green result under the human guidance.

Reviewer evidence. Each command ran once from the project root through the
worktree's `.\senv.bat` and `bin\ghog.bat`, with the guard cleared and
`SWITCHPY_CHOICE=local`. Each run passed the log-freshness check:

- `ghog check` ended at 2026-11-10T23:08:54+01:00 with `exit=0` after
  1m 30.2s. Every step passed: ty, pyright, ruff, the static entry check
  (`Python 3.10 syntax/refusal boundary and PEP 701 negative control passed`),
  radon, vulture, the 650-line big-file check, Markdown (the repaired review
  transcript included), shellcheck and the EOF check.
- `ghog affected --no-cov --scope-file=.reviews/a.review-scope.code.v0.14.0.shared_lifecycle_gate.json`
  ended at 2026-11-10T23:09:47+01:00 with `exit=0`. Testmon found nothing
  affected since the requestor's 23:03 run, so 0 tests ran.

Coverage was assessed statically, and no `ghog day` or `ghog full` ran.

### Resolved validation set and sources for step 7 shared_lifecycle_gate (exchange 1) (round 2)

The request carries one command, `ghog day --full=speed --whole-suite`, from
the `project` and `plan` sources. The repository has no `.review-validation`
declaration.

The requestor owns this set. The reviewer did not run it. Its last complete
result ended at 2026-11-10T21:44:10+01:00:
`ghog day done fail=11 warn=0 xfail=0 cov=withheld outliers=withheld excluded=withheld exit=2 full=speed src=param proof=none reused=none scope=whole`.
All 11 failures are lifecycle wall overruns with CPU under the band, in tests
outside Step 7. The literal `Human guidance:` block authorizes continuing
without another timing run, and that result stays recorded as non-green.

For the round 2 changes, the requestor ran a default day, which runs check
and affected but not full. It ended at 2026-11-10T23:03:29+01:00:
`ghog day done fail=0 warn=0 xfail=0 cov=skipped outliers=skipped excluded=skipped exit=0 full=none src=default proof=none reused=none scope=whole`.
That run includes the fresh 3.12 preflight with all 36 checks. It is not a
coverage or speed proof. I saved its log before my own runs as
`.reviews/a.shared_lifecycle_gate.step7.tmp.r2.rv-requestor-check-affected.log`.

Exchange status binds the round to scope `whole` with fingerprint `686958cd`,
and the reviewer used that `paths.scope` capture.

### Resolver drift and direction for step 7 shared_lifecycle_gate (exchange 1) (round 2)

No drift. There is no `.review-validation` declaration, and the bound scope is
`whole` (fingerprint `686958cd`). The staged change adds no validation command
to the plan or the validation plan. The resolver inputs therefore give the same
single command, `ghog day --full=speed --whole-suite`, from `project` and
`plan`. Neither direction adds or drops a command.

### Repository state around validation for step 7 shared_lifecycle_gate (exchange 1) (round 2)

The validation path set holds the 27 staged paths, the implementation plan
and the root `a.ghog.log` that the reviewer evidence commands write. It was
captured before assessment and again after both ghog commands.

- `validation-state compare` reported `acceptable: true`. No tracked or
  untracked path changed, and one ignored path changed (`a.ghog.log`).
- `umbrella-digest compare` reported not applicable and unchanged. The request
  says `Umbrella draft: none`.
- After assessment, the live index tree is still
  `3a0d82f2e1a37877f8fc396217c52fa58ed2411f`.
- The only unstaged change is the versioned review transcript
  `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`. The exchange
  appended to it, and the requestor's residual commit owns it. It passes the
  Markdown check now.

### Repair inventory for step 7 shared_lifecycle_gate (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 7 shared_lifecycle_gate (exchange 1) (round 2)

An independent `commit-plan-check.bat --format json` rerun on the received
state exited 0 with `state: valid`, `ready: true` and no diagnostics. It listed
the same 27 staged paths and the same five ordered groups as the request
evidence:

1. `fix(pytest): preserve cache for drive-root callers`, 2 paths.
2. `test(pytest): expand executable compatibility cases`, 8 paths.
3. `test(pytest): join prepared consumer policies`, 5 paths.
4. `docs(pytest): document shared policy adoption`, 11 paths.
5. `docs(shared_lifecycle_gate): record step 7 validation`, 1 path.

Reviewer judgment on grouping and scope: membership and order are correct.
The new shell harness and its unit tests belong with the other executable
compatibility tooling in group 2, and that group's body now describes the
eleven shell checks and their virtual transport coverage. The bodies match
the staged changes, and no AI attribution trailer is present. The blank lines
between some group 2 `git add -A` lines are cosmetic.

`a.commit` is accurate. The unstaged review transcript stays outside it for
the requestor's residual commit.

### Findings and boundaries for step 7 shared_lifecycle_gate (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 7 shared_lifecycle_gate (exchange 1) (round 2)

No further implementation work is requested for Step 7.

Non-blocking note: group 2 of `a.commit` has blank lines between some of its
`git add -A` lines. The checker accepts it and membership is correct, so
tidying it is optional.

### Decision rationale for step 7 shared_lifecycle_gate (exchange 1) (round 2)

The six readiness-floor results:

- Identity: pass. The envelope, the readable identity, the plan, step 7,
  round 2, occurrence 1, `Umbrella draft: none` and the request-time index tree
  `3a0d82f2` all agree with the live exchange and index.
- Completeness: pass. Every Step 7 obligation is implemented. The calling-shell
  contracts now run from the tracked harness and its preflight, and the real
  3.12 and 3.13 runs pass all 36 checks.
- Validation and coverage: pass under the literal human guidance. Reviewer
  `ghog check` and `ghog affected --no-cov` both exited 0, and static reading
  finds no coverage gap. The last full-speed walk stays disclosed as non-green:
  11 wall-only errors with CPU under budget, and coverage and speed verdicts
  withheld. The guidance accepts that for continuation. It does not turn the
  walk green.
- Staged attribution: pass. All 27 staged paths are writer work in five
  accurate groups. The reviewer staged nothing and edited nothing tracked.
- Findings: pass. All three round 1 findings are fixed, and no new finding
  remains.
- `a.commit`: pass. The independent checker is valid and ready with no
  diagnostics, and the grouping and bodies are accurate.

This round made no repair, substantive or polishing. The literal
`Human guidance:` block was applied as written: no timing run, no raised
limits, no weakened assertions, no new exclusions, and the non-green result
and unproven coverage and speed claims retained.

Disposition: commit-ready. This is an advisory recommendation and does not
authorize a commit.

### Final reviewer decision for step 7 shared_lifecycle_gate (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-7-round-2 -->

## Round 2 by human - Step 7 - human-confirmation

- Recorded: 2026-11-11T00:01:33+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 7
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 8

- Recorded: 2026-11-11T14:03:13+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 8
- Outcome: request

### Review identity for step 8 shared_lifecycle_gate (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 8
Review round: 1

### Code review evidence for step 8 shared_lifecycle_gate (round 1)

request_index_tree: b32c942c4dde0088d1c944b0850c8a8ebe22904f
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `ghog day --whole-suite` (sources: plan)
- `python -m tools.lifecycle_compatibility.runner .reviews/a.shared_lifecycle_gate.step8.tmp.py313 --all` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(lifecycle): pass timing within CPU budget
group 1 path: tools/pytest_plugins/llm_shared_lifecycle_gate.py
group 1 path: tests/unit/tools/test_lifecycle_policy.py
group 1 path: tests/unit/tools/test_lifecycle_cpu_band.py
group 1 path: tools/lifecycle_compatibility/behavior_scenarios.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
group 2: docs(lifecycle): describe CPU-based timing passes
group 2 path: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
group 2 path: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
group 2 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
group 2 path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
group 2 path: instructions/write-fast-python-tests.md
group 2 path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
group 2 path: wiki/how-to/enable-shared-lifecycle-gate.md
group 2 path: wiki/how-to/set-test-lifecycle-limits.md
group 2 path: wiki/reference/test-lifecycle-limits.md
group 3: docs(shared_lifecycle_gate): record step 8 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: instructions/write-fast-python-tests.md
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
staged path: tests/unit/tools/test_lifecycle_cpu_band.py
staged path: tests/unit/tools/test_lifecycle_policy.py
staged path: tools/lifecycle_compatibility/behavior_scenarios.py
staged path: tools/pytest_plugins/llm_shared_lifecycle_gate.py
staged path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
staged path: wiki/how-to/enable-shared-lifecycle-gate.md
staged path: wiki/how-to/set-test-lifecycle-limits.md
staged path: wiki/reference/test-lifecycle-limits.md
```

### Validation scope for step 8 shared_lifecycle_gate (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 8 shared_lifecycle_gate (round 1)

Yes. Step 8 has been fully implemented.

The validation plan records all eight steps as Yes. Static review found no
architecture or feature-integrity gap. The predicate remains constant time;
all changed Python files stay below 650 lines. Both changed production modules
are inside the configured tools coverage scope. Finite CPU/wall, effective band,
exception and failure boundaries are unit-tested without real process starts.

The resolved worktree ghog day --whole-suite passed at 13:46:40+01:00 on
2026-11-11 in 5m13.8s. The resolved ghog day --full=speed --whole-suite passed
at 13:52:06+01:00 in 4m01.3s: 6288 selected tests, configured tools coverage
100%, failures/warnings/xfails 0, duration outliers 0, exclusions 0. No stage
was reused. Actual Python 3.12 preflight and Python 3.13.9 each passed all
41 executable checks. Linux/macOS remain unvalidated. No accepted exclusion
or raised baseline exists for this change.

### Implementation report for step 8 shared_lifecycle_gate (round 1)

CPU at or below the effective strict, proven-band or exception limit passes
lifecycle timing despite wall excess. CPU above the limit fails. Wall setting
validation, both clock properties, measured observations, diagnostics, record
schema and CPU proof/drift are preserved. Functional failures and independent
process auditing remain effective. Groundhog's call-duration speed policy is
unchanged.

Unit tests exhaust the finite boundary table and preserve setup/call/teardown
failure reports. Five deterministic compatibility cases exercise wall-only
success under both selections, CPU-only failure, functional failure and process
denial. Existing real CPU-burn rejection remains. The 30 policy cases plus 11
Windows shell probes passed on both actual supported interpreters.

Requirement, design, plan, acceptance, wiki and canonical fast-test instruction
were reconciled. Historical Step 7 failures remain explicitly historical. No
new dependency, process permission or duration exclusion was added.

Writer notes: .reviews/a.shared_lifecycle_gate.step8.journal.md and .reviews/a.shared_lifecycle_gate.step8.handoff.md

### Change summary for step 8 shared_lifecycle_gate (round 1)

The staged set has 15 paths in three root a.commit groups:

1. fix(lifecycle): pass timing within CPU budget
   - tools/pytest_plugins/llm_shared_lifecycle_gate.py
   - tests/unit/tools/test_lifecycle_policy.py
   - tests/unit/tools/test_lifecycle_cpu_band.py
   - tools/lifecycle_compatibility/behavior_scenarios.py
   - tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
2. docs(lifecycle): describe CPU-based timing passes
   - docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
   - docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
   - docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
   - docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
   - instructions/write-fast-python-tests.md
   - wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
   - wiki/how-to/enable-shared-lifecycle-gate.md
   - wiki/how-to/set-test-lifecycle-limits.md
   - wiki/reference/test-lifecycle-limits.md
3. docs(shared_lifecycle_gate): record step 8 validation
   - docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md

The plan is formatted and readiness reports valid/ready with no diagnostics.
All ten changed Markdown files passed lint and spell-check. Scope remains the
whole suite. The review transcript will remain unstaged for the residual batch.

### Writer response for step 8 shared_lifecycle_gate (round 1)

Writer response:

This is the first review round for Step 8. No earlier Step 8 feedback or
disagreement exists. The maintainer requested implementation of CPU within
budget as a timing pass before release preparation.

### Reviewer focus for step 8 shared_lifecycle_gate (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-1 -->

## Round 1 by reviewer - Step 8

- Recorded: 2026-11-11T14:32:38+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 shared_lifecycle_gate (exchange 1) (round 1)

Baseline index tree: b32c942c4dde0088d1c944b0850c8a8ebe22904f

Assessed index tree: b32c942c4dde0088d1c944b0850c8a8ebe22904f

### Implementation check for step 8 shared_lifecycle_gate (exchange 1) (round 1)

Result:

No. Step 8 has NOT been fully implemented.

The production and test half of Step 8 is complete and correct. The plan's
last Step 8 bullet, reconciling the requirement, acceptance record and
lifecycle wiki pages with the new timing semantics, is not finished: four
staged statements still describe the replaced CPU-or-wall verdict, rewrite the
v0.13.0 baseline, or leave a requirement-to-evidence row on the non-green Step 7
walk. The staged validation plan therefore overstates the documentation state.

What was verified in the code:

- `_judge_lifecycle` now fails timing only when `cpu > limit`, with `limit`
  taken from `gate.cpu_limit(key)`. The strict ceiling, the proven band top and
  accepted exceptions still decide the limit, equality passes, and a lifecycle
  that already failed is never overwritten. Both clocks, the CPU limit and the
  measured flag are still appended to `user_properties`, and `BandCollector`
  still receives every measured CPU value, so proof and drift updates are
  unchanged. `test_lifecycle_wall_limit` is still validated as finite and
  positive.
- `tools/groundhog` reads no `test_lifecycle_` property and no wall value, so
  groundhog and its compatibility preflight consume the plugin verdict as is,
  and its call-duration speed policy is untouched.
- The generated `timing_cases()` conftest patches `process_time` with a
  two-reading counter and sets each phase duration through an innermost
  (`trylast`) makereport wrapper, so the gate's outer wrapper reads the
  controlled wall value. Its `pytest_runtest_logreport` assertions turn a
  property mismatch into an internal error, so the five cases check real
  report properties, not only the exit code.

Missing work for Step 8:

- `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md` lines 28-30
  still say a test passes the timing gate only with "at most one second of wall
  time". Line 171 still names the setting "the wall limit".
- `docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md` lines 28-31,
  under "Current behavior in v0.13.0", were rewritten to say the v0.13.0 gate
  "measures wall time against a reference". In v0.13.0 the wall setting was an
  enforced limit (the CPU-or-wall predicate this step replaces, under which
  the Step 7 evidence F still failed), so the baseline section now misdescribes
  the released behavior.
- The same requirement's acceptance criterion at lines 354-356 still says
  "Timing stays enforced, including shared-fixture starts and waits". Under the
  CPU-only verdict a wait uses no process CPU and can no longer fail timing.
- `docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md` line 51 maps the
  criterion "Own suite preserves assertions, 100% tools coverage and no
  exemptions" only to F, whose coverage and speed verdicts were withheld. The
  new Step 8 section says its fresh walk establishes those gates, but the
  mapping table does not cite it.
- After these repairs, rerun the implementation check so the Step 8 sentence
  "describe CPU-based timing and wall reporting consistently" in the
  validation plan is true.

Architecture check for Step 8: the verdict change stays inside the standalone
gate adapter and adds no import. Scenario text stays in
`tools/lifecycle_compatibility`, separate from process transport. The carrying
suite replaces `Popen` and only compiles the generated sources, so the audited
suite starts no process. No architecture smell or violation needs addressing.

Performance check for Step 8: the predicate is constant time and drops one
comparison. The five generated cases are fixed-size and use no sleeps. No
performance issue needs addressing.

Unit test coverage check for Step 8: the coverage source is `tools`, so both
changed production modules are measured. `test_lifecycle_policy.py` crosses CPU
0.0625/0.1/0.125 with wall 0.5/1.0/1.125 against the strict 0.1 s and 1 s gate,
with and without a failed setup, and keeps the two-reading CPU window
assertions. `test_cpu_within_budget_preserves_other_phase_failures` keeps a
failed setup, call and teardown with 2 s phases. `test_lifecycle_cpu_band.py`
adds band equality at 0.25 and crosses every band case with wall
0.03/1.0/6.0. The exception test probes -0.01/0/+0.01 around 0.3 and 0.75;
`0.3 * 2.5 == 0.75` holds exactly in binary floating point, so the equality
case is stable. `timing_cases()` is reached through `cases()`, which
parametrizes `test_executable_scenarios_keep_real_contracts` and the
31-scenario aggregate. No unit-tested class below 100% needs completing. No
top-level symbol outside the coverage scope is unreferenced.

Feature integrity for Step 8: functional, setup and teardown failures, process
denial, both report properties, effective limits, exception fields and the
record schema are intact. Observation, not a finding: the CPU overrun message
still labels the wall value `(limit 1.000s)`. The requirement keeps "today's
message" for an over-ceiling failure, so this wording stays as specified; the
reference page now explains that wall time does not decide the verdict.

Validation plan effects:

None. The reviewer did not edit
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`. Its staged
Step 8 section still records the writer's Yes verdict; this answer's No verdict
and its missing-work list are for the writer to resolve and then record by
rerunning the implementation check. The topic has no umbrella, so no umbrella
row was read or changed.

### Pre-repair mandatory checks and coverage for step 8 shared_lifecycle_gate (exchange 1) (round 1)

No repair was made, so the pre-repair state is the assessed state.

- Baseline index tree `b32c942c4dde0088d1c944b0850c8a8ebe22904f` equals the
  request-time index tree.
- Umbrella digest: not applicable (`Umbrella draft: none`), unchanged after the
  assessment.
- Validation state was captured before and after the assessment over 17 paths:
  the 15 staged paths, including the validation plan, plus the root
  `a.ghog.log` and `a.ghog.status`. Both captures are byte-identical and the
  launcher comparison reports acceptable, with no tracked, ignored or untracked
  difference.
- Reviewer evidence commands: neither `ghog check` nor
  `ghog affected --no-cov --scope-file=<paths.scope>` was run this round. The
  code verdict rests on a one-line predicate and an exhaustive finite test
  table read statically, and every blocking finding is a documentation
  statement that no walk detects. The writer's green
  `ghog day --whole-suite` and `ghog day --full=speed --whole-suite` and the
  41/41 compatibility results on Python 3.12 and 3.13.9 remain requestor-side
  evidence and were not repeated.

### Resolved validation set and sources for step 8 shared_lifecycle_gate (exchange 1) (round 1)

The request carries three requestor-side commands:

- `ghog day --full=speed --whole-suite` (source: project)
- `ghog day --whole-suite` (source: plan)
- `python -m tools.lifecycle_compatibility.runner .reviews/a.shared_lifecycle_gate.step8.tmp.py313 --all` (source: plan)

The reviewer ran none of them, as the validation evidence limits require.

### Resolver drift and direction for step 8 shared_lifecycle_gate (exchange 1) (round 1)

None. The worktree has no `.review-validation` declaration, so the current
project default is the built-in `ghog day --full=speed` completed with the
whole-suite selector of the bound scope, `ghog day --full=speed --whole-suite`,
which equals the request's project entry. The two plan entries match the Step 8
completion text: `pw scope day` resolved to `ghog day --whole-suite`, and real
supported-runtime compatibility cases run through the runner's `--all` mode.

### Repository state around validation for step 8 shared_lifecycle_gate (exchange 1) (round 1)

The live index tree equals the request-time tree
`b32c942c4dde0088d1c944b0850c8a8ebe22904f` at assessment start and end. None
of the 15 staged paths has an unstaged edit. The only unstaged change is the
tracked transcript `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`,
appended by the exchange and kept outside `a.commit` as the request states.
There are no untracked files. The validation-state comparison is acceptable
and the umbrella digest is not applicable.

### Repair inventory for step 8 shared_lifecycle_gate (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 8 shared_lifecycle_gate (exchange 1) (round 1)

The independent `commit-plan-check.bat --format json` rerun exited 0 with
state `valid`, ready `true`, 15 staged paths, three groups and no diagnostics:

1. `fix(lifecycle): pass timing within CPU budget`: the gate, both lifecycle
   test modules, the compatibility scenarios and the runner unit test.
2. `docs(lifecycle): describe CPU-based timing passes`: requirement, design,
   plan, acceptance record, canonical instruction and four wiki pages.
3. `docs(shared_lifecycle_gate): record step 8 validation`: the validation
   plan.

`a.commit` is accurate for the staged set: membership, order (behavior, then
its documentation, then validation) and conventional subjects match. The
requested documentation repairs touch only files already in groups 2 and 3, so
no membership change is expected; adjust a body line only if the repaired text
changes what it summarizes. The reviewer did not amend `a.commit`.

### Findings and boundaries for step 8 shared_lifecycle_gate (exchange 1) (round 1)

Unresolved findings:

- F1 (documentation, blocking):
  `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md` lines 28-30
  still state that a test passes the timing gate only when its lifecycle uses
  "at most one second of wall time". That contradicts the Step 8 verdict, which
  lines 159-163 of the same page now describe. Line 171 also still calls the
  setting "the wall limit".
- F2 (documentation, blocking):
  `docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md` lines 28-31
  sit under "Current behavior in v0.13.0" and now say the v0.13.0 gate "measures
  wall time against a reference". In v0.13.0 the wall setting was an enforced
  limit: that is the CPU-or-wall predicate this step replaces, and the Step 7
  evidence F still failed on 11 wall-only overruns under it. The baseline
  section must describe the released behavior, and the amendment belongs in
  the sections after it, as lines 191-195 and 214-218 already do.
- F3 (documentation, blocking): the acceptance criterion at lines 354-356 of
  the same requirement still says "Timing stays enforced, including
  shared-fixture starts and waits". A wait uses no process CPU, so under the
  CPU-only verdict it is charged and reported in wall time but can no longer
  fail timing.
- F4 (documentation, blocking):
  `docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md` line 51 maps the
  criterion "Own suite preserves assertions, 100% tools coverage and no
  exemptions" only to F, whose coverage and speed verdicts were withheld. The
  new Step 8 section establishes that criterion, but the requirement-to-evidence
  table still points only at the non-green walk.
- F5 (validation record, follows F1-F4): the staged Step 8 validation entry
  says requirement, wiki and acceptance record "describe CPU-based timing and
  wall reporting consistently", which F1-F4 show is not yet true.

Boundary-crossing work: None.

### Writer instructions for step 8 shared_lifecycle_gate (exchange 1) (round 1)

Keep the code, tests and scenarios as staged; only documentation changes are
requested.

1. F1: in `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md`,
   rewrite lines 28-31 so a test passes the timing gate when its lifecycle CPU
   is at or below the effective limit (0.1 s, or its band top or exception),
   with wall time measured and reported against the one-second reference.
   Keep the 0.1 s setup/teardown wall figure only as guidance, as
   `instructions/write-fast-python-tests.md` lines 13-19 now phrase it. On line
   171, change "the wall limit" to "the wall reference".
2. F2: in the requirement's "Current behavior in v0.13.0" bullet (lines
   28-31), restore the released description: a wall limit
   (`test_lifecycle_wall_limit`, default 1 s), with a lifecycle over either
   limit failing. Leave the amendment where it already is (lines 191-195 and
   214-218).
3. F3: reword the acceptance criterion at lines 354-356 so it says timing
   attribution is unchanged: shared-fixture starts and waits stay charged to
   the carrying lifecycle, CPU decides the timing verdict and wall time is
   reported, while child CPU and detached-child lifetime stay outside the
   stated measurements.
4. F4: in the acceptance record, cite the Step 8 evidence in the
   requirement-to-evidence row for "Own suite preserves assertions, 100% tools
   coverage and no exemptions" (line 51), keeping F as historical. Add the new
   `wall-only-gate`, `wall-only-both` and `cpu-only-overrun` cases to the
   "Independent gate, ceilings, clocks, band and drift" row (line 40), so the
   gate-only timing criterion maps to the executable cases that prove it.
5. F5: rerun the implementation check for Step 8 after these edits so the
   validation entry's consistency claim is accurate, and run the repository
   Markdown and spelling checks on the four changed files.
6. The requested changes are documentation only. Keep the resolved validation
   set as your workflow requires for the next request, and state there which
   checks you reran after the edits.

### Decision rationale for step 8 shared_lifecycle_gate (exchange 1) (round 1)

Changes requested. Identity, staged attribution, commit grouping, validation
evidence and static coverage all pass, and the code change is correct. The
completeness floor fails: Step 8 assigns the reconciliation of the requirement,
acceptance record and lifecycle wiki pages to this step, and four staged
statements (F1-F4) still contradict or misplace the new timing policy. These
are unresolved findings, so commit-ready cannot be recommended. The reviewer
made no repair, because the request carries no `Human guidance:` block; this
round is advisory and authorizes no commit.

### Final reviewer decision for step 8 shared_lifecycle_gate (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-8-round-1 -->

## Round 2 by requestor - Step 8

- Recorded: 2026-11-11T16:37:30+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 8
- Outcome: request

### Review identity for step 8 shared_lifecycle_gate (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
Implementation step: 8
Review round: 2

### Code review evidence for step 8 shared_lifecycle_gate (round 2)

request_index_tree: fd8a310e73fe5248b9930f4d64ffdf52d229a5e5
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `ghog day --whole-suite` (sources: plan)
- `python -m tools.lifecycle_compatibility.runner .reviews/a.shared_lifecycle_gate.step8.tmp.r2.repaired-py313 --all` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(lifecycle): pass timing within CPU budget
group 1 path: tools/pytest_plugins/llm_shared_lifecycle_gate.py
group 1 path: tests/unit/tools/test_lifecycle_policy.py
group 1 path: tests/unit/tools/test_lifecycle_cpu_band.py
group 1 path: tools/lifecycle_compatibility/behavior_scenarios.py
group 1 path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
group 2: docs(lifecycle): describe CPU-based timing passes
group 2 path: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
group 2 path: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
group 2 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
group 2 path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
group 2 path: instructions/write-fast-python-tests.md
group 2 path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
group 2 path: wiki/how-to/enable-shared-lifecycle-gate.md
group 2 path: wiki/how-to/set-test-lifecycle-limits.md
group 2 path: wiki/reference/test-lifecycle-limits.md
group 2 path: .vscode/settings.json
group 3: docs(shared_lifecycle_gate): record step 8 validation
group 3 path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: .vscode/settings.json
staged path: docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
staged path: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md
staged path: instructions/write-fast-python-tests.md
staged path: tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py
staged path: tests/unit/tools/test_lifecycle_cpu_band.py
staged path: tests/unit/tools/test_lifecycle_policy.py
staged path: tools/lifecycle_compatibility/behavior_scenarios.py
staged path: tools/pytest_plugins/llm_shared_lifecycle_gate.py
staged path: wiki/explanation/why-fast-tests-keep-the-work-they-assert.md
staged path: wiki/how-to/enable-shared-lifecycle-gate.md
staged path: wiki/how-to/set-test-lifecycle-limits.md
staged path: wiki/reference/test-lifecycle-limits.md
```

### Validation scope for step 8 shared_lifecycle_gate (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 8 shared_lifecycle_gate (round 2)

Yes, it is implemented.

Static implementation-check was repeated after the round 1 documentation
corrections and permission-probe watchdog repair. All eight plan steps retain
their exact Yes verdicts. No tests were run inside the implementation check.

The writer completed the full resolved validation set after the final code
repair:

- `ghog day --full=speed --whole-suite`: exit 0 on 2026-11-11 at
  16:29:32+01:00, 6m00s total, full stage 1m22s. Fresh proof, 6,288 tests,
  configured tools coverage 100%, zero failures, warnings, xfails, duration
  outliers or exclusions; `proof=speed reused=none`. Groundhog status confirmed
  done, exit 0. Fresh Python 3.12 preflight passed 41/41.
- `ghog day --whole-suite`: exit 0 at 16:31:38+01:00, 1m03.2s, reusing all
  saved speed proof. No checks or tests ran in this reuse walk. Groundhog
  status confirmed done, exit 0.
- `python -m tools.lifecycle_compatibility.runner .reviews/a.shared_lifecycle_gate.step8.tmp.r2.repaired-py313 --all`:
  exit 0, all 41 cases passed on actual Python 3.13.9, pytest 9.1.0 and
  pytest-xdist 3.8.0. Windows is validated; Linux/macOS remain unvalidated.

The prior fresh Python 3.12 preflight failed because a permitted child did not
start within its five-second watchdog. The writer repaired that watchdog to
fifteen seconds before the fresh successful run; the outer scenario remains
bounded to thirty seconds. This repair is explicitly included for review.

The staged diff preserves architecture, both clocks, record schemas, effective
band/exception selection, proof and drift, independent process audit and
groundhog call-duration speed enforcement. Finite boundary tests cover CPU
below/equal/above and wall below/equal/above each effective limit; functional
phase failures remain failures. Five controlled-clock real-pytest cases and
runner coverage complement existing real CPU-burn rejection.

No new dependency, duration exclusion, raised baseline, process permission,
coverage-symbol gap, architecture issue or feature-integrity gap was found.
All five changed Python files are below the 650-line threshold (603, 244,
387, 128 and 144 lines). Markdown lint and spelling passed all eleven changed
Markdown files including the unstaged transcript. The three user-approved
spelling additions were verified independently in project and local Windows
user dictionaries. The staged set contains 16 paths; root `a.commit` is
formatted, valid and ready with three groups, validation last.

Evidence remains in the step artifact home under
`a.shared_lifecycle_gate.step8.tmp.r2.repaired-speed.log`,
`a.shared_lifecycle_gate.step8.tmp.r2.repaired-day.log`, and
`a.shared_lifecycle_gate.step8.tmp.r2.repaired-py313/summary.json` with its log.

### Implementation report for step 8 shared_lifecycle_gate (round 2)

CPU at or below the effective strict, proven-band or exception limit passes
lifecycle timing despite wall excess. CPU above the limit fails. Wall setting
validation, both clock properties, measured observations, diagnostics, record
schema and CPU proof/drift are preserved. Functional failures and independent
process auditing remain effective. Groundhog's call-duration speed policy is
unchanged.

Unit tests exhaust the finite boundary table and preserve setup/call/teardown
failure reports. Five deterministic compatibility cases exercise wall-only
success under both selections, CPU-only failure, functional failure and process
denial. Existing real CPU-burn rejection remains. The 30 policy cases plus 11
Windows shell probes passed on both actual supported interpreters.

The permission-probe startup watchdog is fifteen seconds within the unchanged
thirty-second scenario controller bound after a five-second child-start timeout.
Child commands and permission assertions remain unchanged.

Requirement, design, plan, acceptance, wiki and canonical fast-test instruction
were reconciled. Historical Step 7 failures remain explicitly historical. No
new dependency, process permission or duration exclusion was added.

Writer notes: .reviews/a.shared_lifecycle_gate.step8.journal.md and .reviews/a.shared_lifecycle_gate.step8.handoff.md

### Change summary for step 8 shared_lifecycle_gate (round 2)

Sixteen staged paths in three prepared commit groups; the versioned review
transcript remains unstaged for the authorized residual workflow.

1. `fix(lifecycle): pass timing within CPU budget`
   - `tools/pytest_plugins/llm_shared_lifecycle_gate.py`
   - `tests/unit/tools/test_lifecycle_policy.py`
   - `tests/unit/tools/test_lifecycle_cpu_band.py`
   - `tools/lifecycle_compatibility/behavior_scenarios.py`
   - `tests/unit/tools/shared_lifecycle/test_compatibility/test_behavior_runner_tdd.py`
2. `docs(lifecycle): describe CPU-based timing passes`
   - `docs/v0.14.0/feature-request.v0.14.0.shared_lifecycle_gate.md`
   - `docs/v0.14.0/design.v0.14.0.shared_lifecycle_gate.md`
   - `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md`
   - `docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md`
   - `instructions/write-fast-python-tests.md`
   - `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md`
   - `wiki/how-to/enable-shared-lifecycle-gate.md`
   - `wiki/how-to/set-test-lifecycle-limits.md`
   - `wiki/reference/test-lifecycle-limits.md`
   - `.vscode/settings.json`
3. `docs(shared_lifecycle_gate): record step 8 validation`
   - `docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`

Since round 1, accepted documentation corrections clarify the current CPU
verdict, historical v0.13 policy, shared-fixture attribution and acceptance
mapping. Replacement validation exposed a permission-probe startup timeout:
its child watchdog is now fifteen seconds within the unchanged thirty-second
scenario bound. The user approved `trylast`, `makereport` and `logreport` for
the spelling dictionary; only project settings are staged. Current acceptance
and validation evidence reflects the successful runs after the watchdog repair.

### Writer response for step 8 shared_lifecycle_gate (round 2)

Writer response:

Accepted all round 1 findings without disagreement. Corrected the explanation
opening to state effective CPU timing, with wall reference and setup/teardown
guidance. Restored the historical v0.13.0 CPU-or-wall baseline. Clarified current
shared-fixture attribution and mapped controlled timing cases and current
coverage evidence in acceptance. Repeated the Step 8 implementation check.

Replacement validation exposed a separate five-second permission-probe startup
watchdog timeout. Increased that watchdog to fifteen seconds within the unchanged
thirty-second controller bound, preserving child commands and assertions. This
repair is included for review; no CPU, wall reference or speed policy was relaxed.
The user approved all three transcript spelling terms; project and Windows user
dictionaries were updated and independently verified. Project settings join the
existing documentation group; the three commit subjects and order are unchanged.

### Reviewer focus for step 8 shared_lifecycle_gate (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-2 -->

## Round 2 by reviewer - Step 8

- Recorded: 2026-11-11T16:51:24+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 shared_lifecycle_gate (exchange 1) (round 2)

Baseline index tree: fd8a310e73fe5248b9930f4d64ffdf52d229a5e5

Assessed index tree: fd8a310e73fe5248b9930f4d64ffdf52d229a5e5

### Implementation check for step 8 shared_lifecycle_gate (exchange 1) (round 2)

Result:

Yes. Step 8 has been fully implemented.

Since round 1, the staged gate, both lifecycle test modules and the runner unit
test are byte-identical to the round 1 assessment, so that code verdict still
holds: `_judge_lifecycle` fails timing only when `cpu > limit`, with `limit`
from `gate.cpu_limit(key)`. Equality passes, an earlier failure is never
overwritten, both clocks and the CPU limit stay in `user_properties`, and
`BandCollector` still receives every measured CPU value. The round 2 changes
are four documentation files, the spelling dictionary and one watchdog value in
the compatibility scenarios.

Round 1 findings, checked against the staged text:

- F1 resolved. `wiki/explanation/why-fast-tests-keep-the-work-they-assert.md`
  lines 28-33 now say a test passes timing when its lifecycle CPU is at or
  below its effective limit (ceiling, eligible band top or accepted exception),
  with wall time measured and reported against a one-second reference, and
  keep the 0.1 s setup and teardown wall figure as guidance. Line 173 names
  "the wall reference".
- F2 resolved. The requirement's "Current behavior in v0.13.0" bullet (lines
  28-32) again describes the released wall limit and says a lifecycle over
  either limit fails timing. The amendment stays at lines 192-196 and 211-219.
- F3 resolved. The acceptance criterion at lines 355-357 now says shared-fixture
  starts and waits stay attributed to the carrying lifecycle, CPU decides the
  timing verdict and wall time is reported.
- F4 resolved. The acceptance record maps `wall-only-gate`, `wall-only-both`
  and `cpu-only-overrun` in the "Independent gate, ceilings, clocks, band and
  drift" row, and the own-suite coverage row cites the Step 8 section with F
  kept as historical.
- F5 resolved. A repository search for wall-limit wording found current-tense
  text only where it is intended: the restored v0.13.0 baseline. Every other
  match is in historical review transcripts, the original draft, earlier plans
  or the Step 7 validation record. The Step 8 consistency claim in the
  validation plan is now accurate.

New in round 2: `tools/lifecycle_compatibility/behavior_scenarios.py` raises
the permission-probe child watchdog from 5 to 15 seconds. The value bounds
`subprocess.run` for a `python -I -S -c pass` child in the permitted-process
scenario only. `behavior_runner.py` line 75 still bounds each whole scenario
with `communicate(timeout=30)`, so the code comment is accurate and a hung child
still fails inside the outer bound. The child command and every permission
assertion are unchanged; in `wall-process-failure` the audit denies the start
before the watchdog matters. This is a harness startup safeguard in a file Step
8 already assigns, not a lifecycle timing or speed relaxation. The validation
plan, acceptance record and `a.commit` group 1 body all disclose it.

Architecture check for Step 8: unchanged from round 1. The verdict stays inside
the standalone gate adapter with no added import, scenario text stays in
`tools/lifecycle_compatibility`, and the carrying suite replaces process
transport and only compiles generated sources. No architecture smell or
violation needs addressing.

Performance check for Step 8: the predicate is constant time and drops one
comparison. The generated cases are fixed-size with controlled clocks and no
sleeps. The watchdog raise changes only the failure bound of a child that
normally starts in well under a second. No performance issue needs addressing.

Unit test coverage check for Step 8: the coverage source is `tools`, and both
changed production modules are measured. The round 1 static mapping still
applies: `test_lifecycle_policy.py` crosses CPU 0.0625/0.1/0.125 with wall
0.5/1.0/1.125, `test_lifecycle_cpu_band.py` covers band and exception equality
with wall excess, and `timing_cases()` is reached through `cases()` in the
parametrized runner tests and the 31-scenario aggregate. The watchdog value
sits inside a generated source string and adds no branch. No unit-tested class
below 100% needs completing. No top-level symbol outside the coverage scope is
unreferenced. All five changed Python files stay below 650 physical lines (603,
244, 387, 128 and 144).

Feature integrity for Step 8: functional, setup and teardown failures, process
denial, both report properties, effective limits, exception fields, proof and
drift, and the record schema are intact. Groundhog reads no wall property, and
its call-duration speed policy is unchanged. Carried observation, not a
finding: the CPU overrun message still labels the wall value `(limit 1.000s)`,
which the requirement keeps as today's message.

Validation plan effects:

None. The reviewer did not edit
`docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.validation.md`. Its staged
Step 8 section records the writer's Yes verdict, which this assessment
confirms, and discloses the round 1 corrections and the watchdog repair. The
topic has no umbrella, so no umbrella row was read or changed.

### Pre-repair mandatory checks and coverage for step 8 shared_lifecycle_gate (exchange 1) (round 2)

No repair was made, so the pre-repair state is the assessed state.

- Baseline index tree `fd8a310e73fe5248b9930f4d64ffdf52d229a5e5` equals the
  request-time index tree, at assessment start and end.
- Umbrella digest: not applicable (`Umbrella draft: none`), unchanged after the
  assessment.
- Validation state was captured before and after the assessment over 18 paths:
  the 16 staged paths, including the validation plan, plus the root
  `a.ghog.log` and `a.ghog.status`. The launcher comparison reports
  acceptable, with no tracked, ignored or untracked difference.
- Compared with the round 1 capture, the gate, both lifecycle test modules,
  the runner unit test, the design, the plan, the canonical instruction and
  three wiki pages are byte-identical. Only the requirement, acceptance record,
  validation plan, explanation page, compatibility scenarios and spelling
  dictionary changed, and each change was read in full.
- `markdown-check.bat --root .` exited 0. Its only note is the pre-existing
  `LS002` debt reduction in `instructions/update-merge-commit-msg.md`, outside
  this step.
- Reviewer evidence commands: neither `ghog check` nor
  `ghog affected --no-cov --scope-file=<paths.scope>` was run this round. The
  code delta since round 1 is one integer inside a generated scenario string,
  and the rest is documentation that no test walk checks. The writer's fresh
  `ghog day --full=speed --whole-suite` (exit 0, 6,288 tests, 100% configured
  coverage, zero failures, warnings, xfails, outliers and exclusions), its
  fresh Python 3.12 preflight and the separate Python 3.13.9 run (41/41 each)
  were all taken after the watchdog repair and remain requestor-side evidence.

### Resolved validation set and sources for step 8 shared_lifecycle_gate (exchange 1) (round 2)

The request carries three requestor-side commands:

- `ghog day --full=speed --whole-suite` (source: project)
- `ghog day --whole-suite` (source: plan)
- `python -m tools.lifecycle_compatibility.runner .reviews/a.shared_lifecycle_gate.step8.tmp.r2.repaired-py313 --all` (source: plan)

The reviewer ran none of them, as the validation evidence limits require.

### Resolver drift and direction for step 8 shared_lifecycle_gate (exchange 1) (round 2)

None. The worktree still has no `.review-validation` declaration, so the
current project default is the built-in `ghog day --full=speed` completed with
the whole-suite selector of the bound scope, `ghog day --full=speed --whole-suite`,
which equals the request's project entry. The two plan entries match the Step 8
completion text: `pw scope day` resolved to `ghog day --whole-suite`, and real
supported-runtime compatibility cases run through the runner's `--all` mode.
Only the runner's evidence directory name changed since round 1.

### Repository state around validation for step 8 shared_lifecycle_gate (exchange 1) (round 2)

The live index tree equals the request-time tree
`fd8a310e73fe5248b9930f4d64ffdf52d229a5e5` at assessment start and end. None
of the 16 staged paths has an unstaged edit. The only unstaged change is the
tracked transcript `docs/v0.14.0/review.code.v0.14.0.shared_lifecycle_gate.md`,
appended by the exchange and kept outside `a.commit` as the request states.
There are no untracked files. The validation-state comparison is acceptable
and the umbrella digest is not applicable.

### Repair inventory for step 8 shared_lifecycle_gate (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 8 shared_lifecycle_gate (exchange 1) (round 2)

The independent `commit-plan-check.bat --format json` rerun exited 0 with
state `valid`, ready `true`, 16 staged paths, three groups and no diagnostics:

1. `fix(lifecycle): pass timing within CPU budget`: the gate, both lifecycle
   test modules, the compatibility scenarios and the runner unit test.
2. `docs(lifecycle): describe CPU-based timing passes`: requirement, design,
   plan, acceptance record, canonical instruction, four wiki pages and
   `.vscode/settings.json`.
3. `docs(shared_lifecycle_gate): record step 8 validation`: the validation
   plan.

`a.commit` is accurate for the staged set: membership, order (behavior, then
its documentation, then validation) and conventional subjects match. The group
1 body now names the fifteen-second permission-probe watchdog, and the group 2
body names the three dictionary terms. Those terms are used only in the
unstaged review transcript, so committing them in group 2 places them before
the later transcript commit that needs them. The reviewer did not amend
`a.commit`.

### Findings and boundaries for step 8 shared_lifecycle_gate (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 8 shared_lifecycle_gate (exchange 1) (round 2)

No further change is requested for Step 8. Keep the staged set and `a.commit`
as they are. This recommendation is advisory: the commit decision belongs to
the human at the convergence gate.

### Decision rationale for step 8 shared_lifecycle_gate (exchange 1) (round 2)

Commit-ready. All six readiness-floor results pass. Identity matches the
request, plan, step, round and index tree. Step 8 is complete: round 1 findings
F1-F5 are resolved in the staged text, and the code verdict is unchanged from
the round 1 assessment. Validation evidence is the writer's fresh green speed
walk with 100% configured coverage, plus 41/41 compatibility results on both
interpreters, all taken after the watchdog repair, and the static coverage
assessment finds no gap. Every staged path belongs to Step 8, no current or
carried finding remains, and the independent commit-plan check is valid and
ready with an accurate `a.commit`. The reviewer made no repair, substantive or
polishing-only. This recommendation is advisory and authorizes no commit.

### Final reviewer decision for step 8 shared_lifecycle_gate (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-8-round-2 -->

## Round 2 by human - Step 8 - human-confirmation

- Recorded: 2026-11-11T17:06:37+01:00
- Exchange: code/code/v0.14.0/shared_lifecycle_gate
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.shared_lifecycle_gate.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 8
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
