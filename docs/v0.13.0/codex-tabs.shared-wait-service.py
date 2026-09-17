"""Launch named fresh Codex TUIs and deliver files through the inspected bridge.

This operator helper is separate from the measured prototype. A unique first
message binds each tab to an exact native thread; titles and newest-thread
guesses never select recipients. Initial setup and seed turns are unmeasured.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path
from threading import Event
from typing import TYPE_CHECKING
from uuid import uuid4

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY))

from watchdog.events import FileSystemEventHandler  # noqa: E402 - Standalone checkout bootstrap.
from watchdog.observers import Observer  # noqa: E402

from tools.wait_evidence.codex_proxy import connect  # noqa: E402
from tools.wait_evidence.models import JsonObject, object_value, reject, text_value  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Mapping

    from watchdog.events import FileSystemEvent

DEFAULT_NAMES = ["baseline", "pair-01-a", "pair-01-b", "pair-02-b", "pair-02-a", "pair-03-a", "pair-03-b"]
MAX_PROMPT_BYTES = 20_000
MAX_BOOTSTRAP_BYTES = 1_048_576
STARTUP_SECONDS = 180
WINDOWS_ACTIVE = 259


def stamp() -> str:
    """Return an explicit UTC timestamp for local receipts."""
    return datetime.now(UTC).isoformat()


def read_json(path: Path) -> JsonObject:
    """Read an exact local record."""
    return object_value(json.loads(path.read_text(encoding="utf-8")))


def write_new(path: Path, data: Mapping[str, object]) -> None:
    """Persist an exclusive record before any delivery can occur."""
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(data, output, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())


def tab_names(config: JsonObject) -> list[str]:
    """Validate the immutable alias list before selecting any local tab record."""
    values = config.get("names")
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        reject("Invalid launcher tab list")
    return [str(value) for value in values]


def read_prompt(path: Path) -> str:
    """Preserve UTF-8 file contents and reject empty or oversized CLI messages."""
    with path.open("rb") as stream:
        data = stream.read(MAX_PROMPT_BYTES + 1)
    if not data.strip() or len(data) > MAX_PROMPT_BYTES:
        reject("Instruction file is empty or exceeds 20,000 UTF-8 bytes")
    return data.decode("utf-8-sig")


def environment(config: JsonObject) -> dict[str, str]:
    """Pin every TUI and queue client to the recorded Codex home."""
    return dict(os.environ, CODEX_HOME=text_value(config, "home"))


def rpc(config: JsonObject, method: str, params: JsonObject) -> JsonObject:
    """Use the same existing Unix backend as the visible TUIs."""
    argv = [text_value(config, "codex"), "app-server", "proxy", "--sock", text_value(config, "socket")]
    with connect(argv, environment(config)) as client:
        return client.request(method, params)


def process_token(pid: int) -> int | None:
    """Identify a live Windows process by creation time, avoiding PID reuse."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        code = wintypes.DWORD()
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != WINDOWS_ACTIVE:
            return None
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(value) for value in times)):
            return None
        return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
    finally:
        kernel.CloseHandle(handle)


def ensure_tab_alive(directory: Path) -> None:
    """Reject closed or replaced TUIs even when their backend thread stays loaded."""
    process = read_json(directory / "process.json")
    token = process_token(int(str(process["pid"])))
    if (directory / "exit.json").exists() or token is None or token != process["created"]:
        reject("The original tab process is no longer alive")


def thread_metadata(config: JsonObject, thread_id: str) -> JsonObject:
    """Check exact identity, build, checkout and live idle state before a send."""
    thread = object_value(rpc(config, "thread/read", {"threadId": thread_id, "includeTurns": False})["thread"])
    if (thread.get("id") != thread_id or thread.get("cliVersion") != config["version"]
            or Path(text_value(thread, "cwd")).resolve() != Path(text_value(config, "repository"))):
        reject("Native thread identity, build or checkout does not match")
    if object_value(thread["status"]).get("type") != "idle":
        reject("The target thread is busy, closed or unavailable; no message was sent")
    return thread


class NativeChanges(FileSystemEventHandler):
    """Wake only ordinary startup code on native catalog writes, with no model polling."""

    def __init__(self, changed: Event) -> None:
        """Keep a coalescing signal for the finite startup deadline."""
        super().__init__()
        self.changed = changed

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Ignore reads and unrelated home files."""
        path = Path(str(event.src_path))
        if (event.event_type in {"modified", "created", "moved"}
                and (path.name.startswith("state_5.sqlite") or path.suffix == ".jsonl")):
            self.changed.set()


def find_binding(config: JsonObject, directory: Path) -> bool:
    """Bind only the exact unique first message, then verify its normal setup end."""
    if (directory / "binding.json").exists():
        return True
    tab = read_json(directory / "tab.json")
    database = Path(text_value(config, "home")) / "state_5.sqlite"
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=5) as catalog:
        rows = catalog.execute("SELECT id, rollout_path FROM threads WHERE first_user_message=? LIMIT 2",
                               (tab["bootstrap"],)).fetchall()
    if not rows:
        return False
    if len(rows) != 1:
        reject("Ambiguous exact bootstrap identity; refusing to choose a thread")
    thread_id, rollout_path = rows[0]
    with Path(rollout_path).open("rb") as stream:
        snapshot = stream.read(MAX_BOOTSTRAP_BYTES + 1)
    if len(snapshot) > MAX_BOOTSTRAP_BYTES:
        reject("Bootstrap evidence exceeds its byte budget")
    # Ignore a partial final record while the host is appending it.
    records = [json.loads(line) for line in snapshot.split(b"\n")[:-1] if line]
    terminal = [row["payload"] for row in records if row.get("type") == "event_msg"
                and row.get("payload", {}).get("type") in {"task_complete", "turn_aborted"}]
    if not terminal:
        return False
    if terminal[-1].get("type") != "task_complete" or terminal[-1].get("last_agent_message", "").strip() != "TAB_READY":
        reject("Setup did not end normally with TAB_READY; retain this tab as a failed preparation")
    ensure_tab_alive(directory)
    thread_metadata(config, thread_id)
    rpc(config, "thread/name/set", {"threadId": thread_id, "name": tab["session_name"]})
    write_new(directory / "bootstrap-evidence.json", {"at": stamp(), "thread": thread_id,
              "rollout": rollout_path, "bytes": len(snapshot), "sha256": hashlib.sha256(snapshot).hexdigest(),
              "normal_end": terminal[-1]})
    write_new(directory / "binding.json", {"at": stamp(), "thread": thread_id, "name": tab["session_name"],
              "alias": tab["alias"], "matched_by": "exact unique first_user_message", "measured": False})
    return True


def bind_all(config: JsonObject, root: Path) -> None:
    """Wait on filesystem notifications until all setup turns end or time expires."""
    changed = Event()
    observer = Observer()
    observer.schedule(NativeChanges(changed), text_value(config, "home"), recursive=False)
    observer.schedule(NativeChanges(changed), str(Path(text_value(config, "home")) / "sessions"), recursive=True)
    observer.start()
    deadline = time.monotonic() + STARTUP_SECONDS
    pending = set(tab_names(config))
    try:
        while pending:
            changed.clear()
            for name in tuple(pending):
                if find_binding(config, root / name):
                    pending.remove(name)
                    print(f"Bound {name}", flush=True)
            remaining = deadline - time.monotonic()
            if not pending:
                break
            if remaining <= 0 or not changed.wait(remaining):
                reject("Setup deadline expired; inspect the retained tabs and use Bind, never Open again on this run")
    finally:
        observer.stop()
        observer.join(timeout=10)


def deliver(config: JsonObject, root: Path, args: argparse.Namespace) -> None:
    """Deliver one immutable instruction file once to a verified named idle TUI."""
    directory = root / args.name
    if args.name not in tab_names(config):
        reject("Unknown tab alias in this run")
    binding = read_json(directory / "binding.json")
    thread_id = text_value(binding, "thread")
    prompt = read_prompt(args.file.resolve())
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if args.kind == "seed" and digest != config["seed_sha256"]:
        reject("Seed contents changed from this run's frozen launcher input")
    if args.kind == "benchmark":
        manifest = read_json(args.file.resolve().parent / "manifest.json")
        if args.file.name != "benchmark.txt" or manifest.get("thread") != thread_id:
            reject("Benchmark must be the prepared benchmark.txt beside its exact thread's durable manifest")
    ensure_tab_alive(directory)
    thread = thread_metadata(config, thread_id)
    if thread.get("name") != binding["name"]:
        reject("The native session name changed; refusing to route by a stale alias")
    argv = [text_value(config, "codex"), "queue", "--remote", text_value(config, "remote"),
            "--thread", thread_id, "--message", prompt]
    if len(subprocess.list2cmdline(argv).encode("utf-16-le")) > 60_000:
        reject("Instruction exceeds the Windows command-line budget")
    slot = directory / args.kind
    # Exclusive directory reservation also protects concurrent delivery commands.
    slot.mkdir()
    write_new(slot / "intent.json", {"at": stamp(), "thread": thread_id, "name": binding["name"],
              "kind": args.kind, "file": str(args.file.resolve()), "sha256": digest,
              "receipt_policy": "One attempt; missing receipt is unknown and never retried automatically"})
    with (slot / "instruction.txt").open("x", encoding="utf-8", newline="") as stored:
        stored.write(prompt)
        stored.flush()
        os.fsync(stored.fileno())
    try:
        result = subprocess.run(argv, env=environment(config), capture_output=True, timeout=45, check=False)  # noqa: S603
    except (OSError, subprocess.TimeoutExpired):
        write_new(slot / "result.json", {"at": stamp(), "outcome": "unknown", "retry": False})
        raise
    write_new(slot / "result.json", {"at": stamp(), "exit": result.returncode,
              "stdout": result.stdout.decode("utf-8", errors="replace"),
              "stderr": result.stderr.decode("utf-8", errors="replace"), "retry": False})
    if result.returncode:
        reject("Queue failed; inspect the retained receipt. Do not resend an uncertain delivery")
    print(f"Queued {args.kind} to {args.name}: {thread_id}", flush=True)


def run_tab(config: JsonObject, directory: Path) -> None:
    """Run a fresh interactive Codex child in this visible Terminal tab."""
    tab = read_json(directory / "tab.json")
    write_new(directory / "launch-intent.json", {"at": stamp(), "fresh": True})
    argv = [text_value(config, "codex"), "--remote", text_value(config, "remote"),
            "-C", text_value(config, "repository"), "-a", "never", "-s", "danger-full-access",
            "-m", text_value(config, "model"), "-c", "model_reasoning_effort=xhigh", text_value(tab, "bootstrap")]
    with subprocess.Popen(argv, env=environment(config), cwd=text_value(config, "repository")) as process:  # noqa: S603
        write_new(directory / "process.json", {"at": stamp(), "pid": process.pid, "created": process_token(process.pid)})
        code = process.wait()
    write_new(directory / "exit.json", {"at": stamp(), "exit": code})


def open_tabs(args: argparse.Namespace, root: Path) -> None:
    """Create one new Terminal window with fresh, uniquely bound tab conversations."""
    if os.name != "nt":
        reject("This launcher requires Windows and Windows Terminal")
    if len(args.names) != len(set(args.names)) or not all(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", name) for name in args.names):
        reject("Use distinct lowercase tab names containing only letters, digits and hyphens")
    seed = read_prompt(args.seed_file.resolve())
    codex_home = args.codex_home.resolve()
    executable = args.codex_executable.resolve()
    terminal = args.terminal.resolve()
    for path in (executable, terminal, codex_home / "state_5.sqlite"):
        if not path.exists():
            reject(f"Required local path is unavailable: {path}")
    build = subprocess.run([str(executable), "--version"], capture_output=True, timeout=15, check=True)  # noqa: S603
    if build.stdout.decode().strip() != "codex-cli 0.154.0":
        reject("This series launcher is inspected for Codex 0.154.0; revalidate a changed build")
    socket = codex_home / "app-server-control/app-server-control.sock"
    config: JsonObject = {"created_at": stamp(), "series": str(uuid4()), "repository": str(REPOSITORY),
                          "home": str(codex_home), "codex": str(executable), "version": "0.154.0",
                          "model": "gpt-6-astra", "socket": str(socket), "remote": "unix://" + socket.as_posix(),
                          "names": args.names, "seed_file": str(args.seed_file.resolve()),
                          "seed_sha256": hashlib.sha256(seed.encode("utf-8")).hexdigest(),
                          "procedure": "User-authorized launcher; fresh TUIs, unmeasured setup then queued seed",
                          "automatic_benchmarks": False}
    # A missing/unhealthy server fails before any tabs or run artifacts exist.
    rpc(config, "thread/loaded/list", {})
    root.mkdir(parents=True, exist_ok=False)
    write_new(root / "launcher.json", config)
    seed_snapshot = root / "seed-instruction.txt"
    with seed_snapshot.open("x", encoding="utf-8", newline="") as output:
        output.write(seed)
        output.flush()
        os.fsync(output.fileno())
    argv = [str(terminal), "-w", "new"]
    for index, name in enumerate(args.names):
        directory = root / name
        directory.mkdir()
        session_name = f"sw-{str(config['series'])[:8]}-{name}"
        bootstrap = (f"Launcher identity: {config['series']} / {name}.\n"
                     "This is an unmeasured setup turn. Do not read files, use tools, or change anything. "
                     "Reply exactly TAB_READY and end the turn normally. Wait for the next instruction.")
        write_new(directory / "tab.json", {"alias": name, "session_name": session_name, "bootstrap": bootstrap})
        if index:
            argv.append(";")
        argv.extend(["new-tab", "--title", name, "--suppressApplicationTitle", "-d", str(REPOSITORY),
                     sys.executable, str(Path(__file__).resolve()), "tab", "--directory", str(root), "--name", name])
    write_new(root / "terminal-intent.json", {"at": stamp(), "argv": argv})
    subprocess.run(argv, check=True, timeout=30)  # noqa: S603 - Explicit interactive window requested by operator.
    print(f"Opened {len(args.names)} tabs. Waiting for exact setup bindings in {root}", flush=True)
    bind_all(config, root)
    for name in args.names:
        deliver(config, root, argparse.Namespace(name=name, file=seed_snapshot, kind="seed"))
    print("Seeds queued. Leave the tabs open; READY and context checks precede every benchmark.", flush=True)


def parser() -> argparse.ArgumentParser:
    """Expose setup, inspection and exact-name file delivery as separate actions."""
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("action", choices=["open", "bind", "status", "send", "tab"])
    result.add_argument("--directory", type=Path, default=REPOSITORY / "a.shared-wait-service/codex-tabs-20260916")
    result.add_argument("--name")
    result.add_argument("--file", type=Path)
    result.add_argument("--kind", choices=["seed", "benchmark", "diagnostic"], default="benchmark")
    result.add_argument("--names", nargs="+", default=DEFAULT_NAMES)
    result.add_argument("--seed-file", type=Path, default=REPOSITORY / "a.shared-wait-service/codex-controlled-proposal-20260916/seed-prompt.proposed.txt")
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    result.add_argument("--codex-home", type=Path, default=codex_home)
    result.add_argument("--codex-executable", type=Path, default=codex_home / "packages/standalone/current/bin/codex.exe")
    result.add_argument("--terminal", type=Path, default=Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WindowsApps/wt.exe")
    return result


def main() -> None:
    """Read structured wrapper arguments without putting file contents into a shell."""
    wrapped = os.environ.pop("LLM_WAIT_TABS_ARGUMENTS", None)
    args = parser().parse_args(json.loads(wrapped) if wrapped else None)
    root = args.directory.resolve()
    if args.action == "open":
        open_tabs(args, root)
        return
    config = read_json(root / "launcher.json")
    if args.action == "bind":
        bind_all(config, root)
    elif args.action == "status":
        for name in tab_names(config):
            path = root / str(name) / "binding.json"
            print(json.dumps(read_json(path) if path.exists() else {"alias": name, "state": "awaiting binding"}))
    elif args.name not in tab_names(config):
        reject("Specify a known --name from this run")
    elif args.action == "tab":
        run_tab(config, root / args.name)
    elif args.file is None:
        reject("Send requires --file")
    else:
        deliver(config, root, args)


if __name__ == "__main__":
    main()

# eof
