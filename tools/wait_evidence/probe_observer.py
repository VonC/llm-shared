"""Independent event-driven source timer and collector for one explicit trial.

Watchdog notifications wake ordinary Python, never a model. Native turn evidence
is bound to the operator-selected registering turn. Timing markers cannot arm a
route. The finite duplicate observation and telemetry drain remain separate.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from threading import Event
from typing import TYPE_CHECKING
from uuid import uuid4

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .collector import Collector
from .models import (
    EvidenceRecord,
    JsonObject,
    TrialManifest,
    number_value,
    object_value,
)
from .prototype import CodexQueue, Prototype, Route
from .reports import write_report
from .telemetry import Telemetry

if TYPE_CHECKING:
    from collections.abc import Callable


def record(directory: Path, kind: str, at: float, data: JsonObject) -> None:
    """Append one identified local measurement without claiming native coverage."""
    manifest = object_value(json.loads((directory / "manifest.json").read_text(encoding="utf-8")))
    event: JsonObject = {key: manifest[key] for key in ("schema", "host", "build", "thread", "profile", "source_id")}
    event.update(type="probe_event", event_id=str(uuid4()), kind=kind, at=at, data=data)
    with (directory / "probe-events.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


class Changed(FileSystemEventHandler):
    """Coalesce notifications only for explicitly selected evidence streams."""

    def __init__(self, paths: set[Path], ready: Event) -> None:
        """Bind the selected paths to one coalesced notification."""
        self.paths, self.ready = paths, ready

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Wake for modifications, replacement or deletion of a selected file."""
        candidates = (event.src_path, event.dest_path)
        if event.event_type in {"modified", "created", "deleted", "moved"} and any(
                path and Path(os.fsdecode(path)).resolve() in self.paths for path in candidates):
            self.ready.set()


class Observation:
    """Drive the source with a native port; replay cannot extend the first final window."""

    def __init__(self, directory: Path, registering_turn: str, route: Route) -> None:
        """Bind an existing registered trial and its exact registering turn."""
        self.prototype = Prototype(directory)
        self.raw = object_value(json.loads((directory / "manifest.json").read_text(encoding="utf-8")))
        self.manifest = TrialManifest.from_dict(self.raw)
        self.adapter, self.collector = Telemetry(self.manifest), Collector(self.manifest)
        self.registering_turn, self.route = registering_turn, route
        self.noted: set[str] = set()
        self.final_at: float | None = None

    def _note(self, kind: str, at: float, data: JsonObject) -> None:
        if kind not in self.noted:
            self.noted.add(kind)
            record(self.prototype.directory, kind, at, data)

    def _native(self, event: EvidenceRecord) -> None:
        if event.kind == "native_interruption":
            self.prototype.suppress("interrupted", event.at)
        if event.kind == "native_turn_complete" and event.data.get("turn_id") == self.registering_turn:
            self.prototype.normal_end(event.at, "direct-turn-evidence")
            self._note("normal_turn_end", event.at, {"evidence": event.location, "origin": "native"})
        if event.kind == "native_turn_complete" and event.data.get("last_agent_message") == "WAIT_TEST_DONE":
            self._remember_final(event.at)
            self._note("final_turn_end", event.at, {"marker": "WAIT_TEST_DONE", "evidence": event.location})

    def _remember_final(self, at: float) -> None:
        self.final_at = at if self.final_at is None else min(self.final_at, at)

    def tick(self, now: float) -> float:
        """Drain a fixed telemetry snapshot, update the timer and return the next deadline."""
        events = list(self.adapter.snapshot(now))
        # Restore the existing journal before replaying native evidence. Work
        # remains linear in newly read records, independent of retained history.
        for event in events:
            self.collector.ingest(event)
            if event.kind == "final_turn_end":
                if event.data.get("marker") == "WAIT_TEST_DONE":
                    self._remember_final(event.at)
                    self.noted.add(event.kind)
            else:
                self.noted.add(event.kind)
        for event in events:
            self._native(event)
        state = self.prototype.snapshot()
        start = number_value(state, "source_start")
        self._note("source_start", start, {})
        # Registration is an observed upper bound on submitted-prompt time.
        # The operator can record the exact submission before this is needed.
        self._note("benchmark_prompt", start, {"origin": "registration-upper-bound"})
        baseline = self.raw["mode"] == "baseline"
        if not baseline:
            result = self._advance(now)
            state = self.prototype.snapshot()
            if state["ready_at"] is not None:
                self._note("source_ready", number_value(state, "ready_at"), {})
            if result in {"accepted", "receipt-unknown", "suppressed", "bridge-failed", "closed", "stale"}:
                self._note("delivery", now, {"status": result})
        return self._deadline(state, baseline=baseline)

    def _advance(self, now: float) -> str:
        """Keep observing an uncertain acceptance without retrying its durable intent."""
        try:
            return self.prototype.advance(now, self.route)
        except (OSError, subprocess.SubprocessError) as error:
            self._note("delivery", now, {"status": "receipt-unknown", "error_type": type(error).__name__})
            return "receipt-unknown"

    def _deadline(self, state: JsonObject, *, baseline: bool) -> float:
        if baseline:
            normal = state.get("normal_end_at") or state.get("operator_normal_end_at")
            start = float(normal) if isinstance(normal, int | float) else number_value(state, "source_start")
            return start + number_value(self.raw, "baseline_seconds") + self.manifest.drain_bound
        if self.final_at is not None:
            return self.final_at + self.manifest.duplicate_window + self.manifest.drain_bound
        due = number_value(state, "due_at")
        return due + self.manifest.wake_bound + self.manifest.duplicate_window + self.manifest.drain_bound

    def run(self, wait: Callable[[float], object]) -> None:
        """Wait on source deadlines or file notifications, then write one immutable report."""
        drain_started: float | None = None
        while True:
            now = time.time()
            deadline = self.tick(now)
            drain_started = self._start_drain(now, drain_started)
            if now >= deadline:
                break
            state = self.prototype.snapshot()
            due = number_value(state, "due_at")
            next_at = min(deadline, due) if now < due else deadline
            if self.final_at is not None and now < self.final_at + self.manifest.duplicate_window:
                next_at = min(next_at, self.final_at + self.manifest.duplicate_window)
            wait(max(0, next_at - now))
        for event in self.adapter.snapshot(now):
            self.collector.ingest(event)
        for event in self.adapter.finish(now):
            self.collector.ingest(event)
        self.collector.drained(now, monotonic_at=time.monotonic())
        write_report(self.prototype.directory / "report.json", self.collector.report(now))

    def _start_drain(self, now: float, previous: float | None) -> float | None:
        """Start accounting once per final boundary, without rescanning on every file event."""
        if self.final_at is not None and now >= self.final_at + self.manifest.duplicate_window and previous != self.final_at:
            self.collector.drained(now, monotonic_at=time.monotonic())
            return self.final_at
        return previous


def observe(directory: Path, registering_turn: str, executable: Path | None) -> None:
    """Run from an independent ordinary process after registration exists."""
    manifest = TrialManifest.from_dict(object_value(json.loads((directory / "manifest.json").read_text(encoding="utf-8"))))
    route = Route("unavailable", lambda: "unavailable", lambda _: None)
    if executable is not None and manifest.host == "codex" and manifest.arm == "B-prototype":
        host = CodexQueue(executable, manifest)
        route = Route("direct-turn-evidence", host.status, host.send)
    observation = Observation(directory, registering_turn, route)
    paths = {stream.path.resolve() for stream in manifest.streams}
    ready = Event()
    watcher = Observer()
    for parent in {path.parent for path in paths}:
        watcher.schedule(Changed(paths, ready), str(parent), recursive=False)
    watcher.start()

    def wait(seconds: float) -> None:
        ready.wait(seconds)
        ready.clear()

    try:
        observation.run(wait)
    finally:
        watcher.stop()
        watcher.join()


# eof
