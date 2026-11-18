"""Record the native checks of the Windows child layer on a real kernel, outside pytest.

Step 2 of v0.14.0 git-cliff-provisioning (plan decisions Q06 and Q07). Started
by hand and never imported by a test, from the project root:

    python -m tests.unit.tools.release_workflow.git_cliff_native_checks --milestone step-2
        --output tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json

`--milestone` selects the cumulative due set; Steps 4, 5 and 8 add their
milestones and checks. Each check runs on stand-in children (the interpreter
with a short script) and temporary paths outside the repository and
`.tools/git-cliff/`, and ends every process it started. Since code review
round 1 of Step 2, each check also runs in its own runner process, this module
started with `--run-check`, through `run_contained` with the check's bound as
deadline: a check that stalls, even inside the production reap, is ended
job-wide with its whole helper tree and recorded `timed-out`. The record's
`recorder_timeout` entry proves that bound on a deliberately stalled runner
whose helper child is alive at the bound and ended after it. Helper parents
are this module started with `--helper`. The Step 2 set:

- `job-membership-before-resume`: `IsProcessInJob` of the created child and its
  job, from the recording callback, before `ResumeThread`.
- `suspended-child-ends-with-parent`: a helper records its child and blocks
  before resume; the helper is killed and its suspended child ends, never run.
- `process-limit-refuses-creation`: a helper inside a job limited to one active
  process gets the job-list creation refused; its job counted only itself.
  (A job with UI limits did not refuse the nesting on Windows 11 build 26200.)
- `kill-on-close-running-child`: a helper's running child ends once the helper
  is killed.
- `descendant-holding-stdout`: the root exits while its descendant keeps the
  captured stdout open; the descendant is still alive when the teardown
  starts, the call returns within its bound and the descendant has ended.
- `teardown-failure-exit`: a helper whose `TerminateJobObject` is made to fail
  (an `api` wrapper over the real kernel) while a descendant holds its pipe
  sees the descendant alive after the error, still exits normally, and
  kill-on-close then ends that descendant; the helper runs inside this
  recorder's own bounded job, observed before that job's own termination.
- `guard-held-before-start` and `inherited-guard-during-child`: a rename is
  refused while the guard is held before any child, and while a child runs
  with the inherited guard after the parent closed its own copy.

The record holds each check's outcome, expected and observed observations,
bound, duration and the LF-normalized SHA-256 of the sources it exercises,
plus the commit, the Windows build and the architecture. It is written with
sorted keys and LF endings, and refused if it still holds a host path.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import platform
import re
import subprocess
import sys
import tempfile
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tools.release_workflow import windows_native as native
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
    process_state,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_ROOT = Path(__file__).resolve().parents[4]
_MODULE = "tests.unit.tools.release_workflow.git_cliff_native_checks"
_MILESTONES = ("step-2",)
_HOST_PATH = re.compile(r"[A-Za-z]:[\\/]\S*|[\\/](?:Users|home)[\\/]\S*")
_RECORDER = "tests/unit/tools/release_workflow/git_cliff_native_checks.py"
_CHILD = ("tools/release_workflow/windows_native.py", "tools/release_workflow/windows_child.py",
          "tools/release_workflow/windows_process.py", _RECORDER)
_GUARD = (*_CHILD, "tools/release_workflow/windows_guard.py")
_SYNCHRONIZE = 0x00100000
_INVALID_PARAMETER = 87
_JOB_BASIC_LIMITS = 2
_LIMIT_ACTIVE_PROCESS = 0x00000008
_POLL = 0.05
_SETTLE = 5.0
_TERMINATE = "TerminateJobObject"
_STALLED = "stalled-runner"
_STALL_BOUND = 3
_STALL_SECONDS = 120
_MARK = "import pathlib, sys; pathlib.Path(sys.argv[1]).write_text('ran')"
_MARK_AND_SLEEP = "import pathlib, sys, time; pathlib.Path(sys.argv[1]).write_text('ran'); time.sleep(120)"
_SPAWN_DESCENDANT = ("import pathlib, subprocess, sys; child = subprocess.Popen([sys.executable, '-I', '-c', 'import time; time.sleep(120)']); "
                     "pathlib.Path(sys.argv[1]).write_text(str(child.pid)); print(child.pid, flush=True)")
_WAIT_FOR_RELEASE = ("import pathlib, sys, time\nend = time.monotonic() + 30\n"
                     "while not pathlib.Path(sys.argv[1]).exists() and time.monotonic() < end:\n    time.sleep(0.05)")
_ABOUT = ("Native checks of the v0.14.0 git-cliff-provisioning Windows child layer, written by "
          "tests/unit/tools/release_workflow/git_cliff_native_checks.py on a real kernel with stand-in children and temporary "
          "paths. A check passes when its observation equals its expectation within its bound; sources holds the LF-normalized "
          "SHA-256 of every repository file the check exercises.")


class CheckTimeoutError(RuntimeError):
    """A bounded wait of a check expired."""


class _Kernel32:
    """The few kernel32 calls only this recorder makes, declared on their own library instance."""

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
        """Close a handle this recorder opened."""
        if handle:
            self.api.CloseHandle(handle)


_K = _Kernel32()


class _Observed:
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


class _FailingTerminate(_Observed):
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
    end = time.monotonic() + _SETTLE
    while process_state(identity) is not ProcessState.DEAD:
        if time.monotonic() > end:
            return False
        time.sleep(_POLL)
    return True


def _helper(name: str, *arguments: Path) -> subprocess.Popen[bytes]:
    """Start this module as a helper parent."""
    command = [sys.executable, "-m", _MODULE, "--helper", name, *map(str, arguments)]
    return subprocess.Popen(command, cwd=_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)  # noqa: S603


def _kill(helper: subprocess.Popen[bytes]) -> None:
    """End a helper parent, as a crash would, and reap it."""
    helper.kill()
    helper.communicate(timeout=_SETTLE)


def _check_membership(bound: float, scratch: Path) -> dict[str, object]:
    """The created child is in its job before it resumes."""
    del scratch
    observed = _Observed()
    seen: dict[str, bool] = {}

    def record(identity: ProcessIdentity) -> None:
        del identity
        seen["in_job"] = is_process_in_job(observed.information.hProcess, observed.job)

    outcome = run_contained(_stand_in("pass", deadline=bound, record=record), api=observed)
    return {"in_job_before_resume": seen.get("in_job"), "status": outcome.status, "timed_out": outcome.timed_out}


def _check_parent_killed(name: str, bound: float, scratch: Path) -> dict[str, object]:
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


def _check_process_limit(bound: float, scratch: Path) -> dict[str, object]:
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


def _check_descendant(bound: float, scratch: Path) -> dict[str, object]:
    """The root exits while its descendant holds stdout: the call returns, the descendant ended by the teardown."""
    pid_file = scratch / "descendant.pid"
    seen: dict[str, Any] = {}

    def before_terminate() -> None:
        seen["handle"] = _K.open_process(int(pid_file.read_text(encoding="utf-8")))
        seen["alive"] = _K.alive(seen["handle"])

    observed = _Observed(before_terminate)
    outcome = run_contained(_stand_in(_SPAWN_DESCENDANT, str(pid_file), deadline=bound / 2), api=observed)
    observed.raise_hook_error()
    return {"status": outcome.status, "timed_out": outcome.timed_out, "descendant_alive_at_teardown": seen["alive"],
            "descendant_ended": _K.ended(seen["handle"], _SETTLE)}


def _check_teardown_failure(bound: float, scratch: Path) -> dict[str, object]:
    """A helper whose termination fails still exits normally, and kill-on-close then ends its descendant."""
    pid_file = scratch / "teardown.pid"
    ended: list[bool] = []
    observed = _Observed(lambda: ended.append(_K.ended(_K.open_process(int(pid_file.read_text(encoding="utf-8"))), _SETTLE)))
    request = ChildRequest(Path(sys.executable), ("-m", _MODULE, "--helper", "teardown-failure", str(pid_file)), cwd=_ROOT, deadline=bound / 2)
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


def _check_guard_before_start(bound: float, scratch: Path) -> dict[str, object]:
    """The guard alone refuses the rename until it is closed."""
    del bound
    executable, moved = scratch / "guarded.exe", scratch / "moved.exe"
    executable.write_bytes(b"stand-in executable")
    guard = open_guard(executable)
    while_held = _rename(executable, moved)
    guard.close()
    return {"while_held": while_held, "after_close": _rename(executable, moved)}


def _check_inherited_guard(bound: float, scratch: Path) -> dict[str, object]:
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
    _await(lambda: "during_child" in results, _SETTLE, "the rename attempt")
    return {**results, "after_child": _rename(executable, moved), "status": outcome.status}


@dataclass(frozen=True)
class _Check:
    """One native check: its milestone, expected observation, bound, sources and run."""

    identifier: str
    milestone: str
    expected: dict[str, object]
    bound: float
    sources: tuple[str, ...]
    run: Callable[[float, Path], dict[str, object]]


_CHECKS = (
    _Check("job-membership-before-resume", "step-2", {"in_job_before_resume": True, "status": 0, "timed_out": False}, 30, _CHILD,
           _check_membership),
    _Check("suspended-child-ends-with-parent", "step-2", {"child_ended": True, "child_ran": False}, 60, _CHILD,
           lambda bound, scratch: _check_parent_killed("suspended", bound, scratch)),
    _Check("process-limit-refuses-creation", "step-2",
           {"error": "ContainmentError", "call": "CreateProcessW", "child_ran": False, "job_total_processes": 1}, 60, _CHILD,
           _check_process_limit),
    _Check("kill-on-close-running-child", "step-2", {"child_ran": True, "child_ended": True}, 60, _CHILD,
           lambda bound, scratch: _check_parent_killed("running", bound, scratch)),
    _Check("descendant-holding-stdout", "step-2",
           {"status": 0, "timed_out": False, "descendant_alive_at_teardown": True, "descendant_ended": True}, 20, _CHILD,
           _check_descendant),
    _Check("teardown-failure-exit", "step-2",
           {"helper_error": "UnconfirmedEndError", "helper_call": "TerminateJobObject", "descendant_alive_after_error": True,
            "helper_status": 0, "helper_timed_out": False, "descendant_ended": True}, 60, _CHILD,
           _check_teardown_failure),
    _Check("guard-held-before-start", "step-2", {"while_held": "refused", "after_close": "renamed"}, 30, _GUARD,
           _check_guard_before_start),
    _Check("inherited-guard-during-child", "step-2",
           {"parent_guard_closed": True, "during_child": "refused", "after_child": "renamed", "status": 0}, 60, _GUARD,
           _check_inherited_guard),
)


def _helper_parent_killed(identity_path: Path, marker: Path, *, running: bool) -> None:
    """Run a child that records itself, then either block before its resume or let it run."""
    def record(identity: ProcessIdentity) -> None:
        _write_identity(identity_path, identity)
        if not running:
            threading.Event().wait()

    run_contained(_stand_in(_MARK_AND_SLEEP if running else _MARK, str(marker), record=record))


def _helper_limited(result: Path, marker: Path) -> None:
    """Join a job limited to one active process, then try a contained creation and report it."""
    api = _K.api
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
        handle = _K.open_process(int(pid_file.read_text(encoding="utf-8")))
        alive = _K.alive(handle)
        _K.close(handle)
        sys.stdout.write(json.dumps({"error": type(error).__name__, "call": error.call, "descendant_alive": alive}))
        sys.stdout.flush()


def _run_helper(name: str, arguments: Sequence[str]) -> int:
    """Dispatch one helper parent."""
    paths = [Path(argument) for argument in arguments]
    if name in {"suspended", "running"}:
        _helper_parent_killed(paths[0], paths[1], running=name == "running")
    elif name == "limited":
        _helper_limited(paths[0], paths[1])
    else:
        _helper_teardown_failure(paths[0])
    return 0


def _run_check(identifier: str, scratch: Path, output: Path) -> int:
    """Runner mode: run one check and write its observation or failure; the stall check never returns."""
    if identifier == _STALLED:
        helper = subprocess.Popen([sys.executable, "-I", "-c", "import time; time.sleep(120)"])  # noqa: S603
        output.write_text(str(helper.pid), encoding="utf-8")
        time.sleep(_STALL_SECONDS)
        return 1
    check = next(check for check in _CHECKS if check.identifier == identifier)
    try:
        report: dict[str, object] = {"observed": check.run(check.bound, scratch)}
    except (CheckTimeoutError, subprocess.TimeoutExpired) as error:
        report = {"outcome": "timed-out", "reason": _HOST_PATH.sub("<path>", str(error))}
    except Exception as error:  # noqa: BLE001 - a check that cannot run is recorded, never raised
        report = {"outcome": "cannot-run", "reason": _HOST_PATH.sub("<path>", f"{type(error).__name__}: {error}")}
    output.write_text(json.dumps(report), encoding="utf-8")
    return 0


def _runner(identifier: str, scratch: Path, output: Path, bound: float, api: _Observed | None = None) -> tuple[bool, str]:
    """Run a check in its own runner process, contained and ended job-wide at its bound; return expiry and stderr."""
    request = ChildRequest(Path(sys.executable), ("-m", _MODULE, "--run-check", identifier, str(scratch), str(output)), cwd=_ROOT,
                           deadline=bound)
    outcome = run_contained(request, api=api)
    return outcome.timed_out, outcome.stderr.decode("utf-8", "replace")[-400:]


def _digest(path: str) -> str:
    """Hash a repository file with LF line endings."""
    return hashlib.sha256((_ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _outcome(check: _Check, scratch: Path) -> tuple[str, dict[str, object], dict[str, str]]:
    """Run a check under its bound and read its outcome, observation and details."""
    result = scratch / "result.json"
    try:
        timed_out, errors = _runner(check.identifier, scratch, result, check.bound)
    except ContainmentError as error:
        return "cannot-run", {}, {"reason": _HOST_PATH.sub("<path>", str(error))}
    if timed_out:
        return "timed-out", {}, {"reason": f"the check runner was ended job-wide at its {check.bound} s bound"}
    if not result.exists():
        return "cannot-run", {}, {"reason": _HOST_PATH.sub("<path>", errors) or "the check runner wrote no result"}
    report = json.loads(result.read_text(encoding="utf-8"))
    if "observed" not in report:
        return report["outcome"], {}, {"reason": report["reason"]}
    return ("passed" if report["observed"] == check.expected else "failed"), report["observed"], {}


def _record(check: _Check) -> dict[str, object]:
    """Run one check in its own scratch directory and runner process, and record its outcome."""
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="git-cliff-native-", ignore_cleanup_errors=True) as scratch:
        outcome, observed, details = _outcome(check, Path(scratch))
    duration = round(time.monotonic() - start, 3)
    if outcome == "passed" and duration > check.bound:
        outcome = "timed-out"
    return {"id": check.identifier, "outcome": outcome, "expected": check.expected, "observed": observed, "details": details,
            "bound_seconds": check.bound, "duration_seconds": duration, "sources": {path: _digest(path) for path in check.sources}}


def _demonstrate_timeout() -> dict[str, object]:
    """Run a deliberately stalled runner with a helper child: alive at the bound, the whole tree ended after it."""
    seen: dict[str, Any] = {}
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="git-cliff-native-", ignore_cleanup_errors=True) as scratch:
        pid_file = Path(scratch) / "stalled.pid"

        def before_terminate() -> None:
            seen["handle"] = _K.open_process(int(pid_file.read_text(encoding="utf-8")))
            seen["alive"] = _K.alive(seen["handle"])

        observed = _Observed(before_terminate)
        timed_out, _errors = _runner(_STALLED, Path(scratch), pid_file, _STALL_BOUND, observed)
        observed.raise_hook_error()
        ended = _K.ended(seen["handle"], _SETTLE)
    return {"bound_seconds": _STALL_BOUND, "duration_seconds": round(time.monotonic() - start, 3),
            "observed": {"timed_out": timed_out, "helper_alive_at_bound": seen["alive"], "helper_tree_ended": ended}}


def main(argv: Sequence[str] | None = None) -> int:
    """Run the due checks of a milestone and write the record, or run one helper parent."""
    parser = argparse.ArgumentParser(description="Record the native checks of the git-cliff provisioning Windows layer.")
    parser.add_argument("--milestone", choices=_MILESTONES)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--helper", help=argparse.SUPPRESS)
    parser.add_argument("--run-check", help=argparse.SUPPRESS)
    parser.add_argument("helper_arguments", nargs="*", help=argparse.SUPPRESS)
    arguments = parser.parse_args(argv)
    if arguments.helper:
        return _run_helper(arguments.helper, arguments.helper_arguments)
    if arguments.run_check:
        return _run_check(arguments.run_check, Path(arguments.helper_arguments[0]), Path(arguments.helper_arguments[1]))
    if arguments.milestone is None or arguments.output is None:
        parser.error("--milestone and --output are required")
    return _record_milestone(arguments.milestone, Path(arguments.output))


def _record_milestone(milestone: str, output: Path) -> int:
    """Run the due checks of a milestone and the timeout demonstration, then write the record."""
    position = _MILESTONES.index(milestone)
    checks = [_record(check) for check in _CHECKS if _MILESTONES.index(check.milestone) <= position]
    timeout = _demonstrate_timeout()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True, text=True, check=True).stdout.strip()  # noqa: S603, S607
    record = {"format": 1, "about": _ABOUT, "milestone": milestone, "commit": commit,
              "host": {"windows_build": platform.version(), "architecture": platform.machine()}, "checks": checks,
              "recorder_timeout": timeout}
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if _HOST_PATH.search(text) is not None:
        msg = "the record still holds a host path; nothing was written"
        raise SystemExit(msg)
    output.write_bytes(text.encode("utf-8"))
    for check in checks:
        sys.stdout.write(f"{check['outcome']:>10}  {check['duration_seconds']:>7.3f} s  {check['id']}\n")
    sys.stdout.write(f"  timeout:  {timeout['duration_seconds']:>7.3f} s  {timeout['observed']}\n")
    return 0 if all(check["outcome"] == "passed" for check in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())


# eof
