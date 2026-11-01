"""Production notification cleanup with explicit event and observer observations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.acceptance.review_resume.notification_simulation import NotificationSchedule

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("failure", [KeyboardInterrupt, RuntimeError])
def test_wait_releases_its_observer_on_exception(tmp_path: Path, failure: type[BaseException]) -> None:
    """A cancelled or failed foreground wait stops and joins exactly once."""
    schedule = NotificationSchedule()
    adapter = schedule.adapter(tmp_path)
    with pytest.raises(failure), adapter:
        raise failure
    assert schedule.lifecycle == ["schedule", "start", "stop", "join"]
    adapter.__exit__()
    assert schedule.lifecycle == ["schedule", "start", "stop", "join"]


def test_notifications_consume_hints_without_wall_clock_waiting(tmp_path: Path) -> None:
    """The adapter clears each hint and preserves its requested wait duration."""
    interval = 30.0
    schedule = NotificationSchedule(lambda: True, lambda: False)
    with schedule.adapter(tmp_path) as adapter:
        assert adapter.wait(interval)
        assert not adapter.wait(interval)
    assert schedule.elapsed == 2 * interval
    assert not schedule.actions
    assert schedule.lifecycle == ["schedule", "start", "stop", "join"]


# eof
