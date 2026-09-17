"""Durable synthetic timer harness for provisional native-wake experiments.

Each explicit ignored run owns a small SQLite database. This is independent of
the future shared service. A committed send intent prevents automatic retries
when a native client accepts a message but its acknowledgement is lost.
Host I/O releases the write lock, with authoritative eligibility checked again.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Empty
from typing import TYPE_CHECKING
from uuid import UUID

from .models import JsonObject, number_value, object_value, reject, text_value

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

    from .models import TrialManifest

GATES = frozenset({"direct-turn-evidence", "host-gated-turn-end"})
SUPPRESSIONS = frozenset({"stop", "cancel", "interrupted", "closed", "stale", "bridge-failed"})


@dataclass(frozen=True)
class Route:
    """Inject proven host gating, recipient validation and native delivery."""

    gate: str
    status: Callable[[], str]
    send: Callable[[str], str | None]


def run_directory(path: Path) -> Path:
    """Require an explicit run beneath the ignored evidence directory."""
    resolved = path.resolve()
    if not path.is_absolute() or "a.shared-wait-service" not in resolved.parts[:-1]:
        reject("Use an absolute run path beneath a.shared-wait-service")
    return resolved


class Prototype:
    """Persist readiness, gates, suppression and consumption; keep host I/O outside transactions."""

    def __init__(self, directory: Path) -> None:
        """Open one selected existing run; never discover the newest run."""
        self.directory = run_directory(directory)
        self.database = self.directory / "prototype.sqlite3"

    @classmethod
    def create(cls, directory: Path, registration: JsonObject) -> Prototype:
        """Reserve fresh state without overwriting an earlier experiment."""
        for key in ("thread", "profile", "source_id", "wait_id", "event_id"):
            text_value(registration, key)
        start, due = number_value(registration, "source_start"), number_value(registration, "due_at")
        if due <= start:
            reject("Source due time must follow source start")
        instance = cls(directory)
        instance.directory.mkdir(parents=True, exist_ok=True)
        # Exclusive reservation protects previous and partially created runs.
        instance.database.touch(exist_ok=False)
        state: JsonObject = {**registration, "ready_at": None, "normal_end_at": None,
                             "gate": None, "operator_normal_end_at": None, "suppressed": None,
                             "delivery": "not-attempted", "consumed_at": None,
                             "duplicate_consumptions": 0, "receipt": None}
        with instance._connection() as connection:
            connection.execute("CREATE TABLE state (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL)")
            connection.execute("INSERT INTO state VALUES (1, ?)", (json.dumps(state),))
        return instance

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection]:
        connection = sqlite3.connect(f"{self.database.as_uri()}?mode=rw", uri=True)
        try:
            connection.execute("PRAGMA synchronous=FULL")
            with connection:
                yield connection
        finally:
            connection.close()

    @contextmanager
    def _edit(self) -> Generator[JsonObject]:
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            state = object_value(json.loads(connection.execute("SELECT value FROM state WHERE id=1").fetchone()[0]))
            yield state
            connection.execute("UPDATE state SET value=? WHERE id=1", (json.dumps(state),))

    def snapshot(self) -> JsonObject:
        """Return a durable observation without changing delivery state."""
        with self._connection() as connection:
            return object_value(json.loads(connection.execute("SELECT value FROM state WHERE id=1").fetchone()[0]))

    def mark_normal_end(self, at: float) -> None:
        """Record an operator measurement; this marker never arms delivery."""
        with self._edit() as state:
            state["operator_normal_end_at"] = number_value({"at": at}, "at")

    def normal_end(self, at: float, gate: str) -> None:
        """Arm only from a route's proven direct or host-gated normal-end fact."""
        if gate not in GATES:
            reject("Unproven normal-end gate")
        with self._edit() as state:
            if at < number_value(state, "source_start"):
                reject("Normal-end precedes registration")
            if state["normal_end_at"] is None:
                state["normal_end_at"], state["gate"] = number_value({"at": at}, "at"), gate

    def suppress(self, reason: str, at: float) -> None:
        """Persist a terminal interruption while retaining any source outcome."""
        if reason not in SUPPRESSIONS:
            reject("Unknown suppression reason")
        with self._edit() as state:
            state["suppressed"], state["suppressed_at"] = reason, number_value({"at": at}, "at")

    def advance(self, now: float, route: Route) -> str:
        """Check native status outside transactions, then revalidate before sending."""
        now = number_value({"at": now}, "at")
        with self._edit() as state:
            result = self._prepare(state, now, route)
            if result != "send":
                return result
        status = route.status()
        with self._edit() as state:
            # Cancellation or a competing intent during host I/O wins.
            result = self._prepare(state, now, route)
            if result != "send":
                return result
            if status != "idle":
                if status in SUPPRESSIONS:
                    state["suppressed"], state["suppressed_at"] = status, now
                return status
            message = self._message(state)
            state["delivery"], state["attempted_at"] = "receipt-unknown", now
        # Intent is durable before host I/O. Exceptions deliberately retain it.
        receipt = route.send(message)
        if receipt:
            self.receipt(receipt)
            return "accepted"
        return "receipt-unknown"

    @staticmethod
    def _prepare(state: JsonObject, now: float, route: Route) -> str:
        if state.get("baseline") is True or now < number_value(state, "due_at"):
            return "waiting"
        if state["ready_at"] is None:
            state["ready_at"], state["result"] = now, "synthetic-source-complete"
        if state["suppressed"] is not None:
            return "suppressed"
        if state["delivery"] != "not-attempted":
            return text_value(state, "delivery")
        if route.gate not in GATES or state["gate"] != route.gate:
            return "retained-result-only"
        return "send"

    @staticmethod
    def _message(state: JsonObject) -> str:
        identity = {key: state[key] for key in ("thread", "wait_id", "event_id", "source_id", "result")}
        return ("Synthetic wait ready: " + json.dumps(identity, sort_keys=True)
                + ". Validate every identity against the manifest, consume the durable event once "
                "with the probe consume action, then finish with exactly WAIT_TEST_DONE.")

    def receipt(self, receipt: str) -> None:
        """Attach an acknowledgement to the existing send intent, never resend."""
        with self._edit() as state:
            if state["delivery"] not in {"receipt-unknown", "accepted"}:
                reject("Receipt requires a persisted send intent")
            state["receipt"], state["delivery"] = text_value({"receipt": receipt}, "receipt"), "accepted"

    def consume(self, event_id: str, thread: str, at: float) -> bool:
        """Accept the first exact recipient consumption and count rejected duplicates."""
        with self._edit() as state:
            if state["event_id"] != event_id or state["thread"] != thread:
                reject("Consumption identity mismatch")
            if state["suppressed"] is not None:
                reject("Consumption suppressed")
            if state["ready_at"] is None or at < number_value(state, "ready_at"):
                reject("Consumption precedes readiness")
            if state["consumed_at"] is not None:
                state["duplicate_consumptions"] = int(number_value(state, "duplicate_consumptions")) + 1
                return False
            state["consumed_at"] = number_value({"at": at}, "at")
            return True


class CodexQueue:
    """Use one explicit socket for WebSocket reads and exact idle-thread delivery.

    The raw proxy needs HTTP Upgrade and WebSocket frames, not stdio JSONL.
    Reads attach to an existing backend without starting or resuming a
    conversation. Protocol fields come from the installed 0.154.0 schema.
    """

    def __init__(self, executable: Path, manifest: TrialManifest) -> None:
        """Bind executable, host home and profile to the frozen trial."""
        if not executable.is_absolute() or manifest.host != "codex" or manifest.build != "0.154.0":
            reject("Codex probe requires the inspected executable/build")
        if str(UUID(manifest.thread)) != manifest.thread:
            reject("Codex queue requires an exact thread UUID")
        self.executable, self.manifest = executable, manifest
        self.socket = manifest.home / "app-server-control" / "app-server-control.sock"

    def _argv(self, *arguments: str) -> list[str]:
        profile = [] if self.manifest.profile == "default" else ["-p", self.manifest.profile]
        return [str(self.executable), *profile, *arguments]

    def _environment(self) -> dict[str, str]:
        return {**os.environ, "CODEX_HOME": str(self.manifest.home)}

    def status(self) -> str:
        """Validate the recipient against the same backend used by queue."""
        try:
            thread = object_value(self._read_thread().get("thread"))
            if thread.get("id") != self.manifest.thread or thread.get("cliVersion") != self.manifest.build:
                return "stale"
            status = text_value(object_value(thread.get("status")), "type")
            return {"idle": "idle", "active": "busy", "notLoaded": "closed"}.get(status, "bridge-failed")
        except (OSError, ValueError, Empty, subprocess.TimeoutExpired):
            return "bridge-failed"

    def _read_thread(self) -> JsonObject:
        """Read metadata over WebSocket without loading a saved recipient."""
        # The standalone collector also supports Python -S without site packages.
        from .codex_proxy import (  # noqa: PLC0415 - Optional native dependency.
            connect,
        )

        with connect(self._argv("app-server", "proxy", "--sock", str(self.socket)), self._environment()) as client:
            return client.request("thread/read", {"threadId": self.manifest.thread, "includeTurns": False})

    def send(self, message: str) -> str | None:
        """Capture CLI acceptance without claiming useful continuation or retrying."""
        result = subprocess.run(  # noqa: S603 - Exact thread UUID and argv, never a shell.
            self._argv("queue", "--remote", f"unix://{self.socket}", "--thread", self.manifest.thread, "--message", message),
            env=self._environment(),
            capture_output=True, text=True, check=False, timeout=30)
        return (result.stdout.strip() or "queue-exit-0") if result.returncode == 0 else None


# eof
