"""Finite Claude observations using the common telemetry, collector and prototype.

The observer starts before input, binds the exact prepared human turn and gates
Monitor delivery on inspected native evidence. Timers run in this process;
neither readiness files nor operator assertions manufacture a native gate.
An adjacent completed-task notice can carry the continuation only when its
native parent, task and Monitor invocation all bind to the ready event.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from hashlib import sha256
from typing import TYPE_CHECKING

from .claude_monitor import IDENTITIES, Watch, deliver, read_json
from .models import (
    EvidenceRecord,
    JsonObject,
    JsonValue,
    number_value,
    object_value,
    reject,
    text_value,
)
from .probe_driver import SOURCE_SECONDS
from .probe_files import save
from .probe_observer import Observation
from .prototype import Route
from .reports import write_report

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


class ClaudeObservation(Observation):
    """Bind one useful continuation through exact ready/completed notification ancestry."""

    def __init__(self, directory: Path) -> None:
        """Capture no new baseline until the prepared prompt actually executes."""
        super().__init__(directory, "", Route("direct-turn-evidence", lambda: "idle", lambda _: deliver(directory)))
        self.directory = directory
        self.prompt = (directory / "benchmark.txt").read_text(encoding="utf-8").strip()
        self.started = time.time()
        self.errors: list[str] = []
        self.monitor_id = ""
        self.task_id = ""
        self.schema_seen = False
        self.prompt_at: float | None = None
        self.normal_at: float | None = None
        self.receipt_at: float | None = None
        self.wake_turn = ""
        self.wake_turns: set[str] = set()
        self.useful_at: float | None = None
        self.execution_at: float | None = None
        self.final_count = 0
        self.activity: list[EvidenceRecord] = []
        self.counts: Counter[str] = Counter()

    def fail(self, reason: str, at: float) -> None:
        """Retain invalidation and suppress future delivery without retrying."""
        if reason not in self.errors:
            self.errors.append(reason)
            save(self.directory / f"invalidation-{len(self.errors)}.json", {"at": at, "reason": reason})
        if (self.directory / "registration.json").exists():
            self.prototype.suppress("interrupted", at)
        if not (self.directory / "stop.json").exists():
            save(self.directory / "stop.json", {"at": at, "reason": reason})

    def native(self, event: EvidenceRecord) -> None:
        """Inspect only normalized evidence; telemetry owns native JSONL parsing."""
        if event.synthetic and event.kind != "gap":
            return
        self.counts[event.kind] += 1
        if event.kind in {"gap", "native_interruption", "compaction"}:
            self.fail(event.kind + ": " + str(event.data.get("reason", "unknown")), event.at)
        configuration = object_value(self.raw.get("configuration"))
        for native, frozen in (("permissionMode", "permission_mode"), ("effortValue", "effort"), ("mode", "mode")):
            if native in event.data and event.data[native] != configuration.get(frozen):
                self.fail("Exposed configuration changed: " + native, event.at)
        if event.kind in {"native_assistant", "tool_call", "usage_completion"}:
            self.activity.append(event)
            self._quiet_activity(event)
        dispatch = {"native_user": self._user, "tool_call": self._call, "tool_result": self._result,
                    "native_turn_complete": self._complete, "native_observation": self._attachment}
        if event.kind in dispatch:
            dispatch[event.kind](event)

    def _quiet_activity(self, event: EvidenceRecord) -> None:
        if self.normal_at is None or event.at <= self.normal_at:
            return
        state = self.prototype.snapshot()
        end = float("inf") if self.raw["mode"] == "baseline" else number_value(state, "due_at")
        if event.at < end:
            self.fail("Native activity during unchanged-source interval", event.at)

    def _user(self, event: EvidenceRecord) -> None:
        data = event.data
        if data.get("origin") == "human":
            if self.prompt_at is not None or text_value(data, "text").strip() != self.prompt:
                self.fail("Intervening or mismatching human input", event.at)
                return
            self.prompt_at, self.registering_turn = event.at, text_value(data, "native_uuid")
            self._note("benchmark_prompt", event.at, {"evidence": event.location, "origin": "native-human"})
            save(self.directory / "prompt-observed.json", {"at": event.at, "turn": self.registering_turn})
        elif data.get("origin") == "task-notification":
            self._notification(event)

    def _notification(self, event: EvidenceRecord) -> None:
        text = text_value(event.data, "text")
        match = re.search(r"<event>(.*?)</event>", text, re.DOTALL)
        if match is None:
            self._stream_end(event, text)
            return  # A separate stream-ended notice is not another ready event.
        try:
            outcome = object_value(json.loads(match[1]))
        except (ValueError, TypeError):
            self.fail("Malformed native Monitor event", event.at)
            return
        if (not self.task_id or f"<task-id>{self.task_id}</task-id>" not in text
                or any(outcome.get(key) != self.raw[key] for key in IDENTITIES)
                or outcome.get("result") != "synthetic-source-complete" or outcome.get("kind") != "claude-wait-ready"):
            self.fail("Native Monitor event identity/result mismatch", event.at)
            return
        if self.receipt_at is not None:
            self.fail("Duplicate native ready event", event.at)
            return
        self.receipt_at, self.wake_turn = event.at, text_value(event.data, "native_uuid")
        self.wake_turns.add(self.wake_turn)
        save(self.directory / "native-receipt.json", {"at": event.at, "evidence": event.location, "task_id": self.task_id})

    def _stream_end(self, event: EvidenceRecord, text: str) -> None:
        """Keep native IDs distinct while binding the exact adjacent task completion."""
        if not self.wake_turn or event.data.get("parent_uuid") != self.wake_turn:
            return
        expected = {"task-id": self.task_id, "tool-use-id": self.monitor_id, "status": "completed"}
        if any(re.findall(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL) != [value] for tag, value in expected.items()):
            return
        notice = text_value(event.data, "native_uuid")
        if len(self.wake_turns) != 1:
            self.fail("Duplicate native Monitor completion notice", event.at)
            return
        self.wake_turns.add(notice)
        save(self.directory / "native-continuation.json", {"at": event.at, "evidence": event.location,
             "ready_uuid": self.wake_turn, "notice_uuid": notice, "task_id": self.task_id, "monitor_id": self.monitor_id})

    def _bound_continuation(self, event: EvidenceRecord) -> bool:
        """Authorize only the registered human turn or a verified wake ancestry."""
        turn = event.data.get("turn_id")
        if not isinstance(turn, str) or not turn:
            return False
        return turn in self.wake_turns if self.raw["arm"] == "B-prototype" else turn == self.registering_turn

    def _call(self, event: EvidenceRecord) -> None:
        data = event.data
        command = str(object_value(data.get("input")).get("command", "")).replace("\\", "/")
        registering = data.get("name") == "Monitor" or str(self.directory.as_posix() + "/register.ps1") in command
        if registering:
            self._execution(event)
        if data.get("name") == "Monitor":
            self._monitor(event)
        if self.directory.as_posix() + "/consume.ps1" in command:
            self._consumption(event)

    def _execution(self, event: EvidenceRecord) -> None:
        if event.data.get("turn_id") == self.registering_turn and self.prompt_at is not None and self.execution_at is None:
            self.execution_at = event.at
            save(self.directory / "execution-started.json", {"at": event.at, "evidence": event.location,
                                                           "thread": self.manifest.thread, "turn": self.registering_turn})

    def _monitor(self, event: EvidenceRecord) -> None:
        data = event.data
        if self.monitor_id or data.get("input") != self.raw["monitor_input"] or data.get("turn_id") != self.registering_turn:
            self.fail("Duplicate or mismatching Monitor invocation", event.at)
        self.monitor_id = text_value(data, "call_id")

    def _consumption(self, event: EvidenceRecord) -> None:
        state = self.prototype.snapshot()
        if not self._bound_continuation(event) or state.get("ready_at") is None:
            self.fail("Consumption lacks exact native continuation binding", event.at)
            return
        if self.useful_at is not None:
            self.fail("Duplicate useful continuation", event.at)
            return
        self.useful_at = event.at
        self._note("useful_continuation", event.at, {"logical_id": self.raw["event_id"], "evidence": event.location,
                                                   "automatic": self.raw["arm"] == "B-prototype"})

    def _result(self, event: EvidenceRecord) -> None:
        if event.data.get("call_id") != self.monitor_id or not self.monitor_id:
            return
        match = re.search(r"Monitor started \(task ([\w-]+),", str(event.data.get("content")))
        if event.data.get("is_error") is not False or match is None:
            self.fail("Monitor registration did not succeed", event.at)
        else:
            self.task_id = match[1]

    def _attachment(self, event: EvidenceRecord) -> None:
        attachment = object_value(event.data.get("attachment", {}))
        if attachment.get("type") != "deferred_tools_record":
            return
        entries = attachment.get("entries", [])
        if isinstance(entries, list):
            for value in entries:
                entry = object_value(value)
                if entry.get("name") == "Monitor":
                    if entry.get("input_schema") != self.raw["monitor_schema"]:
                        self.fail("Loaded Monitor schema differs from inspected capability", event.at)
                    else:
                        self.schema_seen = True

    def _complete(self, event: EvidenceRecord) -> None:
        message = event.data.get("last_agent_message")
        if message == self.raw["armed_marker"]:
            self._arm_gate(event)
        if message == "WAIT_TEST_DONE":
            self.final_count += 1
            if not self._bound_continuation(event) or self.useful_at is None:
                self.fail("Final marker lacks exact useful continuation", event.at)
            self._remember_final(event.at)
            self._note("final_turn_end", event.at, {"marker": "WAIT_TEST_DONE", "evidence": event.location})

    def _arm_gate(self, event: EvidenceRecord) -> None:
        if not self._valid_gate(event):
            self.fail("Native normal-end registration gate is incomplete", event.at)
            return
        self.prototype.normal_end(event.at, "direct-turn-evidence")
        self.normal_at = event.at if self.normal_at is None else self.normal_at
        self._note("normal_turn_end", event.at, {"origin": "native", "evidence": event.location})
        if not (self.directory / "normal-end.json").exists():
            save(self.directory / "normal-end.json", {"at": event.at, "evidence": event.location})

    def _valid_gate(self, event: EvidenceRecord) -> bool:
        checks = [event.data.get("turn_id") == self.registering_turn, self.prompt_at is not None,
                  self.execution_at is not None, (self.directory / "registration.json").exists(), not self.errors]
        if self.raw["mode"] != "baseline":
            checks.extend([self.schema_seen, bool(self.task_id), (self.directory / "bridge-armed.json").exists()])
        return all(checks)

    def tick(self, now: float) -> float:
        """Collect new bytes and drive the fixed source timer outside the model."""
        for event in self.adapter.snapshot(now):
            self.collector.ingest(event)
            self.native(event)
        if (self.directory / "registration.json").exists():
            state = self.prototype.snapshot()
            self._note("source_start", number_value(state, "source_start"), {})
            if self.errors:
                self.prototype.suppress("interrupted", now)
            self._advance(now)
            state = self.prototype.snapshot()
            if state.get("ready_at") is not None:
                self._note("source_ready", number_value(state, "ready_at"), {})
        return self.deadline(now)

    def drain_boundary(self) -> float | None:
        """Keep baseline quiet time, duplicate observation and drain distinct."""
        if self.raw["mode"] == "baseline" and self.normal_at is not None:
            return self.normal_at + number_value(self.raw, "baseline_seconds")
        if self.final_at is not None:
            return self.final_at + self.manifest.duplicate_window
        return None

    def deadline(self, now: float) -> float:
        """Bound missing input, missing registration, wake failure and completion."""
        boundary = self.drain_boundary()
        if boundary is not None:
            return boundary + self.manifest.drain_bound
        if (self.directory / "registration.json").exists():
            state = self.prototype.snapshot()
            return number_value(state, "due_at") + self.manifest.wake_bound + self.manifest.duplicate_window + self.manifest.drain_bound
        if self.prompt_at is not None:
            return self.prompt_at + 180
        return self.started + 86400 if not self.errors else now

    def run(self, wait: Callable[[float], object]) -> None:
        """Observe through the complete windows and publish one durable audit."""
        drain_started: float | None = None
        while True:
            now = time.time()
            deadline = self.tick(now)
            boundary = self.drain_boundary()
            if boundary is not None and now >= boundary and drain_started is None:
                drain_started = now
                self.collector.drained(now, monotonic_at=time.monotonic())
                save(self.directory / "drain-started.json", {"at": now, "boundary": boundary})
            if drain_started is not None:
                deadline = max(deadline, drain_started + self.manifest.drain_bound)
            if now >= deadline:
                break
            wait(self._next_at(now, deadline, boundary) - now)
        for event in self.adapter.finish(now):
            self.collector.ingest(event)
            self.native(event)
        self.collector.drained(now, monotonic_at=time.monotonic())
        write_report(self.directory / "report.json", self.collector.report(now))
        save(self.directory / "audit.json", self.audit(now, drain_started))

    def _next_at(self, now: float, deadline: float, boundary: float | None) -> float:
        next_at = deadline
        if (self.directory / "registration.json").exists():
            due = number_value(self.prototype.snapshot(), "due_at")
            if now < due:
                next_at = min(next_at, due)
        if boundary is not None and now < boundary:
            next_at = min(next_at, boundary)
        return next_at

    def audit(self, now: float, drain_started: float | None) -> JsonObject:
        """Keep functional findings separate from unknown request accounting."""
        state = self.prototype.snapshot() if (self.directory / "registration.json").exists() else {}
        baseline = self.raw["mode"] == "baseline"
        latency = self._latency(state)
        drained = drain_started is not None and now - drain_started >= self.manifest.drain_bound - 0.01
        checks: JsonObject = {"native_execution": self.execution_at is not None, "no_invalidation": not self.errors,
                              "native_normal_end": self.normal_at is not None if self.raw["arm"] == "B-prototype" else True,
                              "telemetry_drain": drained, "no_human_nudge": self.counts["native_user"] >= 1}
        if baseline:
            checks["unchanged_source"] = state.get("ready_at") is None and state.get("delivery") == "not-attempted"
            checks["native_normal_end"] = self.normal_at is not None
        else:
            checks.update(self._trial_checks(state, latency, drain_started))
        return {"status": "passed" if all(value is True for value in checks.values()) else "failed",
                "thread": self.manifest.thread, "checks": checks, "errors": list(self.errors), "source": state,
                "normal_at": self.normal_at, "receipt_at": self.receipt_at, "useful_at": self.useful_at, "wake_latency": latency,
                "final_at": self.final_at, "drain_started": drain_started, "finished_at": now,
                "native_counts": dict(self.counts), "streams": self._snapshots(), "request_attempt_coverage": "unknown",
                "strict_idle_supported": False, "quota_savings": "unproved"}

    def _latency(self, state: JsonObject) -> float | None:
        ready = state.get("ready_at")
        if self.useful_at is not None and isinstance(ready, int | float):
            return self.useful_at - ready
        return None

    def _trial_checks(self, state: JsonObject, latency: float | None, drain_started: float | None) -> JsonObject:
        ready = state.get("ready_at")
        checks: JsonObject = {"source_interval": isinstance(ready, int | float)
                              and ready - number_value(state, "source_start") >= SOURCE_SECONDS,
                              "useful_wake": latency is not None and 0 <= latency <= self.manifest.wake_bound,
                              "single_consumption": state.get("consumed_at") is not None and state.get("duplicate_consumptions") == 0,
                              "one_final": self.final_count == 1,
                              "duplicate_window": self.final_at is not None and drain_started is not None
                              and drain_started >= self.final_at + self.manifest.duplicate_window}
        if self.raw["arm"] == "B-prototype":
            checks.update(native_receipt=self.receipt_at is not None, exact_monitor_schema=self.schema_seen)
        return checks

    def _snapshots(self) -> list[JsonValue]:
        snapshots: list[JsonValue] = []
        for index, stream in enumerate(self.manifest.streams):
            data = stream.path.read_bytes()
            target = self.directory / f"retained-stream-{index}.jsonl"
            target.write_bytes(data)
            snapshots.append({"path": str(target), "sha256": sha256(data).hexdigest(), "bytes": len(data), "offset": stream.offset})
        return snapshots


def observe_claude(directory: Path) -> None:
    """Arm watches before readiness and retain success or failure after termination."""
    save(directory / "observer-process.json", {"pid": os.getpid(), "at": time.time()})
    observer = ClaudeObservation(directory)
    paths = {stream.path for stream in observer.manifest.streams}
    paths.update(directory / name for name in ("registration.json", "bridge-armed.json", "consumption.json", "bridge-finished.json"))
    watch = Watch(paths)
    watch.start()
    try:
        observer.tick(time.time())
        if observer.errors or observer.prompt_at is not None:
            reject("Pre-prompt observer binding failed")
        save(directory / "observer-ready.json", {"pid": os.getpid(), "at": time.time(), "thread": observer.manifest.thread,
                                                 "native_preflight": "passed", "file_watch": "armed"})
        observer.run(watch.wait)
        save(directory / "observer-finished.json", {"at": time.time(), "status": read_json(directory / "audit.json")["status"]})
    except (OSError, ValueError) as error:
        observer.fail(str(error), time.time())
        save(directory / "observer-failed.json", {"at": time.time(), "reason": str(error)})
        raise
    finally:
        watch.close()


# eof
