"""The final native checks: the production `bin/gcliff.bat` and the admitted 2.14.2, its launcher killed while git-cliff runs.

Step 8 of v0.14.0 git-cliff-provisioning (design "Child process lifecycle",
"Reuse check and the use guard" and the acceptance row "Launcher dies while its
git-cliff child runs"). The recorder `git_cliff_native_checks.py` runs it at
milestone `final`, inside its bounded runner; nothing here is imported by a
test. Unlike the Step 5 checks, it uses no stand-in: the caller is the shipped
launcher and the child the admitted git-cliff of this checkout's cache.

1. Warm-up: `bin/gcliff.bat --version` from the check's scratch directory,
   outside any worktree, selects the manifest default, provisions it in this
   checkout's `.tools/git-cliff/` when its entry is not valid yet (network),
   and prints `git-cliff 2.14.2`.
2. The recorder serves a named pipe it never writes, and starts
   `bin/gcliff.bat --from-context <pipe>` through `cmd.exe` from the scratch
   directory: git-cliff reads its context from that pipe and stays alive, and
   no handle its launcher shares has a pending read.
3. The launcher is the interpreter that created the git-cliff of the
   production entry. Since code review round 1, both come from
   `git_cliff_native_ownership.owned_run`: the one run of the executable whose
   chain of older parents reaches the check's own `cmd.exe`, so a concurrent
   invocation of the same executable is never chosen, and two own runs stop
   the check before anything is ended; each is then opened and checked
   against its recorded creation time. Since code review round 2, the run is
   taken only once the pipe names its client (`GetNamedPipeClientProcessId`),
   and must be that client: the guarded `--version` reuse probe that the same
   launcher runs just before never opens the pipe, so it is never observed in
   its place, and a run that never opens the pipe is not ready at the bound.
   Among the launcher's handle values,
   the job is the one `IsProcessInJob` places git-cliff in (the recorder
   keeps a duplicate, so the job's kill-on-close waits for the recorder too),
   and the guard is the one whose file is the executable.
4. The launcher is killed. git-cliff is still alive, its handle of the guard's
   value names the executable, and the rename is refused; the recorder ends
   the job, git-cliff ends, and the rename succeeds (and is undone at once).
5. A control run of the same executable on another silent pipe, contained
   without any guard, leaves the rename possible while that control child,
   the client of its pipe, waits.

`check_gcliff_status_with_inherited_errorlevel` (code review round 1) runs
`bin/gcliff.bat` with a caller variable `ERRORLEVEL=0` and a usage error,
which must still return 2, then with `ERRORLEVEL=7` and a template whose
`get_env` prints the variable git-cliff sees, rendered from a one-release
context derived from this git-cliff's own `--context` output: status 0 and
`seen=7`.
"""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import time
from ctypes import wintypes
from typing import TYPE_CHECKING, Any, Self

from tests.unit.tools.release_workflow.git_cliff_native_ownership import (
    OwnershipError,
    ProcessRecord,
    await_ready_run,
)
from tests.unit.tools.release_workflow.git_cliff_native_probes import (
    ROOT,
    SETTLE,
    Observed,
    _rename,
)
from tests.unit.tools.release_workflow.git_cliff_native_service import KERNEL
from tools.release_workflow import windows_native as native
from tools.release_workflow.git_cliff.cache import CacheLayout
from tools.release_workflow.git_cliff.manifest import (
    ADMITTED_PINS,
    admitted,
    default_version,
)
from tools.release_workflow.windows_child import ChildRequest, run_contained

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from types import TracebackType

_GCLIFF = ROOT / "bin" / "gcliff.bat"
_SNAPSHOT_PROCESSES = 0x2
_INVALID_HANDLE = wintypes.HANDLE(-1).value
_QUERY_LIMITED = 0x1000
_PROCESS_ACCESS = 0x0001 | 0x0040 | _QUERY_LIMITED | 0x00100000  # terminate, duplicate handles, limited query, synchronize
_DUPLICATE_SAME_ACCESS = 2
_PIPE_ACCESS_OUTBOUND = 2
_HANDLE_LIMIT = 0x10000
_PATH_LENGTH = 1024
_CONTROL_SECONDS = 3.0
_CONTEXT_SECONDS = 60
_HIGH_WORD_SHIFT = 32
_CHAIN_DEPTH = 16
_TEMPLATE = '[changelog]\nbody = """seen={{ get_env(name="ERRORLEVEL", default="unset") }}"""\n'


class _ProcessEntry(ctypes.Structure):
    """`PROCESSENTRY32W`, one process of a snapshot."""

    _fields_ = (("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG), ("dwFlags", wintypes.DWORD),
                ("szExeFile", wintypes.WCHAR * 260))


def _declared() -> Any:  # noqa: ANN401 - a ctypes library with declared functions
    """Declare the kernel32 calls only this check makes, on their own library instance."""
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    api.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    for name in ("Process32FirstW", "Process32NextW"):
        getattr(api, name).argtypes = [wintypes.HANDLE, ctypes.POINTER(_ProcessEntry)]
    api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    api.OpenProcess.restype = wintypes.HANDLE
    api.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    api.GetProcessTimes.argtypes = [wintypes.HANDLE, *[ctypes.POINTER(wintypes.FILETIME)] * 4]
    api.GetProcessTimes.restype = wintypes.BOOL
    api.GetCurrentProcess.restype = wintypes.HANDLE
    api.DuplicateHandle.argtypes = [wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD,
                                    wintypes.BOOL, wintypes.DWORD]
    api.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
    api.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    api.GetFinalPathNameByHandleW.restype = wintypes.DWORD
    api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CreateNamedPipeW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
                                     wintypes.DWORD, wintypes.LPVOID]
    api.CreateNamedPipeW.restype = wintypes.HANDLE
    api.GetNamedPipeClientProcessId.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.ULONG)]
    api.GetNamedPipeClientProcessId.restype = wintypes.BOOL
    return api


_API = _declared()


def _same(path: str | None, executable: Path) -> bool:
    """Tell whether a reported path names the executable, whatever its spelling."""
    return path is not None and os.path.normcase(path.removeprefix("\\\\?\\")) == os.path.normcase(os.path.realpath(executable))


def _processes() -> Iterator[tuple[int, int]]:
    """Yield the PID and parent PID of every process in a fresh snapshot."""
    snapshot = _API.CreateToolhelp32Snapshot(_SNAPSHOT_PROCESSES, 0)
    if snapshot in {None, _INVALID_HANDLE}:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        entry = _ProcessEntry(dwSize=ctypes.sizeof(_ProcessEntry))
        found = _API.Process32FirstW(snapshot, ctypes.byref(entry))
        while found:
            yield entry.th32ProcessID, entry.th32ParentProcessID
            found = _API.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        _API.CloseHandle(snapshot)


def _image(pid: int) -> str | None:
    """Name the image of a process, or None when it cannot be opened."""
    process = _API.OpenProcess(_QUERY_LIMITED, 0, pid)
    if not process:
        return None
    try:
        buffer, size = ctypes.create_unicode_buffer(_PATH_LENGTH), wintypes.DWORD(_PATH_LENGTH)
        return buffer.value if _API.QueryFullProcessImageNameW(process, 0, buffer, ctypes.byref(size)) else None
    finally:
        _API.CloseHandle(process)


def _created(process: int) -> int | None:
    """Read the creation time of an open process, or None when it cannot be read."""
    created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
    if not _API.GetProcessTimes(process, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):
        return None
    return (created.dwHighDateTime << _HIGH_WORD_SHIFT) | created.dwLowDateTime


def _creation(pid: int) -> int | None:
    """Read the creation time of a process by PID, or None when it cannot be opened or read."""
    process = _API.OpenProcess(_QUERY_LIMITED, 0, pid)
    if not process:
        return None
    try:
        return _created(process)
    finally:
        _API.CloseHandle(process)


def _table(executable: Path) -> dict[int, ProcessRecord]:
    """Snapshot every process, then record each run of the executable with its ancestors and their creation times."""
    parents = dict(_processes())
    runs = {pid for pid in parents if _same(_image(pid), executable)}
    table: dict[int, ProcessRecord] = {}
    for pid in runs:
        current = pid
        for _ in range(_CHAIN_DEPTH):
            if current not in parents or current in table:
                break
            table[current] = ProcessRecord(current, parents[current], _creation(current), current in runs)
            current = parents[current]
    return table


def _open(record: ProcessRecord) -> int:
    """Open a recorded process for ending and inspection, refusing a PID that another process now holds."""
    handle = _API.OpenProcess(_PROCESS_ACCESS, 0, record.pid)
    if not handle:
        msg = f"process {record.pid} could not be opened"
        raise OwnershipError(msg)
    if _created(handle) != record.created:
        _API.CloseHandle(handle)
        msg = f"process {record.pid} is no longer the one the snapshot recorded"
        raise OwnershipError(msg)
    return handle


class _SilentPipe:
    """A named pipe server this process never writes, so a reader of its client end waits until it is closed."""

    def __init__(self, label: str) -> None:
        """Create the server end under a name of this process."""
        self.name = f"\\\\.\\pipe\\llm-shared-gcliff-native-{os.getpid()}-{label}"
        self._handle = _API.CreateNamedPipeW(self.name, _PIPE_ACCESS_OUTBOUND, 0, 1, 4096, 4096, 0, None)
        if self._handle in {None, _INVALID_HANDLE}:
            raise ctypes.WinError(ctypes.get_last_error())

    def __enter__(self) -> Self:
        """Serve the pipe for a block."""
        return self

    def client(self) -> int | None:
        """Name the process that opened the client end, or None while none has (code review round 2)."""
        pid = wintypes.ULONG()
        return pid.value if _API.GetNamedPipeClientProcessId(self._handle, ctypes.byref(pid)) else None

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None, trace: TracebackType | None) -> None:
        """Close the server end, which ends any read with end of file."""
        _API.CloseHandle(self._handle)


def _duplicate(process: int, value: int) -> int:
    """Duplicate one handle value of another process into this one, or 0 when it is no handle there."""
    copy = wintypes.HANDLE()
    if not _API.DuplicateHandle(process, value, _API.GetCurrentProcess(), ctypes.byref(copy), 0, 0, _DUPLICATE_SAME_ACCESS):
        return 0
    return copy.value or 0


def _file_name(handle: int) -> str | None:
    """Name the file behind a handle of this process, or None when it is not one."""
    buffer = ctypes.create_unicode_buffer(_PATH_LENGTH)
    length = _API.GetFinalPathNameByHandleW(handle, buffer, _PATH_LENGTH, 0)
    return buffer.value if 0 < length < _PATH_LENGTH else None


def _job_and_guard(launcher: int, child: int, executable: Path) -> tuple[int, int]:
    """Find, among the launcher's handle values, a duplicate of the job holding git-cliff and the value of the guard."""
    job, guard = 0, 0
    for value in range(4, _HANDLE_LIMIT, 4):
        copy = _duplicate(launcher, value)
        if not copy:
            continue
        member = wintypes.BOOL()
        if not job and _API.IsProcessInJob(child, copy, ctypes.byref(member)) and member.value:
            job = copy
            continue
        if not guard and _same(_file_name(copy), executable):
            guard = value
        _API.CloseHandle(copy)
        if job and guard:
            break
    return job, guard


def _control(executable: Path, scratch: Path) -> str:
    """Run git-cliff on a silent pipe with no guard at all and try the rename while that control child, its client, waits."""
    seen: dict[str, str] = {}

    with _SilentPipe("control") as pipe:

        def while_running() -> None:
            seen["rename"] = _rename(executable, executable.with_name("control-moved.exe")) if pipe.client() is not None else "not-running"

        observed = Observed(while_running)
        run_contained(ChildRequest(executable, ("--from-context", pipe.name), cwd=scratch, environment=dict(os.environ),
                                   deadline=_CONTROL_SECONDS), api=observed)
    observed.raise_hook_error()
    return seen.get("rename", "not-observed")


def _start(arguments: tuple[str, ...], scratch: Path, name: str, environment: dict[str, str] | None = None) -> subprocess.Popen[bytes]:
    """Start `bin/gcliff.bat` through cmd.exe from the scratch directory, its output kept in files there."""
    command = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(_GCLIFF), *arguments]
    with (scratch / f"{name}.out").open("wb") as stdout, (scratch / f"{name}.err").open("wb") as stderr:
        return subprocess.Popen(command, cwd=scratch, env=environment, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)  # noqa: S603


def _finished(arguments: tuple[str, ...], scratch: Path, name: str, bound: float, environment: dict[str, str] | None = None) -> tuple[int, str]:
    """Run `bin/gcliff.bat` to completion and return its status and what it printed."""
    gcliff = _start(arguments, scratch, name, environment)
    status = gcliff.wait(timeout=bound / 4)
    return status, (scratch / f"{name}.out").read_text(encoding="utf-8").strip()


def _executable() -> Path:
    """Locate the production entry of the manifest default in this checkout's cache."""
    return CacheLayout(ROOT).executable(admitted(str(default_version(ADMITTED_PINS)), ADMITTED_PINS))


def check_gcliff_launcher_killed(bound: float, scratch: Path) -> dict[str, object]:
    """After the production launcher was killed, git-cliff's inherited guard refuses the rename until the job ends it.

    Since code review round 1, the git-cliff run and its launcher are the ones that descend from the check's own
    `cmd.exe`, each opened and checked against its recorded creation time before anything is ended. Since round 2,
    the run is the client of the check's own pipe, observed only once that client exists, so the guarded `--version`
    reuse probe the same launcher starts first is never taken for it.
    """
    _status, version = _finished(("--version",), scratch, "warm-up", bound * 2)
    executable = _executable()
    moved = executable.with_name("moved.exe")
    child = launcher = job = 0
    with _SilentPipe("run") as pipe:
        gcliff = _start(("--from-context", pipe.name), scratch, "run")
        try:
            root = ProcessRecord(gcliff.pid, 0, _creation(gcliff.pid))
            run, owner = await_ready_run(pipe.client, lambda: _table(executable), root, seconds=bound / 4, clock=time.monotonic,
                                         sleep=time.sleep)
            child, launcher = _open(run), _open(owner)
            job, guard = _job_and_guard(launcher, child, executable)
            _API.TerminateProcess(launcher, 1)
            caller_dead = _API.WaitForSingleObject(launcher, int(SETTLE * 1000)) == native.WAIT_OBJECT_0
            alive = _API.WaitForSingleObject(child, 0) == native.WAIT_TIMEOUT
            inherited = bool(guard) and _same(KERNEL.file_of(run.pid, guard), executable)
            during = _rename(executable, moved)
        finally:
            emptied = KERNEL.end_job(job) if job else False
            gcliff.wait(timeout=SETTLE)
    ended = emptied and _API.WaitForSingleObject(child, int(SETTLE * 1000)) == native.WAIT_OBJECT_0
    for handle in (child, launcher):
        _API.CloseHandle(handle)
    return {"warm_up": version, "caller_dead": caller_dead, "child_alive": alive, "inherited_handle_is_guard": inherited,
            "during_child": during, "child_ended": ended, "after_child": _rename(executable, moved),
            "control_without_guard": _control(executable, scratch)}


def _single_release_context(executable: Path, scratch: Path) -> Path:
    """Write a context of one release without commits, in the form this git-cliff reads, from its own `--context` output."""
    full = scratch / "full-context.json"
    subprocess.run([str(executable), "--latest", "--context", "--output", str(full)], cwd=ROOT,  # noqa: S603
                   stdin=subprocess.DEVNULL, capture_output=True, check=True, timeout=_CONTEXT_SECONDS)
    release = json.loads(full.read_text(encoding="utf-8"))[0]
    release["commits"] = []
    context = scratch / "context.json"
    context.write_text(json.dumps([release]), encoding="utf-8")
    return context


def check_gcliff_status_with_inherited_errorlevel(bound: float, scratch: Path) -> dict[str, object]:
    """A caller variable named ERRORLEVEL hides neither a failing nor a succeeding status, and git-cliff still receives it.

    Code review round 1 of Step 8: `bin/gcliff.bat` runs with `ERRORLEVEL=0` and a usage error, then with
    `ERRORLEVEL=7` and a template that prints the variable git-cliff sees.
    """
    _status, version = _finished(("--version",), scratch, "warm-up", bound * 2)
    context = _single_release_context(_executable(), scratch)
    template = scratch / "cliff.toml"
    template.write_text(_TEMPLATE, encoding="utf-8")
    failing, _output = _finished(("--frobnicate",), scratch, "failing", bound, dict(os.environ) | {"ERRORLEVEL": "0"})
    succeeding, seen = _finished(("--config", str(template), "--from-context", str(context)), scratch, "succeeding", bound,
                                 dict(os.environ) | {"ERRORLEVEL": "7"})
    return {"warm_up": version, "failing_status": failing, "succeeding_status": succeeding, "child_saw": seen}


# eof
