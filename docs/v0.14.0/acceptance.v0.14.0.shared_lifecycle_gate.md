# Shared lifecycle gate acceptance evidence for v0.14.0

<!-- markdownlint-disable MD013 -->

This record maps the [requirement](feature-request.v0.14.0.shared_lifecycle_gate.md)
and [design cases](design.v0.14.0.shared_lifecycle_gate.md) to repeatable checks.
Evidence was collected on Windows on 2026-11-10 and 2026-11-11. Linux and macOS are unvalidated;
the implementation retains portable-API intent.

## Evidence sources for shared-policy acceptance

| ID | Repeatable source | Observation |
| --- | --- | --- |
| A | `tests/acceptance/shared_lifecycle/test_shared_plugins/test_shared_plugins_tdd.py::test_prepared_groundhog_consumer_contract` | Four selections join real preparation, runner environment isolation, canonical loading, strict configuration, unused declarations and record writes. Focused groundhog: exit 0, five tests, no warnings, 5.6 seconds. |
| L | `tests/unit/tools/shared_lifecycle/test_loader/test_loader_tdd.py` | Named startup, binding, duplicate-registration and independent-cache checks below. |
| G | `tests/unit/tools/shared_lifecycle/test_gate_contract/test_gate_contract_tdd.py`, `tests/unit/tools/test_lifecycle_cpu_band.py`, `tests/unit/tools/test_lifecycle_policy.py` | Settings, safe storage, existing records, clocks, proof and drift contracts. |
| P | `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`, `test_audit_ownership/test_audit_ownership_tdd.py`, `test_audit_workers/test_audit_workers_tdd.py` under the same shared-lifecycle root | Declaration, ownership, embedded-session and distributed-report contracts. |
| E | `bin/lifecycle_compatibility.bat --evidence <private-evidence>`; main-runtime `python -m tools.lifecycle_compatibility.runner <fresh-private-evidence> --all` | All 36 checks passed on each actual runtime: Python 3.12.15 and 3.13.9; pytest 9.1.0, xdist 3.8.0. These comprise 25 policy cases and 11 Windows shell probes. Worker barriers verified cleanup. |
| W | Tracked `tools.lifecycle_compatibility.shell_runner.run_all`, included in `runner --all` and `bin/lifecycle_compatibility.bat --evidence` | Eleven real `cmd.exe` probes passed on both runtimes: delayed expansion off/on, punctuation and OEM non-ASCII paths, atomic invalid-selection and unrepresentable-value refusal, drive-root preparation, distinct concurrent transfers and concurrent preparations. Other platforms report not run. |
| T | Anonymous existing consumer: prepared-shell `python -m pytest <existing-test-file>` and groundhog `commands.run_tests_outcome` with a genuine child | Both passed 23 existing tests on Python 3.12.10 / pytest 9.1.1. Transient selection `lifecycle,process`; no file changes or persistent activation. |
| R | Compare Step 3 pre-migration snapshot with live lifecycle record after the last validation attempt | All 5,892 previous eligible proofs remain; 345 new eligible proofs. Exception meanings, raw exception fields and other document fields are preserved; no missing nodes or lost eligible proofs. The snapshot was never restored. |
| F | `ghog day --full=speed --whole-suite` through this worktree's launcher | Ended 2026-11-10 at 21:44:10+01:00, exit 2. Fresh executable preflight and static checks passed. Full measured 6,221 tests with 11 wall-only lifecycle errors: CPU 0.015625-0.156250s against the effective 0.250s band limit; wall 1.029650-6.201089s against 1.000s. No assertion failures, warnings or xfails were reported. Coverage and speed verdicts were withheld. |

Private shell and consumer evidence includes before/after environment and file
snapshots. The consumer runs took approximately 5.10 and 5.31 seconds including
setup, respectively. Trial-owned record state was removed and parent transient
environment restored. Raw identities, paths and records remain private.
The executable matrix includes three distributed barrier failures with
identifying exit 4 and 22 policy/configuration/isolation behavior cases.

## Requirement-to-evidence mapping

Rows follow the requirement's sixteen acceptance criteria in order.

| Criterion | Named check or executable case |
| --- | --- |
| Neither plugin selected | A empty selection; E `policies-0`, `prepared-0`; L `test_empty_hook_is_inert`. |
| Exactly selected plugins in both contexts; explicit duplicate loading | A all four selections; `test_every_stage_prepares_its_child` in `test_groundhog_activation`; L `test_hook_reuses_canonical_registration`; E `prepared-explicit`. |
| Selected import failure is identifying exit 4 | L `test_selected_import_errors_are_usage_errors`, `test_import_failure_has_no_registration`, `test_startup_failures_identify_opt_in_before_execution`. |
| Independent gate, ceilings, clocks, band and drift | G `test_one_cpu_window_keeps_initialization_hooks_cleanup_and_limits`, `test_a_run_proves_counts_drift_or_drops_the_proof`, `test_the_hook_judges_each_lifecycle_by_its_own_limit`; E `budget`, `gate-process-only`, `wall-only-gate`, `wall-only-both`, `cpu-only-overrun`. |
| Independent audit across lifecycle phases; collection excluded | P `test_all_process_events_cover_entire_protocol`; E `process`, `fixtures` and barrier cases. |
| Separate test/fixture permissions, ownership, timing and thread scope | P `test_fixture_precedence_and_credit`, `test_nested_dynamic_dependencies_and_cached_access`, `test_thread_and_copied_context_do_not_inherit_fixture_permission`; G lifecycle clock check; E `fixtures`, `workers-fixtures`. |
| Invalid declarations refuse before tests; valid strict declarations remain harmless | P `test_malformed_test_permission_prevents_setup`, `test_inherited_permissions_are_invalid`, `test_all_fixture_entries_are_validated`; A all selections; E `invalid-declaration`, three barrier cases. |
| Summary credit, unused permissions and controller aggregation | P `test_audit_only_summary_reports_only_exercised_own_scope_permissions`, `test_worker_records_merge_usage_and_keep_definitions_distinct`; A unused declarations; E `workers-aggregate`, `workers-fixtures`. |
| Strict no-home behavior; one writer and record continuity | G `test_without_an_ignored_home_the_gate_is_strict_and_writes_nothing`, `test_only_the_controller_collects`, `test_existing_record_round_trip_keeps_human_fields`; A record write; R. |
| Four defaults, ranges and precedence; identifying invalid settings | G `test_guarded_consumer_settings_in_both_registration_orders`, `test_guarded_settings_remain_usable_without_gate`, `test_invalid_settings_name_the_key`, `test_invalid_setting_exits_four_before_collection`; E `guard-late`, `tracked`, `override`. |
| Consumer package identity, independent imports and optional dependencies | L `test_real_canonical_imports_preserve_consumer_packages`; G `test_source_boundary_is_python310_and_stdlib_only`; P `test_standalone_source_contract`; E every behavior case imports consumer `tools` and `tests`, plus `optional-absent`. |
| Actual Windows Python 3.12/3.13 behavior and mandatory fresh 3.12 validation | E both actual interpreters; `test_missing_interpreter_never_installs` in `test_compatibility/test_environment_tdd.py`; `test_compatibility_preflight` unit package; F. |
| Below-3.12 refusal and repeatable 3.10 syntax validity | G `test_version_refusal_precedes_other_imports`; P `test_version_refusal_precedes_runtime_imports`; L `test_version_refusal_runs_before_newer_definitions`; `tools.lifecycle_compatibility.static_entry` run by check. |
| Repeatable isolation and anonymous trial in both contexts | A, E, W and T; `test_same_root_refresh_and_deselection` and `test_stage_rechecks_binding_before_spawn` in `test_groundhog_activation`. |
| Own suite preserves assertions, 100% tools coverage and no exemptions | [Step 8 fresh whole-suite speed and coverage evidence](#step-8-cpu-based-timing-acceptance-on-2026-11-11); F remains historical. Required declaration/reference scan classified below. |
| Adoption and supported-platform documentation | [Gate guide](../../wiki/how-to/enable-shared-lifecycle-gate.md), [audit guide](../../wiki/how-to/enable-shared-process-audit.md), [compatibility guide](../../wiki/how-to/validate-shared-pytest-compatibility.md), [limits reference](../../wiki/reference/test-lifecycle-limits.md). |

## Design-case traceability

| Design case | Evidence |
| --- | --- |
| Neither selected | A empty selection; E `policies-0`, `prepared-0`. |
| Gate only beside consumer packages | E `policies-1`, `prepared-1`, `gate-process-only`; L real canonical import check. |
| Audit only | E `policies-2`, `process`, `fixtures`; P all-process-events check. |
| Prepared plus explicit | E `prepared-explicit`; L canonical registration check. |
| Missing/blocked/unsupported selected policy | L startup-failure and version-refusal checks; G/P version checks. |
| Shared checkout disappears after preparation | L `test_each_loader_copy_handles_independent_removal`, `test_startup_failures_identify_opt_in_before_execution`. |
| Two shared checkouts bind one consumer | L `test_each_loader_copy_handles_independent_removal`; preparation PBT in `test_preparation/test_preparation_pbt.py`. |
| Live contract changes | L `test_all_source_contracts_precede_any_import`, startup-failure check. |
| Exempt test with unexempt session fixture | P `test_fixture_precedence_and_credit`, `test_failed_fixture_operation_unwinds`. |
| Exempt fixture requests unexempt fixture | P `test_nested_dynamic_dependencies_and_cached_access`; E `fixtures`. |
| Exempt fixture and test; fixture receives credit | P `test_fixture_precedence_and_credit`; E `workers-fixtures`. |
| Invalid unused fixture/module mark, serial and distributed | P all-fixture-entries and inherited-permissions checks; E `invalid` worker barrier scenario. |
| Valid declarations, audit absent, strict settings | A empty and lifecycle selections. |
| Tracked keys, gate absent, strict settings | G guarded-settings-without-gate check; A process selection; E `prepared-2`. |
| Fixture permission does not cross threads | P thread/copied-context check; E `fixtures`. |
| Fixture across workers and parameters | P fixture-identity/worker-record checks; E `workers-fixtures`. |
| No safe home | G strict no-home and ignore-byte checks. |
| Existing checkout record | G round-trip/controller checks; R. |
| Own validation missing Python 3.12 | Compatibility environment missing-interpreter check; preflight tests. |
| Consumer needs no second Python | T uses consumer interpreter directly; E optional-absence cases. |
| Anonymous real trial | T, both activation contexts and cleanup snapshots. |
| One invalid worker prevents every test start | E all three barrier scenarios verify peer announcement, no start, exit 4, diagnostic and reaped workers. |
| Embedded audit keeps outer dispatcher and ownership | P `test_nested_sessions_preserve_outer_owner`; E `nested`. |
| Bound root mismatch | L `test_roots_accept_descendants_but_not_siblings`; groundhog stage binding check. |
| Documented guard in either loading order | G guarded registration orders; E `guard-late`, `tracked`, `override`. |

## Historical Step 7 validation and declaration audit

The required `simulation_policy|lifecycle_cpu_record|LLM_SHARED_PROCESS_FIXTURES|process_allowed`
scan found policy implementation identifiers, documentation examples and
generated synthetic consumer declarations. None grants an actual carrying-suite
test or fixture process permission. Legacy module names have no live matches
in the scanned tests, tools, wiki, instructions or project configuration.

The user authorized continuing when measured CPU is within budget and only
wall time fails. That continuation preserves the automated non-green result;
it does not establish whole-suite coverage or speed acceptance. No limit or
assertion was weakened, and no process permission or duration exclusion was
added. The covered whole-suite stage completed with the wall-only errors in F;
its coverage and speed gates remain unproven. Record continuity passed after
that stage, preserving every previous eligible proof. Static checks and the
earlier affected run passed. These observations do not establish green release
acceptance at Step 7.

## Step 8 CPU-based timing acceptance on 2026-11-11

The maintainer subsequently requested an implemented policy: CPU at or below
the effective per-test limit passes lifecycle timing even when wall time
exceeds its reference. This replaces the old CPU-or-wall timing predicate.
The historical non-green Step 7 observation F above is retained. The fresh
results below establish the new policy and the previously unproven full gates.

| Check | Fresh observation |
| --- | --- |
| Strict CPU and wall boundary matrix | `test_one_cpu_window_keeps_initialization_hooks_cleanup_and_limits` covers CPU below/equal/above limit crossed with wall below/equal/above reference; clocks and full CPU window remain asserted. |
| Effective band and exception limits | `test_the_hook_judges_each_lifecycle_by_its_own_limit` and `test_exception_limit_and_drift_survive_wall_excess` cover equality and overruns, retaining CPU observations for proof/drift. |
| Independent failures | `test_cpu_within_budget_preserves_other_phase_failures` preserves setup/call/teardown failures and their text. Executable `wall-functional-failure` and `wall-process-failure` retain exit 1 with CPU below budget and wall excess. |
| Actual Python 3.12 compatibility preflight | The worktree's resolved full-speed day freshly passed all 41 checks: 30 policy cases and eleven Windows shell probes. New `wall-only-gate`, `wall-only-both`, `cpu-only-overrun` and independent-failure cases use controlled clocks without sleeps. |
| Actual Python 3.13.9 compatibility | Main-runtime `python -m tools.lifecycle_compatibility.runner <fresh-private-evidence> --all` passed all 41 checks with pytest 9.1.0 and xdist 3.8.0. |
| Resolved default day | Worktree `ghog day --whole-suite` finished at 13:46:40+01:00, exit 0, in 5m13.8s. Static checks and affected tests passed; coverage and speed were deliberately skipped. |
| Resolved whole-suite speed day | Worktree `ghog day --full=speed --whole-suite` finished at 13:52:06+01:00, exit 0, in 4m01.3s; full stage 59.3s, selection 6,288 tests. Configured `tools` coverage 100%, failures/warnings/xfails 0, duration outliers 0 and exclusions 0. Fresh `proof=speed`, `reused=none`, `state=done`. |

Replacement validation after review corrections and the permission-probe
watchdog repair passed on 2026-11-11. The worktree's whole-suite speed day
finished at 16:29:32+01:00 in 6m00s: 6,288 tests, 100% configured coverage,
zero failures, warnings, xfails, outliers and exclusions, with no reused stage.
Fresh Python 3.12 preflight and separate actual Python 3.13.9 execution each
passed 41/41 checks. The default day finished at 16:31:38+01:00 by reusing
that speed proof; no checks or tests ran in that invocation.

Both timing measurements, effective CPU limit and measured-run properties
remain available. Defaults, accepted exceptions, CPU band/proof/drift rules,
record schema and independent process permissions are unchanged. No duration
exclusion or carrying-suite process permission was added. Groundhog's separate
call-duration speed policy is unchanged. Linux and macOS remain unvalidated.
