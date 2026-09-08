"""One process-local native observer with bounded polling fallback.

Only recognized request writes mark the wait dirty. Callbacks never project
status; the foreground consumer coalesces hints and rescans authoritatively.
"""

from __future__ import annotations

import os
from contextlib import suppress
from pathlib import Path
from threading import Event
from typing import TYPE_CHECKING, Protocol, Self

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from tools.review_artifact_registry import (
    RegisteredArtifactKind,
    ReviewArtifactRegistry,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class ObserverPort(Protocol):
    """The lifecycle of one non-recursive native directory subscription."""

    def schedule(self, event_handler: FileSystemEventHandler, path: str, /, *, recursive: bool) -> object:
        """Subscribe to directory changes."""
        ...

    def start(self) -> None:
        """Start delivering hints."""
        ...

    def stop(self) -> None:
        """Request observer shutdown."""
        ...

    def join(self, timeout: float | None = None) -> None:
        """Bound observer cleanup."""
        ...


class _RequestEventHandler(FileSystemEventHandler):
    """Coalesce recognized request writes into an in-memory event."""

    def __init__(self, dirty: Event) -> None:
        """Bind the event and closed artifact registry."""
        super().__init__()
        self._dirty = dirty
        self._registry = ReviewArtifactRegistry()

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Ignore reads, directories, and unrelated files without filesystem IO."""
        if event.is_directory or event.event_type not in {"created", "modified", "moved", "deleted", "closed"}:
            return
        for path in (event.src_path, event.dest_path):
            registered = self._registry.parse_name(Path(os.fsdecode(path)).name)
            if registered is not None and registered.kind is RegisteredArtifactKind.REQUEST:
                self._dirty.set()
                return


class WatchdogNotificationAdapter:
    """Own one observer for the whole wait and fall back when startup fails."""

    def __init__(
        self,
        watch_directory: Path,
        *,
        observer_factory: Callable[[], ObserverPort] = Observer,
        event_factory: Callable[[], Event] = Event,
    ) -> None:
        """Bind injectable ports; construction performs no IO."""
        self._directory = watch_directory
        self._factory = observer_factory
        self._dirty = event_factory()
        self._observer: ObserverPort | None = None

    def __enter__(self) -> Self:
        """Subscribe before the initial scan, or retain timed polling alone."""
        observer = self._factory()
        try:
            observer.schedule(_RequestEventHandler(self._dirty), str(self._directory), recursive=False)
            observer.start()
        except (OSError, RuntimeError):
            observer.stop()
            # A failed startup may never have started the observer thread.
            with suppress(RuntimeError):
                observer.join(timeout=1.0)
        else:
            self._observer = observer
        return self

    def wait(self, seconds: float) -> bool:
        """Block quietly and consume accumulated hints before the next scan."""
        notified = self._dirty.wait(seconds)
        self._dirty.clear()
        return notified

    def __exit__(self, *_exception: object) -> None:
        """Release the subscription after success, failure, or cancellation."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=1.0)
            self._observer = None


# eof
