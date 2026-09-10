"""Native observer lifecycle tests kept outside the pure wait-policy test leaf."""

from __future__ import annotations

from threading import Event
from typing import TYPE_CHECKING

from tools.review_resume_notifications import WatchdogNotificationAdapter

if TYPE_CHECKING:
    from pathlib import Path


class TestWatchdogNotificationAdapter:
    """Exercise native notification as a bounded, non-authoritative hint."""

    def test_wait_starts_and_stops_one_non_recursive_observer(self, tmp_path: Path) -> None:
        """An event hint performs no artifact read and always closes the observer."""
        scheduled: list[tuple[object, str, bool]] = []

        class FakeObserver:
            """Record the adapter lifecycle without starting a platform watcher."""

            def schedule(self, handler: object, path: str, *, recursive: bool) -> None:
                """Record the bounded directory subscription."""
                scheduled.append((handler, path, recursive))

            def start(self) -> None:
                """Provide the observer start seam."""

            def stop(self) -> None:
                """Provide the observer stop seam."""

            def join(self, timeout: float | None = None) -> None:
                """Provide the observer join seam."""

        class FakeEvent(Event):
            """Return a deterministic native-event hint."""

            def wait(self, timeout: float | None = None) -> bool:
                """Record that one bounded wait was requested."""
                assert timeout == 1.0
                return True

        adapter = WatchdogNotificationAdapter(
            tmp_path,
            observer_factory=FakeObserver,
            event_factory=FakeEvent,
        )

        with adapter:
            assert adapter.wait(1.0)
        assert scheduled[0][1:] == (str(tmp_path), False)

# eof
