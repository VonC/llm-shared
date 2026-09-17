"""Exact-session Monitor bridge, durable handoff and prepared shell entry points.

Only the observer publishes an event after the native gate. The bridge waits in
ordinary code and writes one stdout line. File acceptance is not native receipt.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from threading import Event

from watchdog.observers import Observer

from .models import JsonObject, number_value, object_value, reject, text_value
from .probe_files import save
from .probe_observer import Changed, record
from .prototype import Prototype

IDENTITIES = ("thread", "source_id", "wait_id", "event_id")


def read_json(path: Path) -> JsonObject:
    """Read one selected durable object."""
    return object_value(json.loads(path.read_text(encoding="utf-8")))


class Watch:
    """Coalesce explicit file notifications without model or filesystem polling."""

    def __init__(self, paths: set[Path]) -> None:
        """Install watches before callers inspect their durable conditions."""
        self.ready = Event()
        self.observer = Observer()
        paths = {path.resolve() for path in paths}
        for parent in {path.parent for path in paths}:
            self.observer.schedule(Changed(paths, self.ready), str(parent), recursive=False)

    def start(self) -> None:
        """Arm the operating-system file watches."""
        self.observer.start()

    def wait(self, seconds: float) -> None:
        """Block ordinary code until a deadline or a selected file changes."""
        self.ready.wait(max(0, seconds))
        self.ready.clear()

    def close(self) -> None:
        """Release every operating-system watch."""
        self.observer.stop()
        self.observer.join()


def register(directory: Path) -> Prototype:
    """Publish registration readiness only after SQLite initialization commits."""
    manifest = read_json(directory / "manifest.json")
    start = time.time()
    registration = {key: manifest[key] for key in (*IDENTITIES, "profile")}
    registration.update(source_start=start, due_at=start + number_value(manifest, "source_seconds"),
                        baseline=manifest["mode"] == "baseline")
    prototype = Prototype.create(directory, registration)
    save(directory / "registration.json", {**registration, "pid": os.getpid()})
    return prototype


def bridge(directory: Path) -> None:
    """Register once, await one gated event, and leave all diagnostics off stdout."""
    watch = Watch({directory / "event.json", directory / "stop.json"})
    watch.start()
    try:
        prototype = register(directory)
        state = prototype.snapshot()
        save(directory / "bridge-armed.json", {**{key: state[key] for key in IDENTITIES}, "at": time.time(), "pid": os.getpid()})
        deadline = number_value(state, "due_at") + 180
        while not (directory / "event.json").exists():
            if (directory / "stop.json").exists() or time.time() >= deadline:
                reject("Monitor bridge stopped or deadline expired; do not retry")
            watch.wait(deadline - time.time())
        save(directory / "bridge-finished.json", {"at": time.time(), "status": "event-for-stdout"})
    finally:
        watch.close()


def confirm(directory: Path) -> JsonObject:
    """Bound bridge startup independently of successful Monitor registration."""
    watch = Watch({directory / "bridge-armed.json", directory / "stop.json"})
    watch.start()
    try:
        deadline = time.time() + 90
        while not (directory / "bridge-armed.json").exists():
            if (directory / "stop.json").exists() or time.time() >= deadline:
                reject("Monitor bridge did not arm; do not retry")
            watch.wait(deadline - time.time())
        return read_json(directory / "bridge-armed.json")
    finally:
        watch.close()


def deliver(directory: Path) -> str:
    """Publish the durable outcome after Prototype has persisted its send intent."""
    state = Prototype(directory).snapshot()
    event = {key: state[key] for key in IDENTITIES}
    event.update(kind="claude-wait-ready", result=state["result"])
    save(directory / "event.json", event)
    return "bridge-file-published"


def consume(directory: Path) -> JsonObject:
    """Validate every bound identity and outcome before single consumption."""
    manifest = read_json(directory / "manifest.json")
    prototype = Prototype(directory)
    state = prototype.snapshot()
    event = read_json(directory / "event.json") if manifest["arm"] == "B-prototype" else state
    if any(state[key] != manifest[key] or event[key] != manifest[key] for key in IDENTITIES):
        reject("Durable event identity mismatch")
    if state.get("result") != "synthetic-source-complete" or event.get("result") != state["result"]:
        reject("Durable source outcome mismatch")
    at = time.time()
    accepted = prototype.consume(text_value(manifest, "event_id"), text_value(manifest, "thread"), at)
    record(directory, "consumption", at, {"logical_id": manifest["event_id"], "accepted": accepted})
    if not accepted:
        reject("Duplicate consumption rejected; do not retry")
    result: JsonObject = {"at": at, "accepted": True, "validated": {key: event[key] for key in (*IDENTITIES, "result")}}
    save(directory / "consumption.json", result)
    return result


def prepare(directory: Path, data: JsonObject) -> str:
    """Create exact wrappers and the final prompt before any measured input."""
    root = Path(text_value(data, "repository"))
    script = root / "docs/v0.13.0/probe.shared-wait-service.py"
    data["armed_marker"] = "CLAUDE_WAIT_" + text_value(data, "run_id") + "_ARMED"
    monitor: JsonObject = {"description": "CLAUDE_WAIT_" + text_value(data, "run_id"), "timeout_ms": 1200000,
                          "command": f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{directory.as_posix()}/monitor.ps1"'}
    data["monitor_input"] = monitor
    for name, action in (("monitor", "claude-bridge"), ("confirm", "claude-confirm"),
                         ("consume", "claude-consume"), ("register", "register"), ("source", "source")):
        output = directory / ("event.json" if name == "monitor" else name + "-command.log")
        body = ["$ErrorActionPreference = 'Continue'", "$env:SENV_UID = [Guid]::NewGuid().ToString('N')",
                f"Set-Location -LiteralPath '{root.as_posix()}'",
                f"& cmd.exe /d /v:on /c 'set NO_MORE_SENV_%PRJ_DIR_NAME%=& {root / 'senv.bat'} && python {script.as_posix()} {action} --directory {directory.as_posix()}' > '{directory.as_posix()}/{name}-command.log' 2>&1",
                "$commandExit = $LASTEXITCODE", "$ErrorActionPreference = 'Stop'",
                f"if ($commandExit -ne 0) {{ throw '{name} failed; retain diagnostics and do not retry' }}",
                f"[Console]::Out.WriteLine([IO.File]::ReadAllText('{output.as_posix()}').TrimEnd())"]
        if name == "monitor":
            body[-1] = f"Get-Content -LiteralPath '{output.as_posix()}' -Raw | ConvertFrom-Json | ConvertTo-Json -Compress"
        (directory / (name + ".ps1")).write_text("\n".join(body) + "\n", encoding="utf-8")
    prefix = (f"Run the prepared synthetic wait benchmark in this exact existing session: {data['thread']}. "
              f"Read {directory.as_posix()}/manifest.json and preserve its thread, source_id, wait_id and event_id. "
              "Keep the seeded context and current model, effort, provider and permissions unchanged. "
              "Do not reseed, compact, delegate, restart or send PushNotification. Use PowerShell for the prepared scripts. ")
    if data["mode"] == "baseline":
        return prefix + (f"Run & '{directory.as_posix()}/register.ps1' once. On success reply exactly {data['armed_marker']} "
                         "and end this turn normally. The independent observer measures 600 seconds of unchanged source "
                         "after native normal end and a separate 120-second drain. Do no further work and do not poll.")
    ending = (f"Validate the ready outcome against the manifest, then run & '{directory.as_posix()}/consume.ps1' once. "
              "On confirmed consumption reply exactly WAIT_TEST_DONE and end normally. Do no further work. "
              "An independent observer retains 120 seconds of duplicate observation and a separate 120-second drain.")
    if data["arm"] == "A":
        return prefix + (f"Run & '{directory.as_posix()}/register.ps1' once, then run & '{directory.as_posix()}/source.ps1'. "
                         "Use the installed foreground tool's initial yield of 1000 ms where supported, otherwise its supported minimum, "
                         "then blocking waits of 60000 ms until the source completes. These waits are the benchmark-only exception. "
                         "Inspect the installed tool schema as needed; do not invent parameters or substitute Monitor. " + ending)
    return prefix + ("Load the actual Monitor tool. Invoke it once with exactly this input (no persistent parameter):\n"
                     + json.dumps(monitor, indent=2) + "\nAfter Monitor reports successful startup, run "
                     f"& '{directory.as_posix()}/confirm.ps1' once. If the bridge is armed, reply exactly {data['armed_marker']} "
                     "and end this turn normally. Do not wait or poll. The native Monitor event must wake this same session "
                     "automatically. When that event arrives, " + ending)


# eof
