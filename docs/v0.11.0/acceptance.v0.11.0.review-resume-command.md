# Review resume acceptance scenarios for v0.11.0

Executable mapping for the 19 criteria in the
[feature request](feature-request.v0.11.0.review-resume-command.md).
Results are recorded in the [validation plan](plan.v0.11.0.review-resume-command.validation.md).

## Scenario locations for review resumption

- [Sequential lifecycle](../../tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_acceptance_tdd.py): real public launchers, both review families, fresh-lease displacement, human authorization, and actual `pw skill` release.
- [Migration](../../tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_migration_tdd.py): root and former-default evidence, collisions, damaged recovery, unsafe homes, and repeated status.
- [Identity](../../tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_identity_tdd.py): Claude, Codex, Gemini, unknown, legacy gaps.
- [Conflict](../../tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_conflict_tdd.py): recorded role-nature conflict, Stop and Override.
- [Concurrency](../../tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_concurrency_tdd.py): independent waiting processes, one claim winner, ambiguity, quiet cancellation.
- [Parked wait](../../tests/acceptance/review_resume/test_review_resume_acceptance/test_review_resume_parked_wait_tdd.py): a wait held across the human gate or release, woken by a later round or family.
- [Public documentation](../../tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py): connected current pages and canonical resume behavior.

## Feature criterion to executable scenario mapping

| Criterion | Test names |
| --- | --- |
| AC01 | `test_every_runtime_artifact_uses_the_declared_ignored_home` |
| AC02 | `test_every_runtime_artifact_uses_the_declared_ignored_home`; `test_resume_checks_migrates_rechecks_then_claims` |
| AC03 | `test_status_migrates_complete_sets_once_without_changing_evidence`; `test_unsafe_layout_stops_before_identity_or_ownership_changes` |
| AC04 | `test_resume_checks_migrates_rechecks_then_claims`; `test_unsafe_layout_stops_before_identity_or_ownership_changes` |
| AC05 | `test_public_status_preserves_bytes_and_reports_both_hosts`; `test_status_migrates_complete_sets_once_without_changing_evidence` |
| AC06 | `test_selected_identity_backfills_all_runtime_evidence_and_leaves_counterpart_missing`; `test_public_status_preserves_bytes_and_reports_both_hosts` |
| AC07 | `test_selected_identity_backfills_all_runtime_evidence_and_leaves_counterpart_missing` |
| AC08 | `test_conflict_stop_makes_no_partial_backfill_and_returns_all_evidence` |
| AC09 | `test_conflict_stop_makes_no_partial_backfill_and_returns_all_evidence`; `test_override_preserves_conflict_and_fills_only_missing_selected_role` |
| AC10 | `test_selected_identity_backfills_all_runtime_evidence_and_leaves_counterpart_missing` |
| AC11 | `test_legacy_role_prompt_is_read_only_and_explicit_role_continues` |
| AC12 | `test_competing_reviewers_have_one_winner_and_loser_waits_for_replacement`; `test_wait_survives_convergence_and_conclusion_then_wakes`; `test_simultaneous_requests_return_ambiguity_without_claiming` |
| AC13 | `test_bare_resume_claims_before_fresh_lease_continuation`; `test_release_retains_unique_transcript_and_no_session_secrets` |
| AC14 | `test_bare_resume_claims_before_fresh_lease_continuation`; `test_legacy_role_prompt_is_read_only_and_explicit_role_continues` |
| AC15 | `test_resume_public_docs_describe_shipped_waiting_and_automatic_pickup` |
| AC16 | `test_every_runtime_artifact_uses_the_declared_ignored_home`; `test_unsafe_layout_stops_before_identity_or_ownership_changes` |
| AC17 | `test_unsafe_layout_stops_before_identity_or_ownership_changes` |
| AC18 | `test_status_migrates_complete_sets_once_without_changing_evidence`; `test_unsafe_layout_stops_before_identity_or_ownership_changes` |
| AC19 | `test_graceful_foreground_cancellation_has_one_result_and_no_durable_waiter`; `test_simultaneous_requests_return_ambiguity_without_claiming` |

## Acceptance evidence boundaries for resume orchestration

Scenario fixtures simulate the LLM instruction sequence from the exact text
`resume` and run support operations in separate processes. They do not claim
to execute an LLM. Exchange operations run as `python -m
tools.review_exchange_cli`, a real isolated child over the same CLI the
launcher wraps; `rvw_status.bat` and `prompt_workflow.bat` are still driven
through their batch launchers, so the shipped shims keep acceptance coverage. The instruction/provider suites independently validate the
canonical sequence and thin adapters. Cancellation injects a graceful interrupt
at the notification wait boundary after real preflight and discovery.
All runtime role transitions, migration, Git ignore checks, status and competing
reviewer claims use production behavior. Slow process setup stays in fixtures;
scenario assertions remain in measured tests.

The existing Step 0/5 performance guards retain their timing and operation-count
bounds. Existing schema, migration recovery, notification fallback, role, adapter,
requestor and reviewer regression suites remain part of the mandatory validation
set. The closed host and layout matrices need no new property-based generator;
the existing state and ownership property tests continue to exercise their domains.
