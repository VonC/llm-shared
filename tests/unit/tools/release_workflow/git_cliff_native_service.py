"""The Step 5 native checks: the provisioning service on a real kernel, with helper callers that are killed.

Step 5 of v0.14.0 git-cliff-provisioning (plan decisions Q06 and Q07; design
"Child process lifecycle", "Reuse check and the use guard" and "Lock record
and transition mutex"). The recorder `git_cliff_native_checks.py` runs these
checks with `--milestone step-5` and dispatches their helper callers from its
`--helper` mode; nothing here is imported by a test. The probes module
`git_cliff_native_probes.py` had reached 470 lines, so the Step 5 checks live
here and reuse its helpers.

No pin is admitted before Step 7, so every check uses a temporary tooling
root, the synthetic pin 9.9.9 and, where git-cliff runs, an entry whose
executable is a stand-in: pip's vendored distlib console launcher followed by
a shebang naming this interpreter and a ZIP holding `__main__.py`. It prints
`git-cliff 9.9.9`; for any other argument than `--version` it marks that it
ran and waits, and with `LLM_SHARED_NATIVE_CHECK_WAIT` set it also waits after
`--version`. The temporary root holds no checkout, so a helper starts the
download worker through this checkout's bootstrap.

- `worker-ends-with-killed-caller`: a helper provisions with the proxy
  variables pointing at a local endpoint that accepts and never answers; once
  its worker is recorded in the lock record and connected, the helper is
  killed: kill-on-close ends the worker, and the lock record and staging stay
  for a later recovery.
- `git-cliff-run-ends-with-killed-caller`: a helper reuses the stand-in entry
  and starts its git-cliff run through the invocation object; once the run
  marked itself, the helper is killed and the run ends.
- `guard-held-by-reuse-probe-after-caller-killed` and
  `guard-held-by-git-cliff-run-after-caller-killed`: the recorder first takes
  a duplicate of the helper's job handle, so its kill-on-close waits for the
  recorder, and names the file behind the handle value the child inherited,
  which must be the guarded executable; after the helper was killed, the
  child's inherited guard refuses the executable rename; once the recorder
  ends the job and it counts no active process (the stand-in's interpreter,
  a member too, holds an inherited copy as well), the rename succeeds. Since
  code review round 1, a control run of the stand-in without any guard shows
  that its running image and its own reads leave the rename possible.
- `abandoned-mutex-keeps-lock-record`: a helper holds the cache lock, then a
  thread of it takes the transition mutex and ends without releasing it; the
  recorder observes the abandoned mutex, its own waiter fails at a 2 s wait
  naming the live holder, and the lock record is unchanged.
"""

from __future__ import annotations

import ctypes
import dataclasses
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import threading
import time
import zipfile
from ctypes import wintypes
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tests.unit.tools.release_workflow.git_cliff_native_probes import (
    RECORDER_MODULE,
    ROOT,
    SETTLE,
    Observed,
    _await,
    _dead,
    _kill,
    _rename,
    _SilentEndpoint,
)
from tools.release_workflow import windows_native as native
from tools.release_workflow.git_cliff.budget import resolve_budget
from tools.release_workflow.git_cliff.cache import CacheLayout, EntryRecord
from tools.release_workflow.git_cliff.cache_lock import (
    CacheLock,
    LockRecord,
    LockSeams,
    LockWaitError,
)
from tools.release_workflow.git_cliff.invocation import Policy
from tools.release_workflow.git_cliff.manifest import PLATFORM_TRIPLE, AdmittedPin
from tools.release_workflow.git_cliff.provisioning import production_seams, provision
from tools.release_workflow.windows_child import ChildRequest, run_contained
from tools.release_workflow.windows_process import ProcessIdentity

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tools.release_workflow.windows_child import ChildOutcome

VERSION = "9.9.9"
PIN = AdmittedPin(version=VERSION, default=True, triple=PLATFORM_TRIPLE, asset=f"git-cliff-{VERSION}-{PLATFORM_TRIPLE}.zip", size=1024,
                  sha256="0" * 64, member=f"git-cliff-{VERSION}/git-cliff.exe", evidence="native-check")
HELPERS = frozenset({"service-worker", "service-run", "service-probe", "service-mutex"})
_MARK, _WAIT = "LLM_SHARED_NATIVE_CHECK_MARK", "LLM_SHARED_NATIVE_CHECK_WAIT"
_STAND_IN = f"""import os, pathlib, sys, time
sys.stdout.write("git-cliff {VERSION}\\n")
sys.stdout.flush()
if sys.argv[1:] != ["--version"]:
    pathlib.Path(os.environ["{_MARK}"]).write_text("ran", encoding="utf-8")
    time.sleep(120)
elif os.environ.get("{_WAIT}"):
    time.sleep(120)
"""
_SYNCHRONIZE = 0x00100000
_PROCESS_DUP_HANDLE_AND_SYNCHRONIZE = 0x0040 | _SYNCHRONIZE
_DUPLICATE_SAME_ACCESS = 2
_WAIT_ABANDONED = 0x80
_INFINITE = 0xFFFFFFFF
_WAITER_SECONDS = 2.0
_CONTROL_SECONDS = 3.0
_PATH_LENGTH = 1024


class _Kernel:
    """The kernel32 calls only these checks make, declared on their own library instance."""

    def __init__(self) -> None:
        """Declare them."""
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenProcess.restype = wintypes.HANDLE
        api.GetCurrentProcess.restype = wintypes.HANDLE
        api.DuplicateHandle.argtypes = [wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD,
                                        wintypes.BOOL, wintypes.DWORD]
        api.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
        api.CreateMutexW.restype = wintypes.HANDLE
        api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        api.WaitForSingleObject.restype = wintypes.DWORD
        api.ReleaseMutex.argtypes = [wintypes.HANDLE]
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        api.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
        api.GetFinalPathNameByHandleW.restype = wintypes.DWORD
        api.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        api.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.POINTER(native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION),
                                                  wintypes.DWORD, wintypes.LPVOID]
        self.api: Any = api

    def end_job(self, job: int) -> bool:
        """End every member of a job, wait until it counts no active process, then close it; tell whether it emptied."""
        accounting = native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
        try:
            self.api.TerminateJobObject(job, 1)
            end = time.monotonic() + SETTLE
            while time.monotonic() < end:
                self.api.QueryInformationJobObject(job, native.JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION, ctypes.byref(accounting),
                                                   ctypes.sizeof(accounting), None)
                if not accounting.ActiveProcesses:
                    return True
                time.sleep(0.05)
            return False
        finally:
            self.api.CloseHandle(job)

    def duplicate_job(self, helper: int, job: int) -> int:
        """Take a handle on a helper's job, so its kill-on-close waits for this process too."""
        process = self.api.OpenProcess(_PROCESS_DUP_HANDLE_AND_SYNCHRONIZE, 0, helper)
        if not process:
            raise ctypes.WinError(ctypes.get_last_error())
        copy = wintypes.HANDLE()
        try:
            if not self.api.DuplicateHandle(process, job, self.api.GetCurrentProcess(), ctypes.byref(copy), 0, 0, _DUPLICATE_SAME_ACCESS):
                raise ctypes.WinError(ctypes.get_last_error())
        finally:
            self.api.CloseHandle(process)
        return copy.value or 0

    def file_of(self, pid: int, value: int) -> str | None:
        """Name the file a handle value of another process refers to, through a copy closed at once; None when it is not one."""
        process = self.api.OpenProcess(_PROCESS_DUP_HANDLE_AND_SYNCHRONIZE, 0, pid)
        if not process:
            return None
        copy = wintypes.HANDLE()
        try:
            if not self.api.DuplicateHandle(process, value, self.api.GetCurrentProcess(), ctypes.byref(copy), 0, 0, _DUPLICATE_SAME_ACCESS):
                return None
            buffer = ctypes.create_unicode_buffer(_PATH_LENGTH)
            length = self.api.GetFinalPathNameByHandleW(copy, buffer, _PATH_LENGTH, 0)
        finally:
            if copy.value:
                self.api.CloseHandle(copy)
            self.api.CloseHandle(process)
        return buffer.value.removeprefix("\\\\?\\") if 0 < length < _PATH_LENGTH else None

    def abandoned(self, name: str) -> bool:
        """Enter a named mutex once and tell whether its last owner abandoned it."""
        handle = self.api.CreateMutexW(None, 0, name)
        try:
            wait = self.api.WaitForSingleObject(handle, 1000)
            self.api.ReleaseMutex(handle)
        finally:
            self.api.CloseHandle(handle)
        return wait == _WAIT_ABANDONED


KERNEL = _Kernel()


def _stand_in_executable() -> bytes:
    """Build the stand-in: the distlib console launcher, a shebang naming this interpreter, then the script as a ZIP."""
    spec = importlib.util.find_spec("pip")
    if spec is None or spec.origin is None:
        msg = "pip, whose vendored distlib launcher builds the stand-in executable, is not installed"
        raise RuntimeError(msg)
    launcher = (Path(spec.origin).parent / "_vendor" / "distlib" / "t64.exe").read_bytes()
    interpreter = f'"{sys.executable}"' if " " in sys.executable else sys.executable
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("__main__.py", _STAND_IN)
    return launcher + f"#!{interpreter} -I\n".encode() + archive.getvalue()


def install_stand_in(tooling: Path) -> CacheLayout:
    """Publish a valid entry of the synthetic pin whose executable is the stand-in."""
    layout = CacheLayout(tooling)
    executable = _stand_in_executable()
    layout.entry_dir(PIN).mkdir(parents=True)
    layout.executable(PIN).write_bytes(executable)
    record = EntryRecord(version=VERSION, triple=PIN.triple, asset=PIN.asset, asset_sha256=PIN.sha256,
                         executable_sha256=hashlib.sha256(executable).hexdigest(), executable_size=len(executable),
                         provisioned="2026-11-20T10:00:00+01:00")
    layout.record(PIN).write_bytes(record.encode())
    return layout


def _helper(name: str, *arguments: Path, environment: dict[str, str] | None = None) -> subprocess.Popen[bytes]:
    """Start the recorder as a helper caller of the service."""
    command = [sys.executable, "-m", RECORDER_MODULE, "--helper", name, *map(str, arguments)]
    return subprocess.Popen(command, cwd=ROOT, env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)  # noqa: S603


def _published(path: Path) -> dict[str, int]:
    """Read what a helper published about its child."""
    return json.loads(path.read_text(encoding="utf-8"))


def _recorded_worker(lock: Path) -> ProcessIdentity | None:
    """Read the first child of a lock record being written by another process, or None for now."""
    try:
        children = LockRecord.decode(lock.read_bytes()).children
    except (OSError, ValueError, TypeError):
        return None
    return children[0] if children else None


def check_worker_killed(bound: float, scratch: Path) -> dict[str, object]:
    """A recorded, connected download worker ends with its killed caller; lock record and staging stay."""
    layout = CacheLayout(scratch / "tooling")
    lock = layout.lock_path(PIN)
    endpoint = _SilentEndpoint()
    proxy = f"http://127.0.0.1:{endpoint.port}"
    environment = {name: value for name, value in os.environ.items() if name.upper() not in {"NO_PROXY", "HTTPS_PROXY", "HTTP_PROXY"}}
    environment |= {"HTTPS_PROXY": proxy, "HTTP_PROXY": proxy}
    helper = _helper("service-worker", layout.tooling_root, environment=environment)
    try:
        _await(lambda: _recorded_worker(lock) is not None, bound / 2, "the worker's recording")
        _await(endpoint.connected.is_set, bound / 2, "the worker's connection")
        worker = _recorded_worker(lock)
    finally:
        _kill(helper)
        endpoint.close()
    staging = [path for path in layout.version_dir(PIN).iterdir() if path.name.startswith(".staging-")]
    return {"worker_recorded": worker is not None, "endpoint_connected": endpoint.connected.is_set(),
            "worker_ended": worker is not None and _dead(worker),
            "lock_record_kept": lock.exists(), "staging_kept": len(staging) == 1}


def check_run_killed(bound: float, scratch: Path) -> dict[str, object]:
    """A git-cliff run started through the invocation object ends with its killed caller."""
    install_stand_in(scratch / "tooling")
    published, mark = scratch / "run.json", scratch / "run.ran"
    helper = _helper("service-run", scratch / "tooling", published, mark)
    try:
        _await(lambda: published.exists() and mark.exists(), bound / 2, "the git-cliff run")
        child = _published(published)
    finally:
        _kill(helper)
    return {"child_ran": mark.exists(), "child_ended": _dead(ProcessIdentity(child["pid"], child["created"]))}


def _control_without_guard(executable: Path, scratch: Path) -> str:
    """Run the stand-in with no guard at all and try the rename while it runs: its image and own reads must not refuse it."""
    mark, moved = scratch / "control.ran", executable.with_name("control-moved.exe")
    seen: dict[str, str] = {}

    def while_running() -> None:
        seen["rename"] = _rename(executable, moved) if mark.exists() else "not-running"

    observed = Observed(while_running)
    run_contained(ChildRequest(executable, ("--native-check-control",), cwd=scratch, environment=dict(os.environ) | {_MARK: str(mark)},
                               deadline=_CONTROL_SECONDS), api=observed)
    observed.raise_hook_error()
    return seen.get("rename", "not-observed")


def check_guard_after_kill(kind: str, bound: float, scratch: Path) -> dict[str, object]:
    """After its caller was killed, the child's inherited copy of the guard refuses the rename until the job ends it.

    Since code review round 1 of Step 5, the check first proves that the handle the child inherited is the guard
    of this executable, and a control run of the same stand-in without any guard shows that the running image and
    its own reads leave the rename possible, so the refusal comes from the inherited guard.
    """
    layout = install_stand_in(scratch / "tooling")
    executable, moved = layout.executable(PIN), layout.entry_dir(PIN) / "moved.exe"
    published, mark = scratch / f"{kind}.json", scratch / f"{kind}.ran"
    environment = dict(os.environ) | ({_WAIT: "1"} if kind == "probe" else {})
    helper = _helper(f"service-{kind}", scratch / "tooling", published, mark, environment=environment)
    job = 0
    try:
        _await(published.exists, bound / 2, f"the {kind} child")
        child = _published(published)
        job = KERNEL.duplicate_job(child["helper"], child["job"])
        handle = KERNEL.api.OpenProcess(_SYNCHRONIZE, 0, child["pid"])
        guard = KERNEL.file_of(child["pid"], child["guard"])
    finally:
        _kill(helper)
    try:
        alive = KERNEL.api.WaitForSingleObject(handle, 0) == native.WAIT_TIMEOUT
        during = _rename(executable, moved)
    finally:
        # Every member, the stand-in's own interpreter included, holds a copy until the job has emptied.
        emptied = KERNEL.end_job(job)
    ended = emptied and KERNEL.api.WaitForSingleObject(handle, int(SETTLE * 1000)) == native.WAIT_OBJECT_0
    KERNEL.api.CloseHandle(handle)
    return {"caller_dead": helper.poll() is not None, "child_alive": alive,
            "inherited_handle_is_guard": guard is not None and os.path.normcase(guard) == os.path.normcase(os.path.realpath(executable)),
            "during_child": during, "child_ended": ended, "after_child": _rename(executable, moved),
            "control_without_guard": _control_without_guard(executable, scratch)}


def check_abandoned_mutex(bound: float, scratch: Path) -> dict[str, object]:
    """The transition mutex abandoned by a thread of a live holder authorizes nothing: the waiter fails, the record stays."""
    layout = CacheLayout(scratch / "tooling")
    ready = scratch / "mutex.json"
    helper = _helper("service-mutex", layout.tooling_root, ready)
    try:
        _await(ready.exists, bound / 2, "the holder's abandoned mutex")
        name = json.loads(ready.read_text(encoding="utf-8"))["name"]
        before = layout.lock_path(PIN).read_bytes()
        abandoned = KERNEL.abandoned(name)
        waiter = CacheLock(layout, PIN, caller="native-check", seams=LockSeams(clock=time.monotonic, sleep=time.sleep))
        try:
            waiter.acquire(_WAITER_SECONDS, lambda _holder, _wait: None)
            error, owner = "none", None
        except LockWaitError as failure:
            error, owner = type(failure).__name__, failure.owner
        holder = LockRecord.decode(before).owner
        alive = helper.poll() is None
        kept = layout.lock_path(PIN).read_bytes() == before
    finally:
        _kill(helper)
    return {"mutex_abandoned": abandoned, "holder_alive": alive, "waiter_error": error, "holder_named": owner == holder, "record_kept": kept}


def _publishing(published: Path, role: str) -> Callable[[ChildRequest], ChildOutcome]:
    """Run children contained, publishing this helper's PID, the child's job handle and identity for one role before resume."""
    def launch(request: ChildRequest) -> ChildOutcome:
        if ("probe" if request.arguments == ("--version",) else "run") != role:
            return run_contained(request)
        observed = Observed()

        def record(identity: ProcessIdentity) -> None:
            facts = {"helper": os.getpid(), "job": observed.job, "pid": identity.pid, "created": identity.created,
                     "guard": request.inherited[0] if request.inherited else 0}
            temporary = published.with_suffix(".partial")
            temporary.write_text(json.dumps(facts), encoding="utf-8")
            temporary.replace(published)

        return run_contained(dataclasses.replace(request, record=record), api=observed)
    return launch


def _rooted_worker(request: ChildRequest) -> ChildOutcome:
    """Start the download worker through this checkout's bootstrap, since the temporary root holds no checkout."""
    if "git-cliff-worker" in request.arguments:
        arguments = list(request.arguments)
        arguments[3] = str(ROOT / "tools" / "release_workflow" / "bootstrap.py")
        request = dataclasses.replace(request, arguments=tuple(arguments))
    return run_contained(request)


def _abandon(name: str) -> None:
    """Take the transition mutex on this thread and end without releasing it."""
    handle = KERNEL.api.CreateMutexW(None, 0, name)
    KERNEL.api.WaitForSingleObject(handle, _INFINITE)


def run_helper(name: str, arguments: Sequence[str]) -> int:
    """Run one helper caller of the service until it is killed."""
    paths = [Path(argument) for argument in arguments]
    seams = production_seams(Path(sys.executable))
    if name == "service-worker":
        provision(paths[0], PIN, resolve_budget({}), seams=dataclasses.replace(seams, launch=_rooted_worker), caller="native-check")
    elif name == "service-mutex":
        lock = CacheLock(CacheLayout(paths[0]), PIN, caller="native-check", seams=LockSeams(clock=time.monotonic, sleep=time.sleep))
        lock.acquire(5, lambda _holder, _wait: None)
        thread = threading.Thread(target=_abandon, args=(lock._name,))  # noqa: SLF001 - the mutex name the lock derived
        thread.start()
        thread.join()
        paths[1].write_text(json.dumps({"name": lock._name}), encoding="utf-8")  # noqa: SLF001 - the mutex name the lock derived
        time.sleep(120)
    else:
        role = "probe" if name == "service-probe" else "run"
        invocation = provision(paths[0], PIN, resolve_budget({}), seams=dataclasses.replace(seams, launch=_publishing(paths[1], role)),
                               caller="native-check")
        invocation.run(["--native-check-run"], policy=Policy.ENGINE, cwd=paths[0], environment=os.environ | {_MARK: str(paths[2])})
    return 0


# eof
