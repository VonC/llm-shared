"""Claude lifecycle ledger boot-boundary tests.

Step 1 of v0.15.0 resume-paused, design Q28=A follow-up: an unproved boot
boundary discharges no ordinary work. With an unresolved boundary every listed
in-checkout transcript gets the lifecycle check, however old: an older
unmatched task stays pending, complete older history with matched ends still
proves absence, and missing, unreadable or incomplete history stays pending
under its own reason. Only a resolved boundary bounds older work, and a
pending boot decision keeps the decision pending, whatever counts its reasons
carry. A schedule closes only on its own deletion: a recurring firing, an
assumed seven-day expiry and a host restart close nothing, with durable or
session-only schedules alike. Each older transaction is shifted whole, so its
record times and its file's modification time agree; the expiry one ends
eight days before the bound turn (Q28=A review round 1).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any

import pytest

from tests.unit.tools.resume_paused_test_support import (
    UNRESOLVED_BOOT,
    FakeTranscriptSource,
    at,
    claude_profile,
    closed_turn,
    closing,
    jsonl,
    record,
    reply,
    resolved_boot,
    session_start,
    task_ended,
    typed,
)
from tests.unit.tools.test_resume_paused_claude_ledger.test_resume_paused_claude_ledger_tdd import (
    BOUND,
    OLD,
    PROCESS,
    SCOPE,
    WATCHER,
    Files,
    reasons,
)
from tools.resume_paused_claude_ledger import Absence, ClaudeLedger, LedgerDecision
from tools.resume_paused_profiles import (
    BootBoundary,
    BootDecision,
    BootObservation,
    Reason,
    boot_boundary,
)

NEW = "new.jsonl"
RECENT = timedelta(days=1)
STALE = timedelta(days=8)
UNRESOLVED_FROM_POLICY = boot_boundary(BootObservation(boot_created_at=at(30), now=at(600), uptime=timedelta(seconds=570)), None)
PENDING_CLOCK = BootDecision(BootBoundary.PENDING, None, (Reason("clock-backward-beyond-tolerance"),))
CREATED = ("CronCreate", {"id": "job1", "recurring": True, "durable": True})
UNRESOLVED_SCHEDULE = {"schedule-unresolved": 1}
MARKERLESS = [item for item in closed_turn() if item.get("uuid") != "start"]
MARKER_MISSING = {"generation-marker-missing": 1, "parent-missing": 1}
Scenario = tuple[list[dict[str, Any]], Files]


def evaluate(files: Files, boot: BootDecision, modified: dict[str, datetime] | None = None, **profile: Any) -> LedgerDecision:  # noqa: ANN401
    """Evaluate declared transcripts under a boot decision; ``OLD`` is modified before the boot at second 30."""
    data = {path: jsonl(value) if isinstance(value, list) else value for path, value in files.items()}
    source = FakeTranscriptSource(data, {OLD: at(0)} if modified is None else modified)
    return ClaudeLedger(claude_profile(**profile), source, lambda: PROCESS).evaluate(replace(SCOPE, boot_boundary=boot))


def test_policy_without_boot_semantics_leaves_the_boundary_unresolved() -> None:
    """With no profile recording boot semantics, the shipped policy bounds no history."""
    assert UNRESOLVED_FROM_POLICY.state is BootBoundary.UNRESOLVED
    assert UNRESOLVED_FROM_POLICY.boundary is None


def test_older_unmatched_task_under_an_unproved_boundary_is_pending() -> None:
    """An unresolved boundary keeps an older file's open start in scope."""
    decision = evaluate({OLD: closed_turn(WATCHER), BOUND: closed_turn()}, UNRESOLVED_FROM_POLICY)

    assert reasons(decision) == {"background-start-unmatched": 1}
    assert decision.account.files == 2  # noqa: PLR2004


def test_same_older_task_under_a_resolved_true_boot_is_discharged() -> None:
    """A resolved boundary bounds the older file's tasks: it is read for schedules only."""
    decision = evaluate({OLD: closed_turn(WATCHER), BOUND: closed_turn()}, resolved_boot(30))

    assert decision.absence is Absence.PROVED
    assert decision.account.files == 2  # noqa: PLR2004


def test_complete_older_history_with_matched_ends_proves_absence() -> None:
    """Under an unresolved boundary, older starts closed by their own ends still prove absence."""
    older = [*closed_turn(WATCHER, ("CronCreate", {"id": "job1"}), ("CronDelete", {"id": "job1"})), task_ended(50, "task1")]

    assert evaluate({OLD: older, BOUND: closed_turn()}, UNRESOLVED_BOOT).absence is Absence.PROVED


@pytest.mark.parametrize(
    ("older", "expected"),
    [
        (None, {"read-failed": 1}),
        (jsonl(closed_turn())[:-1], {"transcript-incomplete": 1}),
        (MARKERLESS, MARKER_MISSING),
    ],
)
def test_missing_or_incomplete_older_history_stays_pending(older: list[dict[str, Any]] | bytes | None, expected: dict[str, int]) -> None:
    """Unreadable, truncated or markerless older history proves nothing under an unresolved boundary."""
    assert reasons(evaluate({OLD: older, BOUND: closed_turn()}, UNRESOLVED_BOOT)) == expected


def test_older_file_without_its_marker_is_checked_only_without_a_resolved_boundary() -> None:
    """A schedule-only read past a resolved boot skips the generation check that an unresolved boundary requires."""
    files: Files = {OLD: MARKERLESS, BOUND: closed_turn()}

    assert evaluate(files, resolved_boot(30)).absence is Absence.PROVED
    assert reasons(evaluate(files, UNRESOLVED_BOOT)) == MARKER_MISSING


def test_incomplete_enumeration_stays_pending_under_an_unresolved_boundary() -> None:
    """Without the complete listing, no boundary state can prove absence."""
    source = FakeTranscriptSource({}, complete=False)

    decision = ClaudeLedger(claude_profile(), source, lambda: PROCESS).evaluate(replace(SCOPE, boot_boundary=UNRESOLVED_BOOT))

    assert decision.reasons == (Reason("enumeration-incomplete"),)


@pytest.mark.parametrize(
    ("boot", "expected"),
    [
        (PENDING_CLOCK, {"clock-backward-beyond-tolerance": 1}),
        (BootDecision(BootBoundary.PENDING, None, ()), {"boot-boundary-pending": 1}),
        (BootDecision(BootBoundary.PENDING, None, (Reason("boot-evidence-invalid", 0),)), {"boot-evidence-invalid": 1}),
        (BootDecision(BootBoundary.PENDING, None, (Reason("boot-evidence-invalid", -1),)), {"boot-evidence-invalid": 1}),
    ],
)
def test_pending_boot_decision_keeps_absence_pending(boot: BootDecision, expected: dict[str, int]) -> None:
    """A pending boot keeps an otherwise clean decision pending, whatever counts its reasons carry."""
    assert reasons(evaluate({BOUND: closed_turn()}, boot)) == expected


def aged(records: list[dict[str, Any]], age: timedelta) -> list[dict[str, Any]]:
    """Move a whole transaction ``age`` earlier: every recorded timestamp shifts by the same amount."""
    return [
        {**item, "timestamp": (datetime.fromisoformat(item["timestamp"]) - age).isoformat()} if "timestamp" in item else item
        for item in records
    ]


def last_written(records: list[dict[str, Any]]) -> datetime:
    """Return the instant of a transaction's last stamped record, its file's modification time."""
    return max(datetime.fromisoformat(item["timestamp"]) for item in records if "timestamp" in item)


def recurring_firing() -> Scenario:
    """Build a recurring schedule created a day earlier whose firing completed as a task carrying the job id."""
    return aged([*closed_turn(CREATED), task_ended(50, "job1")], RECENT), {BOUND: closed_turn()}


def expired_by_assumption() -> Scenario:
    """Build a schedule whose whole transaction ended eight days before the bound turn, never deleted."""
    return aged(closed_turn(CREATED), STALE), {BOUND: closed_turn()}


def restarted_host() -> Scenario:
    """Build a schedule created a day earlier, then a host restart: a later startup generation, no deletion."""
    restart = [record("mode"), session_start("s2", 45), typed("in2", "s2", 46), reply("r2", "in2", 47), *closing("t2", "r2", 48)]
    return aged(closed_turn(CREATED), RECENT), {NEW: restart, BOUND: closed_turn()}


SCENARIOS = [recurring_firing(), expired_by_assumption(), restarted_host()]


def evaluate_scenario(scenario: Scenario, boot: BootDecision, **profile: Any) -> LedgerDecision:  # noqa: ANN401
    """Evaluate an older transaction, modified at its last record, with the scenario's later files."""
    older, files = scenario
    return evaluate({OLD: older, **files}, boot, {OLD: last_written(older)}, **profile)


def test_expiry_fixture_creates_its_schedule_more_than_seven_days_before_the_bound_turn() -> None:
    """The expiry case is not vacuous: its ``CronCreate`` result predates the bound turn's close by over seven days."""
    older, files = expired_by_assumption()
    created = next(datetime.fromisoformat(item["timestamp"]) for item in older if "toolUseResult" in item)
    bound = files[BOUND]

    assert isinstance(bound, list)
    assert last_written(bound) - created > timedelta(days=7)
    assert last_written(older) < at(30)


@pytest.mark.parametrize("scenario", SCENARIOS)
@pytest.mark.parametrize("boot", [UNRESOLVED_BOOT, resolved_boot(30)])
def test_durable_schedule_without_its_own_deletion_stays_unresolved(scenario: Scenario, boot: BootDecision) -> None:
    """A firing, an untested seven-day expiry and a restart close no schedule, before or after a resolved boot."""
    assert reasons(evaluate_scenario(scenario, boot)) == UNRESOLVED_SCHEDULE


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_session_only_schedules_are_not_discharged_by_an_unproved_restart(scenario: Scenario) -> None:
    """Session-only schedules skip older files only past a resolved boot; an unresolved one keeps them."""
    assert reasons(evaluate_scenario(scenario, UNRESOLVED_BOOT, durable_schedules=False)) == UNRESOLVED_SCHEDULE
    assert evaluate_scenario(scenario, resolved_boot(30), durable_schedules=False).absence is Absence.PROVED


# eof
