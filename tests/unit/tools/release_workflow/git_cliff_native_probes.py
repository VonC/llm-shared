"""The native checks of the git-cliff provisioning layer and their helper parents, run by the recorder on a real kernel.

Step 2 of v0.14.0 git-cliff-provisioning (plan decisions Q06 and Q07) wrote
these checks inside `git_cliff_native_checks.py`; Step 4 moves them here
before adding its own, as the Step 2 validation planned once the recorder
reached the 550 to 650 line band. The recorder keeps the catalog, the
bounded runner, the record and the command line, and dispatches the helper
parents of this module from its `--helper` mode. Nothing here is imported by
a test.

Every check takes its bound and a scratch directory outside the repository,
runs stand-in children (the interpreter with a short script) or the real
download worker, ends every process it started, and returns its observation.
Step 4 adds `check_worker_deadline`: a download worker started through the
bootstrap, recorded in a disposable staging directory under a temporary
tooling root, stalls on a local endpoint that accepts and never answers, and
is ended job-wide at its deadline before it writes any outcome.
"""

from __future__ import annotations

import ctypes
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tools.release_workflow import windows_native as native
from tools.release_workflow.git_cliff.cache import OWNER_FILE, CacheLayout, OwnerFile
from tools.release_workflow.git_cliff.download_worker import (
    WorkerRequest,
    worker_command,
)
from tools.release_workflow.git_cliff.manifest import PLATFORM_TRIPLE
from tools.release_workflow.windows_child import (
    ChildRequest,
    ContainmentError,
    UnconfirmedEndError,
    is_process_in_job,
    run_contained,
)
from tools.release_workflow.windows_guard import open_guard
from tools.release_workflow.windows_native import NativeCallError
from tools.release_workflow.windows_process import (
    ProcessIdentity,
    ProcessState,
    current_identity,
    process_state,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

ROOT = Path(__file__).resolve().parents[4]
RECORDER_MODULE = "tests.unit.tools.release_workflow.git_cliff_native_checks"
SETTLE = 5.0
_SYNCHRONIZE = 0x00100000
_INVALID_PARAMETER = 87
_JOB_BASIC_LIMITS = 2
_LIMIT_ACTIVE_PROCESS = 0x00000008
_POLL = 0.05
_TERMINATE = "TerminateJobObject"
_WORKER_DEADLINE = 10.0
_MARK = "import pathlib, sys; pathlib.Path(sys.argv[1]).write_text('ran')"
_MARK_AND_SLEEP = "import pathlib, sys, time; pathlib.Path(sys.argv[1]).write_text('ran'); time.sleep(120)"
_SPAWN_DESCENDANT = ("import pathlib, subprocess, sys; child = subprocess.Popen([sys.executable, '-I', '-c', 'import time; time.sleep(120)']); "
                     "pathlib.Path(sys.argv[1]).write_text(str(child.pid)); print(child.pid, flush=True)")
_WAIT_FOR_RELEASE = ("import pathlib, sys, time\nend = time.monotonic() + 30\n"
                     "while not pathlib.Path(sys.argv[1]).exists() and time.monotonic() < end:\n    time.sleep(0.05)")


class CheckTimeoutError(RuntimeError):
    """A bounded wait of a check expired."""


class Kernel32:
    """The few kernel32 calls only the recorder makes, declared on their own library instance."""

    def __init__(self) -> None:
        """Declare them."""
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenProcess.restype = wintypes.HANDLE
        api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        api.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
        api.CreateJobObjectW.restype = wintypes.HANDLE
        api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.POINTER(native.JOBOBJECT_BASIC_LIMIT_INFORMATION),
                                                wintypes.DWORD]
        api.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                  ctypes.POINTER(native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION), wintypes.DWORD,
                                                  wintypes.LPVOID]
        api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        api.GetCurrentProcess.restype = wintypes.HANDLE
        self.api: Any = api

    def open_process(self, pid: int) -> int | None:
        """Open a process to wait on it; `None` when no process has this PID any more."""
        handle = self.api.OpenProcess(_SYNCHRONIZE, 0, pid)
        if not handle and ctypes.get_last_error() == _INVALID_PARAMETER:
            return None
        return handle or 0

    def alive(self, handle: int | None) -> bool:
        """Tell whether the process behind a handle is still running."""
        return bool(handle) and self.api.WaitForSingleObject(handle, 0) == native.WAIT_TIMEOUT

    def ended(self, handle: int | None, seconds: float) -> bool:
        """Tell whether the process behind a handle ended within the given time, closing the handle."""
        if handle is None:
            return True
        try:
            return bool(handle) and self.api.WaitForSingleObject(handle, int(seconds * 1000)) == native.WAIT_OBJECT_0
        finally:
            self.close(handle)

    def close(self, handle: int | None) -> None:
        """Close a handle the recorder opened."""
        if handle:
            self.api.CloseHandle(handle)


KERNEL = Kernel32()


class Observed:
    """The real declared kernel, observed: it keeps the job and the process information and runs a hook before termination."""

    def __init__(self, before_terminate: Callable[[], None] | None = None) -> None:
        """Wrap the declared kernel32."""
        self._kernel = native.kernel()
        self._before = before_terminate
        self.job = 0
        self.information: Any = None
        self.hook_error: Exception | None = None

    def __getattr__(self, name: str) -> Callable[..., Any]:
        """Pass every other call to the real kernel."""
        return getattr(self._kernel, name)

    def CreateJobObjectW(self, *arguments: Any) -> int:  # noqa: N802 - the kernel32 name
        """Keep the job handle."""
        self.job = self._kernel.CreateJobObjectW(*arguments)
        return self.job

    def CreateProcessW(self, *arguments: Any) -> int:  # noqa: N802 - the kernel32 name
        """Keep the process information structure."""
        result = self._kernel.CreateProcessW(*arguments)
        self.information = arguments[9]
        return result

    def TerminateJobObject(self, *arguments: Any) -> int:  # noqa: N802 - the kernel32 name
        """Run the hook, then terminate; a failing hook fails its check, never the termination."""
        if self._before is not None:
            try:
                self._before()
            except Exception as error:  # noqa: BLE001 - kept and raised by the check once the child has ended
                self.hook_error = error
        return self._kernel.TerminateJobObject(*arguments)

    def raise_hook_error(self) -> None:
        """Fail the check when its observation hook failed."""
        if self.hook_error is not None:
            raise self.hook_error


class _FailingTerminate(Observed):
    """The real kernel, except that every `TerminateJobObject` call fails."""

    def TerminateJobObject(self, *arguments: Any) -> int:  # noqa: N802 - the kernel32 name
        """Fail as a refused termination would."""
        del arguments
        raise NativeCallError(_TERMINATE, native.ERROR_ACCESS_DENIED)


def _stand_in(script: str, *arguments: str, **request: Any) -> ChildRequest:
    """Build a request running the interpreter with a short script."""
    return ChildRequest(Path(sys.executable), ("-I", "-c", script, *arguments), **request)


def _await(predicate: Callable[[], bool], seconds: float, what: str) -> None:
    """Poll until the predicate holds, or fail the check."""
    end = time.monotonic() + seconds
    while not predicate():
        if time.monotonic() > end:
            msg = f"{what} did not happen within {seconds} s"
            raise CheckTimeoutError(msg)
        time.sleep(_POLL)


def _write_identity(path: Path, identity: ProcessIdentity) -> None:
    """Publish a child identity for the recorder, complete before it appears."""
    temporary = path.with_suffix(".partial")
    temporary.write_text(json.dumps({"pid": identity.pid, "created": identity.created}), encoding="utf-8")
    temporary.replace(path)


def _read_identity(path: Path) -> ProcessIdentity:
    """Read a published child identity."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return ProcessIdentity(data["pid"], data["created"])


def _dead(identity: ProcessIdentity) -> bool:
    """Wait a little for an exact process identity to be gone."""
    end = time.monotonic() + SETTLE
    while process_state(identity) is not ProcessState.DEAD:
        if time.monotonic() > end:
            return False
        time.sleep(_POLL)
    return True


def _helper(name: str, *arguments: Path) -> subprocess.Popen[bytes]:
    """Start the recorder as a helper parent."""
    command = [sys.executable, "-m", RECORDER_MODULE, "--helper", name, *map(str, arguments)]
    return subprocess.Popen(command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)  # noqa: S603


def _kill(helper: subprocess.Popen[bytes]) -> None:
    """End a helper parent, as a crash would, and reap it."""
    helper.kill()
    helper.communicate(timeout=SETTLE)


def check_membership(bound: float, scratch: Path) -> dict[str, object]:
    """The created child is in its job before it resumes."""
    del scratch
    observed = Observed()
    seen: dict[str, bool] = {}

    def record(identity: ProcessIdentity) -> None:
        del identity
        seen["in_job"] = is_process_in_job(observed.information.hProcess, observed.job)

    outcome = run_contained(_stand_in("pass", deadline=bound, record=record), api=observed)
    return {"in_job_before_resume": seen.get("in_job"), "status": outcome.status, "timed_out": outcome.timed_out}


def check_parent_killed(name: str, bound: float, scratch: Path) -> dict[str, object]:
    """A helper's child, suspended or running, ends once the helper is killed."""
    identity_path, marker = scratch / f"{name}.identity.json", scratch / f"{name}.ran"
    helper = _helper(name, identity_path, marker)
    try:
        _await(identity_path.exists, bound / 2, "the helper's child identity")
        if name == "running":
            _await(marker.exists, bound / 2, "the helper's child start")
        identity = _read_identity(identity_path)
    finally:
        _kill(helper)
    return {"child_ended": _dead(identity), "child_ran": marker.exists()}


def check_process_limit(bound: float, scratch: Path) -> dict[str, object]:
    """A helper inside a job limited to one active process cannot create a contained child."""
    result, marker = scratch / "limited.json", scratch / "limited.ran"
    helper = _helper("limited", result, marker)
    try:
        _, errors = helper.communicate(timeout=bound)
    finally:
        if helper.poll() is None:
            _kill(helper)
    if not result.exists():
        raise RuntimeError(errors.decode("utf-8", "replace")[-400:])
    reported = json.loads(result.read_text(encoding="utf-8"))
    return {"error": reported["error"], "call": reported["call"], "child_ran": marker.exists(),
            "job_total_processes": reported["job_total_processes"]}


def check_descendant(bound: float, scratch: Path) -> dict[str, object]:
    """The root exits while its descendant holds stdout: the call returns, the descendant ended by the teardown."""
    pid_file = scratch / "descendant.pid"
    seen: dict[str, Any] = {}

    def before_terminate() -> None:
        seen["handle"] = KERNEL.open_process(int(pid_file.read_text(encoding="utf-8")))
        seen["alive"] = KERNEL.alive(seen["handle"])

    observed = Observed(before_terminate)
    outcome = run_contained(_stand_in(_SPAWN_DESCENDANT, str(pid_file), deadline=bound / 2), api=observed)
    observed.raise_hook_error()
    return {"status": outcome.status, "timed_out": outcome.timed_out, "descendant_alive_at_teardown": seen["alive"],
            "descendant_ended": KERNEL.ended(seen["handle"], SETTLE)}


def check_teardown_failure(bound: float, scratch: Path) -> dict[str, object]:
    """A helper whose termination fails still exits normally, and kill-on-close then ends its descendant."""
    pid_file = scratch / "teardown.pid"
    ended: list[bool] = []
    observed = Observed(lambda: ended.append(KERNEL.ended(KERNEL.open_process(int(pid_file.read_text(encoding="utf-8"))), SETTLE)))
    request = ChildRequest(Path(sys.executable), ("-m", RECORDER_MODULE, "--helper", "teardown-failure", str(pid_file)), cwd=ROOT,
                           deadline=bound / 2)
    outcome = run_contained(request, api=observed)
    observed.raise_hook_error()
    reported = json.loads(outcome.stdout.decode("utf-8") or "{}")
    return {"helper_error": reported.get("error"), "helper_call": reported.get("call"),
            "descendant_alive_after_error": reported.get("descendant_alive"), "helper_status": outcome.status,
            "helper_timed_out": outcome.timed_out, "descendant_ended": ended == [True]}


def _rename(source: Path, target: Path) -> str:
    """Try the rename a replacement needs; undo it when it succeeds."""
    try:
        source.rename(target)
    except PermissionError as error:
        return "refused" if error.winerror == native.ERROR_SHARING_VIOLATION else f"denied {error.winerror}"
    target.rename(source)
    return "renamed"


def check_guard_before_start(bound: float, scratch: Path) -> dict[str, object]:
    """The guard alone refuses the rename until it is closed."""
    del bound
    executable, moved = scratch / "guarded.exe", scratch / "moved.exe"
    executable.write_bytes(b"stand-in executable")
    guard = open_guard(executable)
    while_held = _rename(executable, moved)
    guard.close()
    return {"while_held": while_held, "after_close": _rename(executable, moved)}


def check_inherited_guard(bound: float, scratch: Path) -> dict[str, object]:
    """After the parent closes its guard, the child's inherited copy still refuses the rename."""
    executable, moved, release = scratch / "inherited.exe", scratch / "inherited-moved.exe", scratch / "release"
    executable.write_bytes(b"stand-in executable")
    guard = open_guard(executable)
    results: dict[str, object] = {}

    def attempt() -> None:
        time.sleep(0.3)
        results["during_child"] = _rename(executable, moved)
        release.write_text("go", encoding="utf-8")

    def record(identity: ProcessIdentity) -> None:
        del identity
        guard.close()
        results["parent_guard_closed"] = True
        threading.Thread(target=attempt, daemon=True).start()

    outcome = run_contained(_stand_in(_WAIT_FOR_RELEASE, str(release), inherited=(guard.handle,), deadline=bound / 2, record=record))
    _await(lambda: "during_child" in results, SETTLE, "the rename attempt")
    return {**results, "after_child": _rename(executable, moved), "status": outcome.status}


@dataclass(frozen=True)
class _Place:
    """The version and triple of the disposable staging directory."""

    version: str
    triple: str


class _SilentEndpoint:
    """A local TCP endpoint that accepts one connection and never answers it."""

    def __init__(self) -> None:
        """Listen on a free loopback port and accept in a daemon thread."""
        self._server = socket.create_server(("127.0.0.1", 0))
        self.port: int = self._server.getsockname()[1]
        self.connected = threading.Event()
        self._accepted: list[socket.socket] = []
        threading.Thread(target=self._accept, daemon=True).start()

    def _accept(self) -> None:
        """Hold the first connection open without a byte of answer."""
        try:
            connection, _ = self._server.accept()
        except OSError:
            return
        self._accepted.append(connection)
        self.connected.set()

    def close(self) -> None:
        """Close the accepted connection and the listener."""
        for connection in self._accepted:
            connection.close()
        self._server.close()


def check_worker_deadline(bound: float, scratch: Path) -> dict[str, object]:
    """A recorded download worker stalled on a silent endpoint is ended job-wide at its deadline."""
    del bound
    layout, owner = CacheLayout(scratch / "tooling"), current_identity()
    staging = layout.attempt_dir(_Place("2.14.2", PLATFORM_TRIPLE), "staging", owner, secrets.token_hex(4))
    staging.mkdir(parents=True)
    owner_file = staging / OWNER_FILE
    owner_file.write_bytes(OwnerFile(owner).encode())

    def record(identity: ProcessIdentity) -> None:
        owner_file.write_bytes(OwnerFile.decode(owner_file.read_bytes()).with_child(identity).encode())

    endpoint = _SilentEndpoint()
    try:
        request = WorkerRequest(mode="archive", url=f"https://127.0.0.1:{endpoint.port}/git-cliff.zip", target=staging / "git-cliff.zip",
                                expected_size=1024, remaining=60.0)
        executable, arguments = worker_command(Path(sys.executable), ROOT, request)
        # The loopback endpoint must be reached directly, whatever proxy the environment declares.
        environment = {name: value for name, value in os.environ.items() if name.upper() != "NO_PROXY"} | {"NO_PROXY": "127.0.0.1"}
        outcome = run_contained(ChildRequest(executable, tuple(arguments), cwd=scratch, environment=environment,
                                             deadline=_WORKER_DEADLINE, record=record))
    finally:
        endpoint.close()
    recorded = OwnerFile.decode(owner_file.read_bytes()).children
    return {"timed_out": outcome.timed_out, "endpoint_connected": endpoint.connected.is_set(),
            "worker_recorded": recorded == (outcome.identity,), "worker_ended": _dead(outcome.identity),
            "stdout_empty": outcome.stdout == b""}


def _helper_parent_killed(identity_path: Path, marker: Path, *, running: bool) -> None:
    """Run a child that records itself, then either block before its resume or let it run."""
    def record(identity: ProcessIdentity) -> None:
        _write_identity(identity_path, identity)
        if not running:
            threading.Event().wait()

    run_contained(_stand_in(_MARK_AND_SLEEP if running else _MARK, str(marker), record=record))


def _helper_limited(result: Path, marker: Path) -> None:
    """Join a job limited to one active process, then try a contained creation and report it."""
    api = KERNEL.api
    job = api.CreateJobObjectW(None, None)
    limits = native.JOBOBJECT_BASIC_LIMIT_INFORMATION()
    limits.LimitFlags, limits.ActiveProcessLimit = _LIMIT_ACTIVE_PROCESS, 1
    if not api.SetInformationJobObject(job, _JOB_BASIC_LIMITS, limits, ctypes.sizeof(limits)) or not api.AssignProcessToJobObject(
            job, api.GetCurrentProcess()):
        raise ctypes.WinError(ctypes.get_last_error())
    report: dict[str, object] = {"error": None, "call": None}
    try:
        run_contained(_stand_in(_MARK, str(marker), deadline=10))
    except ContainmentError as error:
        report = {"error": type(error).__name__, "call": error.call, "winerror": error.error}
    accounting = native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
    api.QueryInformationJobObject(job, native.JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION, accounting, ctypes.sizeof(accounting), None)
    result.write_text(json.dumps({**report, "job_total_processes": accounting.TotalProcesses}), encoding="utf-8")


def _helper_teardown_failure(pid_file: Path) -> None:
    """Run a descendant-holding child with a failing termination, report the error, then exit normally."""
    try:
        run_contained(_stand_in(_SPAWN_DESCENDANT, str(pid_file), deadline=10), api=_FailingTerminate())
    except UnconfirmedEndError as error:
        handle = KERNEL.open_process(int(pid_file.read_text(encoding="utf-8")))
        alive = KERNEL.alive(handle)
        KERNEL.close(handle)
        sys.stdout.write(json.dumps({"error": type(error).__name__, "call": error.call, "descendant_alive": alive}))
        sys.stdout.flush()


def run_helper(name: str, arguments: Sequence[str]) -> int:
    """Dispatch one helper parent of the recorder's `--helper` mode."""
    paths = [Path(argument) for argument in arguments]
    if name in {"suspended", "running"}:
        _helper_parent_killed(paths[0], paths[1], running=name == "running")
    elif name == "limited":
        _helper_limited(paths[0], paths[1])
    else:
        _helper_teardown_failure(paths[0])
    return 0


# eof
