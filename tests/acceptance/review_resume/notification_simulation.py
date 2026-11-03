"""Scheduled notification observations for the real foreground wait loop.

Callbacks advance repository state at explicit wait boundaries. No thread,
observer, child process or wall-clock sleep is created by this driver.
"""

from __future__ import annotations

import sys
from collections import deque
from io import StringIO
from threading import Event
from typing import TYPE_CHECKING

from tools.review_resume_notifications import WatchdogNotificationAdapter

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from watchdog.events import FileSystemEventHandler


def assert_quiet() -> None:
    """Require silent captured CLI streams before a terminal result."""
    assert isinstance(sys.stdout, StringIO)
    assert isinstance(sys.stderr, StringIO)
    assert sys.stdout.getvalue() == sys.stderr.getvalue() == ""


class NotificationSchedule(Event):
    """Supply virtual event waits and record production adapter cleanup."""

    def __init__(self, *actions: Callable[[], bool]) -> None:
        """Declare a finite sequence; an undeclared wait is always an error."""
        super().__init__()
        self.actions = deque(actions)
        self.elapsed = 0.0
        self.lifecycle: list[str] = []
        self.dirty = False

    def adapter(self, directory: Path) -> WatchdogNotificationAdapter:
        """Build the production adapter with thread-free observation ports."""
        return WatchdogNotificationAdapter(
            directory, observer_factory=lambda: self, event_factory=lambda: self,
        )

    def schedule(self, event_handler: FileSystemEventHandler, path: str, /, *, recursive: bool) -> object:
        """Record the one non-recursive subscription."""
        del event_handler, path
        assert not recursive
        self.lifecycle.append("schedule")
        return self

    def start(self) -> None:
        """Record observer startup without creating a thread."""
        self.lifecycle.append("start")

    def stop(self) -> None:
        """Record observer shutdown."""
        self.lifecycle.append("stop")

    def join(self, timeout: float | None = None) -> None:
        """Observe the bounded join contract without waiting."""
        assert timeout == 1.0
        self.lifecycle.append("join")

    def set(self) -> None:
        """Retain a notification hint."""
        self.dirty = True

    def clear(self) -> None:
        """Consume accumulated hints."""
        self.dirty = False

    def wait(self, timeout: float | None = None) -> bool:
        """Advance virtual time and execute exactly one scheduled action."""
        assert timeout is not None
        assert timeout > 0
        assert self.actions, "unexpected notification wait; declare the next observation"
        self.elapsed += timeout
        return self.actions.popleft()() or self.dirty


# eof
