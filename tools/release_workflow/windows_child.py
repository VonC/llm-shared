"""Run one Windows child contained from its creation, then end it job-wide before reading its output.

Step 2 of v0.14.0 git-cliff-provisioning (design "Child process lifecycle" and
"Deadline enforcement"; design decisions Q07, Q10 and Q17; plan decisions Q04,
Q05, Q06 and Q14). `run_contained` follows seven phases on every path:

1. Setup: a kill-on-close job with a non-inheritable handle, the capture pipes
   (read ends never inheritable), `NUL` for a closed stdin and an attribute
   list holding exactly the job list and the handle list.
2. Creation: the listed handles are inheritable only around `CreateProcessW`,
   which creates the child suspended and already in the job; then inheritance
   is reset, the list deleted and the parent's write ends and `NUL` closed. No
   create-then-assign path, no `subprocess` fallback.
3. Pre-resume: the identity is read and handed to the recording callback, then
   the thread is resumed.
4. Wait: daemon readers drain the native pipe handles into private buffers
   while the parent waits on the root within the deadline.
5. Teardown: `TerminateJobObject` (once), the root reaped, `ActiveProcesses`
   polled to 0; no budget of its own once the termination has succeeded.
6. Drain: only then are the readers joined and the handles closed, so a
   returned outcome means every member of the job has ended.
7. Unconfirmed end: a failure in phase 5 moves the job, process, thread and
   pipe handles to `RETAINED`, which never closes them, and raises
   `UnconfirmedEndError`; nothing is joined. The parent's exit closes the job
   handle, so kill-on-close ends the members.

Any failure before phase 5 settles the attempt: a created child is ended and
confirmed, every resource released, then `ContainmentError` is raised (an
interrupt propagates as is). Since code review rounds 1 and 2: bookkeeping is
linear and written before each native call; a failed reset or close keeps its
handle, the others are still released and the rest retried; what remains goes
to `RETAINED` on every exit path, named by `ContainmentError.cleanup` or a note.
On the main thread, with Python's default handler, a Ctrl+C is recorded and
raised only at safe points or once the run is settled; a `KeyboardInterrupt`
raised while ending or releasing is held back the same way. An unconfirmed end
always reaches the caller. `ignore_console_interrupts`, the launcher's console
filter, is a handler routine children do not inherit, unlike the null routine.
"""

from __future__ import annotations

import ctypes
import math
import platform
import signal
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from ctypes import wintypes
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Protocol

from tools.release_workflow import windows_native as native
from tools.release_workflow.windows_native import NativeCallError
from tools.release_workflow.windows_process import ProcessIdentity

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping, Sequence
    from pathlib import Path
    from types import FrameType

    from tools.release_workflow.windows_native import Kernel

_POLL_SECONDS = 0.01
_TERMINATED_STATUS = 1
_READ_SIZE = 65536
_ATTRIBUTE_COUNT = 2
_MILLISECONDS = 1000
_SUPPORTED_MAJOR = 10
_X64_MACHINES = frozenset({"AMD64", "X86_64"})
_HIGH_WORD_SHIFT = 32
_STREAM_MODES = {"stdin": ("closed", "inherit"), "output": ("capture", "inherit")}


class PlatformError(OSError):
    """This Windows release or architecture is below the provisioning baseline."""

    stage = "platform"


class ContainmentError(OSError):
    """No child of the attempt runs; `cleanup` names failed reset or close calls whose handles `RETAINED` now owns."""

    stage = "containment"

    def __init__(self, message: str, *, call: str, error: int | None, cleanup: tuple[str, ...] = ()) -> None:
        """Keep the failing native call or step, its Windows error when it has one, and any failed cleanup call."""
        super().__init__(message)
        self.call = call
        self.error = error
        self.cleanup = cleanup


class UnconfirmedEndError(ContainmentError):
    """The end of a created child could not be confirmed; its resources are retained, nothing is cleaned up."""

    stage = "unconfirmed-end"

    def __init__(self, *, pid: int, identity: ProcessIdentity | None, call: str, error: int | None) -> None:
        """Name the child, by PID when its identity was never read, and the failing call."""
        super().__init__(f"the end of contained child {pid} is unconfirmed: {call} failed", call=call, error=error)
        self.pid = pid
        self.identity = identity


@dataclass(frozen=True)
class RetainedChild:
    """The native resources of a child whose end is unconfirmed, owned until the process ends."""

    pid: int
    identity: ProcessIdentity | None
    call: str
    handles: tuple[int, ...]
    readers: tuple[object, ...] = field(default=(), compare=False)


class _Retained:
    """The process-lifetime owner of unresolved native resources: it only appends, it never closes."""

    def __init__(self) -> None:
        """Hold nothing yet."""
        self._entries: list[object] = []

    def keep(self, entry: object) -> None:
        """Own a resource until the operating system closes it with the process."""
        self._entries.append(entry)

    def entries(self) -> tuple[object, ...]:
        """Return what is owned, oldest first."""
        return tuple(self._entries)


RETAINED = _Retained()


class _WindowsVersion(Protocol):
    """The part of `sys.getwindowsversion()` the platform check reads."""

    @property
    def platform_version(self) -> tuple[int, int, int]:
        """Return the kernel's major, minor and build numbers."""
        ...


def require_supported_platform(version: _WindowsVersion | None = None, machine: str | None = None) -> None:
    """Refuse a Windows release below Windows 10 or Windows Server 2016, or a machine other than x64."""
    found = sys.getwindowsversion() if version is None else version
    architecture = platform.machine() if machine is None else machine
    major, minor, build = found.platform_version
    if major < _SUPPORTED_MAJOR or architecture.upper() not in _X64_MACHINES:
        msg = (f"git-cliff provisioning needs Windows 10 or Windows Server 2016 or later on x64; "
               f"this machine runs Windows {major}.{minor}.{build} on {architecture}")
        raise PlatformError(msg)


@dataclass(frozen=True)
class ChildRequest:
    """One child to start: what it runs, where, with which streams, inherited guards, deadline and recorder."""

    executable: Path
    arguments: tuple[str, ...] = ()
    cwd: Path | None = None
    environment: Mapping[str, str] | None = None
    stdin: Literal["closed", "inherit"] = "closed"
    output: Literal["capture", "inherit"] = "capture"
    inherited: tuple[int, ...] = ()
    deadline: float | None = None
    record: Callable[[ProcessIdentity], None] | None = None

    def __post_init__(self) -> None:
        """Refuse stream modes and environment entries Windows cannot carry, before any native call."""
        for name, modes in _STREAM_MODES.items():
            if getattr(self, name) not in modes:
                msg = f"invalid {name} mode {getattr(self, name)!r}"
                raise ValueError(msg)
        for key, value in (self.environment or {}).items():
            if not key or "=" in key[1:] or "\0" in key or "\0" in value:
                msg = f"invalid environment variable {key!r}"
                raise ValueError(msg)

    def command_line(self) -> str:
        """Quote the executable and arguments as the C runtime parses them."""
        return subprocess.list2cmdline([str(self.executable), *self.arguments])

    def environment_block(self) -> str | None:
        """Return the double-NUL terminated block, sorted case-insensitively as Windows requires, or inherit."""
        if self.environment is None:
            return None
        entries = sorted(self.environment.items(), key=lambda entry: entry[0].upper())
        return ("".join(f"{key}={value}\0" for key, value in entries) or "\0") + "\0"


@dataclass(frozen=True)
class ChildOutcome:
    """A child that has ended with every member of its job: its status and captured bytes."""

    status: int
    stdout: bytes
    stderr: bytes
    timed_out: bool
    identity: ProcessIdentity


class _Reader:
    """A daemon thread draining one native pipe read handle into a private buffer."""

    def __init__(self, api: Kernel, handle: int, name: str) -> None:
        """Prepare the thread; it starts when the child runs."""
        self._api = api
        self._handle = handle
        self._chunks: list[bytes] = []
        self.error: NativeCallError | None = None
        self.thread = threading.Thread(target=self._drain, name=name, daemon=True)

    def _drain(self) -> None:
        """Read until every holder of the write end has ended."""
        buffer = ctypes.create_string_buffer(_READ_SIZE)
        count = wintypes.DWORD()
        while True:
            try:
                self._api.ReadFile(self._handle, buffer, _READ_SIZE, count, None)
            except NativeCallError as error:
                if error.winerror != native.ERROR_BROKEN_PIPE:
                    self.error = error
                return
            self._chunks.append(ctypes.string_at(buffer, count.value))

    def data(self) -> bytes:
        """Return every byte read."""
        return b"".join(self._chunks)


def _milliseconds(deadline: float | None) -> int:
    """Convert a deadline in seconds to a wait bound, rounded up; `None` waits without bound."""
    if deadline is None:
        return native.INFINITE
    return min(native.INFINITE - 1, max(0, math.ceil(deadline * _MILLISECONDS)))


def _value(handle: wintypes.HANDLE) -> int:
    """Return the integer value of a handle a call has filled."""
    return handle.value or 0


class _Run:
    """The handles and phases of one contained child."""

    def __init__(self, api: Kernel, request: ChildRequest, sleep: Callable[[float], None]) -> None:
        """Hold no handle yet; the request was validated when it was built."""
        self._api = api
        self._request = request
        self._sleep = sleep
        self._environment = request.environment_block()
        self._job = 0
        self._owned: dict[int, None] = {}
        self._parent_ends: dict[int, None] = {}
        self._restore: dict[int, None] = {}
        self._adopted = False
        self._cleanup: tuple[str, ...] = ()
        self._reads: dict[str, int] = {}
        self._standard: tuple[int, int, int] = (0, 0, 0)
        self._attributes: ctypes.Array[ctypes.c_char] | None = None
        self._values: list[object] = []
        self._startup = native.STARTUPINFOEXW()
        self._info = native.PROCESS_INFORMATION()
        self._identity: ProcessIdentity | None = None
        self._readers: list[_Reader] = []
        self._step = "setup"
        self._terminated = False
        self._status = 0
        self._status_failure: NativeCallError | None = None
        self._failures: list[NativeCallError] = []
        self._interrupt: KeyboardInterrupt | None = None

    def execute(self) -> ChildOutcome:
        """Run the phases; a deferred interrupt then follows the outcome or replaces the error, an unconfirmed end excepted."""
        try:
            outcome = self._phases()
        except UnconfirmedEndError:
            raise
        except BaseException as error:
            if self._interrupt is None or isinstance(error, KeyboardInterrupt):
                raise
            raise self._interrupt from error
        if self._interrupt is not None:
            raise self._interrupt
        return outcome

    def defer_interrupt(self, signum: int, frame: FrameType | None) -> None:
        """SIGINT handler during the run: keep the Ctrl+C for the next safe point instead of raising it now."""
        del signum, frame
        self._interrupt = self._interrupt or KeyboardInterrupt()

    def _interrupt_point(self) -> None:
        """Raise a deferred Ctrl+C where every handle is accounted for."""
        if self._interrupt is not None:
            raise self._interrupt

    def _phases(self) -> ChildOutcome:
        """Phases 1 to 6; any failure, an interrupt included, settles the attempt before it propagates."""
        try:
            self._setup()
            self._interrupt_point()
            self._create()
            self._release_creation_inputs()
            self._raise_failed_release()
            identity = self._pre_resume()
            timed_out = self._wait()
            self._interrupt_point()
        except BaseException as error:
            self._settle()
            if isinstance(error, Exception):
                raise self._containment(error) from error
            if self._cleanup:
                error.add_note(f"contained child: {', '.join(self._cleanup)} failed; handles left to the process lifetime")
            raise
        self._shielded(self._teardown)
        status = self._drain()
        outputs = [reader.data() for reader in self._readers] or [b"", b""]
        return ChildOutcome(status, outputs[0], outputs[1], timed_out=timed_out, identity=identity)

    def _setup(self) -> None:
        """Phase 1: the kill-on-close job, the standard handles and the attribute list."""
        api = self._api
        self._job = api.CreateJobObjectW(None, None)
        self._owned[self._job] = None
        limits = native.JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = native.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        api.SetInformationJobObject(self._job, native.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, limits, ctypes.sizeof(limits))
        self._standard = (self._stdin(), *self._outputs())
        startup = self._startup.StartupInfo
        startup.cb = ctypes.sizeof(self._startup)
        startup.dwFlags = native.STARTF_USESTDHANDLES
        startup.hStdInput, startup.hStdOutput, startup.hStdError = self._standard
        size = ctypes.c_size_t()
        api.InitializeProcThreadAttributeList(None, _ATTRIBUTE_COUNT, 0, size)
        attributes = ctypes.create_string_buffer(size.value)
        api.InitializeProcThreadAttributeList(attributes, _ATTRIBUTE_COUNT, 0, size)
        self._attributes = attributes
        self._update(native.PROC_THREAD_ATTRIBUTE_JOB_LIST, (self._job,))
        self._update(native.PROC_THREAD_ATTRIBUTE_HANDLE_LIST, self._listed())
        self._startup.lpAttributeList = ctypes.addressof(attributes)

    def _stdin(self) -> int:
        """Return the parent's standard input, or a `NUL` handle the parent closes after creation."""
        if self._request.stdin == "inherit":
            return self._api.GetStdHandle(native.STD_INPUT_HANDLE)
        handle = self._api.CreateFileW("NUL", native.GENERIC_READ, native.FILE_SHARE_READ | native.FILE_SHARE_WRITE, None,
                                       native.OPEN_EXISTING, 0, None)
        self._parent_ends[handle] = None
        return handle

    def _outputs(self) -> tuple[int, int]:
        """Return the parent's standard output and error, or the write ends of two capture pipes."""
        if self._request.output == "inherit":
            return self._api.GetStdHandle(native.STD_OUTPUT_HANDLE), self._api.GetStdHandle(native.STD_ERROR_HANDLE)
        return self._pipe("stdout"), self._pipe("stderr")

    def _pipe(self, name: str) -> int:
        """Create a pipe whose read end stays with the parent; return its write end."""
        read, write = wintypes.HANDLE(), wintypes.HANDLE()
        self._api.CreatePipe(read, write, None, 0)
        self._reads[name] = _value(read)
        self._owned[_value(read)] = None
        self._parent_ends[_value(write)] = None
        return _value(write)

    def _listed(self) -> tuple[int, ...]:
        """The only handles the child inherits: the standard handles, once each, then the guards."""
        return tuple(dict.fromkeys((*self._standard, *self._request.inherited)))

    def _update(self, attribute: int, handles: Sequence[int]) -> None:
        """Add one attribute; its value must live until the list is deleted."""
        value = (wintypes.HANDLE * len(handles))(*handles)
        self._values.append(value)
        self._api.UpdateProcThreadAttribute(self._attributes, 0, attribute, value, ctypes.sizeof(value), None, None)

    def _create(self) -> None:
        """Phase 2: make the listed handles inheritable, then create the child suspended inside its job."""
        api = self._api
        for handle in self._listed():
            flags = wintypes.DWORD()
            api.GetHandleInformation(handle, flags)
            if not flags.value & native.HANDLE_FLAG_INHERIT:
                self._restore[handle] = None
                api.SetHandleInformation(handle, native.HANDLE_FLAG_INHERIT, native.HANDLE_FLAG_INHERIT)
        request = self._request
        environment = None if self._environment is None else ctypes.create_unicode_buffer(self._environment, len(self._environment))
        api.CreateProcessW(str(request.executable), ctypes.create_unicode_buffer(request.command_line()), None, None, 1,
                           native.CREATE_SUSPENDED | native.EXTENDED_STARTUPINFO_PRESENT | native.CREATE_UNICODE_ENVIRONMENT,
                           environment, None if request.cwd is None else str(request.cwd), self._startup, self._info)
        self._adopt_child()

    def _adopt_child(self) -> None:
        """Own the process and thread handles `CreateProcessW` filled in, once."""
        if self._info.hProcess and not self._adopted:
            self._adopted = True
            self._owned.update(dict.fromkeys((self._info.hProcess, self._info.hThread)))

    def _release_creation_inputs(self) -> None:
        """Reset inheritance, delete the list, close the parent's write ends and `NUL`; repeatable, linear.

        A failed reset or close keeps its handle and the failure; a failed reset of a handle then closed is dropped.
        """
        for handle in tuple(self._restore):
            try:
                self._api.SetHandleInformation(handle, native.HANDLE_FLAG_INHERIT, 0)
            except NativeCallError as error:
                self._failures.append(error)
            else:
                del self._restore[handle]
        attributes, self._attributes = self._attributes, None
        if attributes is not None:
            self._api.DeleteProcThreadAttributeList(attributes)
        ours = tuple(self._parent_ends)
        self._close(self._parent_ends)
        for handle in ours:
            if handle not in self._parent_ends:
                self._restore.pop(handle, None)

    def _raise_failed_release(self) -> None:
        """Fail a created run whose creation inputs were not all released; settling retries the release."""
        if self._failures:
            raise self._failures[0]

    def _pre_resume(self) -> ProcessIdentity:
        """Phase 3: read the identity, record it, then let the child run."""
        self._step = "GetProcessTimes"
        created, exited, kernel_time, user_time = (wintypes.FILETIME() for _ in range(4))
        self._api.GetProcessTimes(self._info.hProcess, created, exited, kernel_time, user_time)
        identity = ProcessIdentity(self._info.dwProcessId, (created.dwHighDateTime << _HIGH_WORD_SHIFT) | created.dwLowDateTime)
        self._identity = identity
        if self._request.record is not None:
            self._step = "record"
            self._request.record(identity)
        self._interrupt_point()
        self._api.ResumeThread(self._info.hThread)
        return identity

    def _wait(self) -> bool:
        """Phase 4: start the readers and wait on the root within the deadline; return whether it expired."""
        self._step = "reader"
        for name, handle in self._reads.items():
            reader = _Reader(self._api, handle, f"contained-{self._info.dwProcessId}-{name}")
            reader.thread.start()
            self._readers.append(reader)
        result = self._api.WaitForSingleObject(self._info.hProcess, _milliseconds(self._request.deadline))
        return result == native.WAIT_TIMEOUT

    def _teardown(self) -> None:
        """Phase 5: end every member once (rerun after an interrupt), reap the root, wait for an empty job; else phase 7."""
        api = self._api
        accounting = native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
        try:
            if not self._terminated:
                api.TerminateJobObject(self._job, _TERMINATED_STATUS)
                self._terminated = True
            api.WaitForSingleObject(self._info.hProcess, native.INFINITE)
            while True:
                api.QueryInformationJobObject(self._job, native.JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION, accounting,
                                              ctypes.sizeof(accounting), None)
                if not accounting.ActiveProcesses:
                    return
                self._sleep(_POLL_SECONDS)
        except Exception as error:
            raise self._unconfirmed(error) from error

    def _unconfirmed(self, error: Exception) -> UnconfirmedEndError:
        """Phase 7: hand the job, process, thread and pipe handles to `RETAINED` and describe the unconfirmed end."""
        call, code = (error.call, error.winerror) if isinstance(error, NativeCallError) else ("teardown", None)
        handles = (self._job, self._info.hProcess, self._info.hThread, *self._reads.values())
        RETAINED.keep(RetainedChild(self._info.dwProcessId, self._identity, call, handles, tuple(self._readers)))
        return UnconfirmedEndError(pid=self._info.dwProcessId, identity=self._identity, call=call, error=code)

    def _drain(self) -> int:
        """Phase 6: after the confirmed end, read the root's status, then join the readers and release every handle."""
        self._shielded(self._read_status)
        self._shielded(self._release)
        self._retain_unreleased()
        reader = next((reader.error for reader in self._readers if reader.error is not None), None)
        failure = self._status_failure or reader or (self._failures[0] if self._failures else None)
        if failure is not None:
            raise self._containment(failure) from failure
        return self._status

    def _read_status(self) -> None:
        """Read the root's exit status, keeping a failure for the drain to report after the release."""
        status = wintypes.DWORD()
        try:
            self._api.GetExitCodeProcess(self._info.hProcess, status)
        except NativeCallError as error:
            self._status_failure = error
        else:
            self._status = status.value

    def _settle(self) -> None:
        """After a failure, end a created child and confirm it, then release every resource; phase 7 when unconfirmed."""
        if self._info.hProcess:
            self._shielded(self._teardown)
        self._shielded(self._release)
        self._retain_unreleased()

    def _release(self) -> None:
        """Join the readers, release the creation inputs and close every owned handle; repeatable."""
        self._adopt_child()
        for reader in self._readers:
            reader.thread.join()
        self._release_creation_inputs()
        self._close(self._owned)

    def _retain_unreleased(self) -> None:
        """Hand every handle a release could not settle to `RETAINED`, whatever error then propagates."""
        unreleased = (*self._restore, *self._parent_ends, *self._owned)
        if unreleased:
            self._cleanup = tuple(dict.fromkeys(failure.call for failure in self._failures)) or ("release",)
            RETAINED.keep(RetainedChild(self._info.dwProcessId, self._identity, self._cleanup[0], unreleased))

    def _shielded(self, action: Callable[[], None]) -> None:
        """Run a settling action to its end, again after each interrupt, which `execute` delivers afterwards."""
        while True:
            try:
                action()
            except KeyboardInterrupt as interrupt:
                self._interrupt = self._interrupt or interrupt
            else:
                return

    def _close(self, handles: dict[int, None]) -> None:
        """Close handles, most recent first; each leaves the set before its close and returns to it if the close fails."""
        for handle in reversed(tuple(handles)):
            del handles[handle]
            try:
                self._api.CloseHandle(handle)
            except NativeCallError as error:
                handles[handle] = None
                self._failures.append(error)

    def _containment(self, error: Exception) -> ContainmentError:
        """Describe a failure that left no running child, with the failed cleanup calls whose handles were retained."""
        if isinstance(error, NativeCallError):
            call, code, detail = error.call, error.winerror, str(error)
        else:
            call, code, detail = self._step, None, f"{self._step} failed: {error}"
        if self._cleanup:
            detail += f"; handles left to the process lifetime after {', '.join(self._cleanup)} failed"
        return ContainmentError(f"cannot contain {self._request.executable.name}: {detail}", call=call, error=code,
                                cleanup=self._cleanup)


@contextmanager
def _sigint_deferred(run: _Run) -> Generator[None]:
    """On the main thread, with Python's default SIGINT handler, hold a Ctrl+C for the run's safe points."""
    if threading.current_thread() is not threading.main_thread() or signal.getsignal(signal.SIGINT) is not signal.default_int_handler:
        yield
        return
    signal.signal(signal.SIGINT, run.defer_interrupt)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, signal.default_int_handler)


def run_contained(request: ChildRequest, *, api: Kernel | None = None, sleep: Callable[[float], None] = time.sleep) -> ChildOutcome:
    """Run a child created suspended inside its own kill-on-close job and return once every member has ended."""
    run = _Run(native.kernel() if api is None else api, request, sleep)
    with _sigint_deferred(run):
        return run.execute()


def is_process_in_job(process: int, job: int | None = None, *, api: Kernel | None = None) -> bool:
    """Tell whether a process belongs to a job, or to any job when `job` is `None`; used by the native checks."""
    result = wintypes.BOOL()
    (native.kernel() if api is None else api).IsProcessInJob(process, job, result)
    return bool(result.value)


def _ignore_interrupt(event: int) -> bool:
    """Handle Ctrl+C and Ctrl+Break, so the console's default handler does not end the launcher."""
    return event in {native.CTRL_C_EVENT, native.CTRL_BREAK_EVENT}


@contextmanager
def ignore_console_interrupts(*, api: Kernel | None = None) -> Generator[None]:
    """Ignore console interrupts while the launcher waits for git-cliff, which still receives them."""
    kernel = native.kernel() if api is None else api
    handler = native.PHANDLER_ROUTINE(_ignore_interrupt)
    kernel.SetConsoleCtrlHandler(handler, 1)
    try:
        yield
    finally:
        kernel.SetConsoleCtrlHandler(handler, 0)


# eof
