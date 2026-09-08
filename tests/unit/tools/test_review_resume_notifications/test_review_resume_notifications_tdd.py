"""Exercise native hints, missed notifications, startup failure, and cleanup."""

from __future__ import annotations

from threading import Event
from typing import TYPE_CHECKING

import pytest
from watchdog.events import (
    DirModifiedEvent,
    FileCreatedEvent,
    FileMovedEvent,
    FileOpenedEvent,
)

from tools.review_resume_notifications import (
    WatchdogNotificationAdapter,
    _RequestEventHandler,
)
from tools.review_resume_wait import GlobalReviewerWait, GlobalWaitOutcome

if TYPE_CHECKING:
    from pathlib import Path

    from watchdog.events import FileSystemEventHandler


class ObserverDouble:
    """Record one subscription lifecycle and inject platform startup failures."""

    def __init__(self, *, fail: bool = False) -> None:
        """Initialize isolated lifecycle counters."""
        self.fail = fail
        self.starts = 0
        self.stops = 0
        self.joins = 0
        self.handler: FileSystemEventHandler | None = None

    def schedule(self, event_handler: FileSystemEventHandler, path: str, *, recursive: bool) -> None:
        """Record only the configured non-recursive subscription."""
        assert path
        assert not recursive
        self.handler = event_handler

    def start(self) -> None:
        """Simulate an unavailable native watcher when requested."""
        self.starts += 1
        if self.fail:
            raise OSError

    def stop(self) -> None:
        """Record shutdown."""
        self.stops += 1

    def join(self, timeout: float | None = None) -> None:
        """Record bounded cleanup, including a thread that never started."""
        assert timeout == 1.0
        self.joins += 1
        if self.fail:
            raise RuntimeError


def test_filters_and_coalesces_request_hints() -> None:
    """Unrelated files and read events cannot cause an idle rescan loop."""
    dirty = Event()
    handler = _RequestEventHandler(dirty)
    name = "a.review-requested.code.v0.11.0.example.md"
    for event in (DirModifiedEvent(".reviews"), FileOpenedEvent(name), FileCreatedEvent("a.notes.md")):
        handler.on_any_event(event)
        assert not dirty.is_set()
    handler.on_any_event(FileMovedEvent("temporary", name))
    handler.on_any_event(FileCreatedEvent(name))
    assert dirty.is_set()


@pytest.mark.parametrize("fail", [False, True])
def test_one_observer_and_bounded_polling(tmp_path: Path, *, fail: bool) -> None:
    """Lost notifications still return at the deadline; no observer is restarted."""
    observer = ObserverDouble(fail=fail)
    dirty = Event()
    adapter = WatchdogNotificationAdapter(tmp_path, observer_factory=lambda: observer, event_factory=lambda: dirty)
    with adapter:
        dirty.set()
        assert adapter.wait(0)
        assert not adapter.wait(0)
    assert observer.starts == 1
    assert observer.stops == 1
    assert observer.joins == 1


def test_cancel_releases_observer(tmp_path: Path) -> None:
    """Cancellation cannot leave the native watcher subscribed."""
    observer = ObserverDouble()
    with pytest.raises(KeyboardInterrupt), WatchdogNotificationAdapter(tmp_path, observer_factory=lambda: observer):
        raise KeyboardInterrupt
    assert observer.stops == 1
    assert observer.joins == 1

@pytest.mark.parametrize("notified", [False, True])
def test_wired_wait_coalesces_hints_and_rescans_after_fallback(tmp_path: Path, *, notified: bool) -> None:
    """Native hints and missed events both reach the same authoritative foreground rescan."""
    observer = ObserverDouble()
    dirty = Event()
    adapter = WatchdogNotificationAdapter(tmp_path, observer_factory=lambda: observer, event_factory=lambda: dirty)
    scans: list[None] = []
    fallbacks: list[None] = []
    candidate = object()
    expected_scans = 2

    def rescan() -> tuple[object, ...]:
        """The filesystem becomes ready only on the second authoritative scan."""
        scans.append(None)
        return (candidate,) if len(scans) == expected_scans else ()

    waiter = GlobalReviewerWait(
        rescan_candidates=rescan, wait_for_notification=adapter.wait,
        fallback_poll=lambda: fallbacks.append(None), claim_candidate=lambda _: True,
        poll_interval_seconds=0.001,
    )
    with adapter:
        assert observer.handler is not None
        if notified:
            for _ in range(50):
                observer.handler.on_any_event(FileCreatedEvent("a.review-requested.code.v0.11.0.example.md"))
        assert not scans
        result = waiter.wait()
    assert result.outcome is GlobalWaitOutcome.FOUND
    assert len(scans) == expected_scans
    assert len(fallbacks) == int(not notified)
    assert observer.starts == observer.stops == 1
