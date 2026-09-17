"""Bounded Monitor smoke probe; ordinary code observes a human-started Claude TUI.

No host is launched, messaged or resumed by this driver. Native normal-end
evidence gates one durable outcome; request-attempt coverage remains unknown.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from hashlib import sha256
from pathlib import Path
from threading import Event
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.wait_evidence.prototype import Prototype, Route  # noqa: E402
from watchdog.events import FileSystemEventHandler  # noqa: E402
from watchdog.observers import Observer  # noqa: E402

SPEC = importlib.util.spec_from_file_location("claude_probe_state", Path(__file__).with_name("claude-probe-state.shared-wait-service.py"))
assert SPEC is not None and SPEC.loader is not None
STATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATE)


class Changes(FileSystemEventHandler):
    def __init__(self, paths, event):
        self.paths, self.event = {path.resolve() for path in paths}, event

    def on_any_event(self, event):
        if event.event_type in {"modified", "created", "deleted", "moved"} and any(
                item and Path(os.fsdecode(item)).resolve() in self.paths for item in (event.src_path, event.dest_path)):
            self.event.set()


class Watch:
    def __init__(self, paths):
        self.event = Event()
        self.observer = Observer()
        handler = Changes(paths, self.event)
        for parent in {path.parent for path in paths}:
            self.observer.schedule(handler, str(parent), recursive=False)

    def __enter__(self):
        self.observer.start()
        return self

    def wait(self, deadline):
        self.event.wait(max(0, deadline - time.time()))
        self.event.clear()

    def __exit__(self, *_):
        self.observer.stop()
        self.observer.join()


def prepare(directory, transcript):
    directory.mkdir(parents=True, exist_ok=False)
    raw = transcript.read_bytes()
    records = STATE.native_records(transcript)
    capability = STATE.capability(records)
    (directory / "capability-native.jsonl").write_bytes(raw)
    capability["native_sha256"] = sha256(raw).hexdigest()
    STATE.write_json(directory / "capability.json", capability)
    marker = "CLAUDE_WAIT_SMOKE_" + directory.name
    monitor = {"description": marker, "timeout_ms": 1200000,
               "command": f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{directory.as_posix()}/monitor.ps1"'}
    config = {key: capability[key] for key in ("thread", "build", "model", "permission_mode", "effort", "provider")}
    config.update(prepared_at=time.time(), transcript=str(transcript), quiet_seconds=600,
                  wake_seconds=60, duplicate_seconds=120, drain_seconds=120,
                  startup_seconds=86400, registration_seconds=180, armed_marker=marker + "_ARMED",
                  monitor_input=monitor, source_id=str(uuid4()), wait_id=str(uuid4()), event_id=str(uuid4()),
                  profile="existing-interactive-session", source_condition="600 seconds after verified native normal end",
                  classification="unseeded capability smoke; excluded from matched A/B series")
    STATE.write_json(directory / "config.json", config)
    script = Path(__file__).resolve().as_posix()
    # Claude sets NoDefaultCurrentDirectoryInExePath=1. A bare senv.bat can
    # resolve to an unrelated PATH entry even after Set-Location.
    environment = str(ROOT / "senv.bat")
    for name, action in (("monitor", "bridge"), ("consume", "consume")):
        # The environment wrapper emits output, so Monitor captures it to local diagnostics.
        # Only bridge.py's dedicated event file is copied to stdout by this launcher.
        body = ["$ErrorActionPreference = 'Stop'", f"Set-Location -LiteralPath '{ROOT.as_posix()}'",
                # Windows PowerShell turns native stderr (including successful uv
                # status messages) into error records. Capture them and check exit.
                "$ErrorActionPreference = 'Continue'",
                f"& cmd.exe /d /v:on /c 'set NO_MORE_SENV_%PRJ_DIR_NAME%=& {environment} && python {script} {action} --directory {directory.as_posix()}' > '{directory.as_posix()}/{name}-command.log' 2>&1",
                "$commandExit = $LASTEXITCODE", "$ErrorActionPreference = 'Stop'",
                f"if ($commandExit -ne 0) {{ throw '{name} command failed; see {name}-command.log' }}"]
        if name == "monitor":
            body.append(f"[Console]::Out.WriteLine([IO.File]::ReadAllText('{directory.as_posix()}/event.txt').TrimEnd())")
        else:
            body.append(f"Get-Content -LiteralPath '{directory.as_posix()}/consumption.json' -Raw")
        (directory / (name + ".ps1")).write_text("\n".join(body) + "\n", encoding="utf-8")
    confirmation = f"""$ErrorActionPreference = 'Stop'
$armedPath = '{directory.as_posix()}/armed.json'
$watcher = New-Object System.IO.FileSystemWatcher '{directory.as_posix()}', '*'
$watcher.EnableRaisingEvents = $true
$deadline = [DateTime]::UtcNow.AddSeconds(90)
try {{
    while (-not (Test-Path -LiteralPath $armedPath)) {{
        $remaining = [int]($deadline - [DateTime]::UtcNow).TotalMilliseconds
        if ($remaining -le 0) {{ throw 'Bridge did not arm within 90 seconds; do not retry.' }}
        $null = $watcher.WaitForChanged([IO.WatcherChangeTypes]::All, $remaining)
    }}
    Get-Content -LiteralPath $armedPath -Raw
}}
finally {{ $watcher.Dispose() }}
"""
    (directory / "confirm.ps1").write_text(confirmation, encoding="utf-8")
    print(json.dumps({"directory": str(directory), "thread": config["thread"], "capability": "Monitor loaded", "state": "prepared"}))


def bridge(directory, config):
    start = time.time()
    registration = {key: config[key] for key in ("thread", "profile", "source_id", "wait_id", "event_id")}
    registration.update(source_start=start, due_at=start + config["quiet_seconds"])
    Prototype.create(directory, registration)
    STATE.write_json(directory / "armed.json", {"at": start, "pid": os.getpid(), "thread": config["thread"]})
    event_path, stop_path = directory / "event.txt", directory / "stop.json"
    with Watch([event_path, stop_path]) as watch:
        deadline = start + 1050
        while not event_path.exists():
            if stop_path.exists() or time.time() >= deadline:
                raise RuntimeError("Probe stopped or bridge deadline expired before delivery")
            watch.wait(deadline)
    STATE.write_json(directory / "bridge-finished.json", {"at": time.time(), "reason": "one event ready for stdout"})


def consume(directory, config):
    state = Prototype(directory).snapshot()
    event = STATE.read_json(directory / "event.txt")
    for key in ("thread", "source_id", "wait_id", "event_id"):
        if state[key] != config[key] or event[key] != config[key]:
            raise ValueError("Durable event identity mismatch: " + key)
    if state.get("result") != "synthetic-source-complete" or event["result"] != state["result"]:
        raise ValueError("Durable result missing or differs from event")
    at = time.time()
    accepted = Prototype(directory).consume(config["event_id"], config["thread"], at)
    if not accepted:
        raise ValueError("Event was already consumed")
    STATE.write_json(directory / "consumption.json", {"at": at, "accepted": True, "validated": event})
    print("consumed once")


def deliver(directory, config):
    """Prototype has persisted result and intent before this one stdout handoff."""
    state = Prototype(directory).snapshot()
    event = {key: config[key] for key in ("thread", "source_id", "wait_id", "event_id")}
    event.update(kind="claude-wait-ready", result=state["result"])
    STATE.write_json(directory / "event.txt", event, compact=True)
    # Accepted means a file handed to the bridge, not Claude reception.
    return "bridge-file-published"


def observe(directory, config):
    transcript = Path(config["transcript"])
    armed_path, consumption_path = directory / "armed.json", directory / "consumption.json"
    # Validate the real native file before publishing a readiness acknowledgement.
    STATE.native_state(STATE.native_records(transcript), config)
    started, emitted, finish_at = time.time(), None, None
    with Watch([transcript, armed_path, consumption_path, directory / "bridge-finished.json"]) as watch:
        STATE.write_json(directory / "observer-started.json", {"at": time.time(), "pid": os.getpid(),
                         "native_preflight": "passed", "file_watch": "armed"})
        while True:
            now = time.time()
            native = STATE.native_state(STATE.native_records(transcript), config)
            if native["interruption"]:
                raise RuntimeError(native["interruption"])
            if not armed_path.exists():
                deadline = started + config["startup_seconds"]
                if now >= deadline:
                    raise RuntimeError("No Monitor bridge started within operator window")
            elif native["armed_end"] is None:
                deadline = STATE.read_json(armed_path)["at"] + config["registration_seconds"]
                if now >= deadline:
                    raise RuntimeError("No successful Monitor call plus exact native normal-end evidence")
            elif emitted is None:
                gate = native["armed_end"]
                deadline = gate["at"] + config["quiet_seconds"]
                quiet_calls = [call for call in native["calls"] if call["at"] > gate["at"]]
                quiet_usage = [usage for usage in native["usage_completions"] if usage["at"] > gate["at"]]
                if quiet_calls or quiet_usage:
                    raise RuntimeError("Claude performed work during the unchanged-source interval")
                if not (directory / "normal-end.json").exists():
                    STATE.write_json(directory / "normal-end.json", gate)
                if now >= deadline:
                    prototype = Prototype(directory)
                    prototype.normal_end(gate["at"], "direct-turn-evidence")
                    route = Route("direct-turn-evidence", lambda: "idle", lambda _: deliver(directory, config))
                    prototype.advance(now, route)
                    emitted = now
                    STATE.write_json(directory / "delivery.json", {"at": now, "native_gate": gate,
                                     "quiet_seconds": now - gate["at"], "receipt_scope": "bridge handoff only"})
                    continue
            else:
                deadline = emitted + config["wake_seconds"]
                useful = [call for call in native["calls"] if call["at"] >= emitted
                          and "consume.ps1" in json.dumps(call["input"])]
                if useful:
                    if useful[0]["at"] > deadline:
                        raise RuntimeError("First useful continuation exceeded the 60-second wake bound")
                    deadline = emitted + 180
                if native["final_end"]:
                    if finish_at is None:
                        finish_at = native["final_end"]["at"] + config["duplicate_seconds"] + config["drain_seconds"]
                    deadline = finish_at
                    if now >= finish_at:
                        report(directory, config, native, emitted)
                        return
                elif now >= deadline:
                    raise RuntimeError("Wake bound or final completion deadline expired")
            watch.wait(deadline)


def report(directory, config, native, emitted):
    raw = Path(config["transcript"]).read_bytes()
    (directory / "native-final.jsonl").write_bytes(raw)
    state = Prototype(directory).snapshot()
    consumption = STATE.read_json(directory / "consumption.json") if (directory / "consumption.json").exists() else None
    final_at = native["final_end"]["at"]
    useful = [call for call in native["calls"] if call["at"] >= emitted and "consume.ps1" in json.dumps(call["input"])]
    extras = [call for call in native["calls"] if call["at"] > final_at]
    extra_usage = [usage for usage in native["usage_completions"] if usage["at"] > final_at]
    result = {"classification": config["classification"], "thread": config["thread"], "build": config["build"],
              "finished_at": time.time(), "native_sha256": sha256(raw).hexdigest(), "native": native,
              "durable": state, "consumption": consumption,
              "useful_latency_seconds": useful[0]["at"] - emitted if useful else None,
              "extra_tool_calls_after_final": extras, "extra_usage_after_final": extra_usage,
              "request_attempt_coverage": "unknown",
              "functional_success": bool(consumption and useful and useful[0]["at"] - emitted <= 60
                  and native["done_messages"] == 1 and not extras and not extra_usage
                  and state["duplicate_consumptions"] == 0)}
    STATE.write_json(directory / "report.json", result)
    STATE.write_json(directory / "observer-finished.json", {"at": time.time(), "functional_success": result["functional_success"]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "bridge", "observe", "consume"])
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--transcript", type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if not args.directory.is_absolute() or "a.shared-wait-service" not in directory.parts:
        raise ValueError("Use an absolute ignored evidence directory")
    if args.action == "prepare":
        prepare(directory, args.transcript)
    else:
        config = STATE.read_json(directory / "config.json")
        try:
            {"bridge": bridge, "observe": observe, "consume": consume}[args.action](directory, config)
        except Exception as error:
            if args.action == "observe":
                STATE.write_json(directory / "stop.json", {"at": time.time(), "error": str(error)})
                (directory / "native-failed.jsonl").write_bytes(Path(config["transcript"]).read_bytes())
                if (directory / "prototype.sqlite3").exists():
                    Prototype(directory).suppress("bridge-failed", time.time())
            raise


if __name__ == "__main__":
    main()

# eof
