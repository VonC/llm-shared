"""A fake kernel32 for the Windows child layer: it records calls, plays a declared child and fails on demand.

Step 2 of v0.14.0 git-cliff-provisioning (plan decision Q05, shared test
architecture). `FakeKernel` stands where `windows_native.kernel()` would return
the declared kernel32 library: production code receives it through its explicit
`api` argument, so no test reaches the operating system. Every call is logged
with its arguments, in order; `fail(name, occurrence=n)` makes the n-th call of
one function raise `NativeCallError`, as the declared error check would, and
`interrupt(name, occurrence=n)` delivers a Ctrl+C after it ran: it calls the
Python SIGINT handler then installed, as CPython does once a native call
returns, so the default handler raises `KeyboardInterrupt` and a run's
deferring handler records it (code review rounds 1 and 2).

The next created child plays `FakeKernel.child`: its exit status and output
bytes, whether it is still running at its deadline, and whether a descendant
keeps the stdout write end until the job is terminated. A pipe read blocks on a
condition until data arrives or every write-end holder (the parent's copy, the
root, a descendant) has ended; `release()` ends every holder, so a test whose
readers were left blocked by an unconfirmed end lets them finish. A read still
blocked after a safety bound fails with the fake-only error `STALLED`, so a
wrong join order fails instead of hanging. The end of file of a pipe is logged
as a `pipe-end` entry, so a test can place it after `TerminateJobObject`.
"""

from __future__ import annotations

import ctypes
import signal
import threading
from collections import Counter
from ctypes import wintypes
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from tools.release_workflow import windows_native as native
from tools.release_workflow.windows_native import NativeCallError

if TYPE_CHECKING:
    from collections.abc import Callable

type _Buffer = ctypes.Array[ctypes.c_char]

STDIN = 0x10
STDOUT = 0x14
STDERR = 0x14
STALLED = 0x5A11
_FIRST_HANDLE = 0x100
_HANDLE_STEP = 4
_STALL_SECONDS = 5.0
_STILL_ACTIVE = 259
_ATTRIBUTE_SIZE = 48
_HIGH_WORD_SHIFT = 32
_LOW_WORD = 0xFFFFFFFF
_CREATE_FILE = "CreateFileW"
_READ_FILE = "ReadFile"


def deliver_ctrl_c() -> None:
    """Call the Python SIGINT handler now installed, as the interpreter does when Ctrl+C arrives; no signal is sent."""
    handler = signal.getsignal(signal.SIGINT)
    if handler is None or isinstance(handler, int):
        raise KeyboardInterrupt
    handler(signal.SIGINT, None)


@dataclass
class FakeChild:
    """What the next created child does once resumed."""

    status: int = 0
    stdout: bytes = b""
    stderr: bytes = b""
    exits: bool = True
    descendant: bool = False
    pid: int = 4242
    created: int = 0x01DB_0000_1234_5678


@dataclass(frozen=True)
class Creation:
    """The arguments and handle state seen by the one `CreateProcessW` call."""

    application: str
    command_line: str
    inherit_handles: int
    flags: int
    environment: str | None
    cwd: str | None
    standard: tuple[int, int, int]
    attributes: tuple[tuple[int, tuple[int, ...]], ...]
    inheritable: dict[int, bool]


@dataclass
class _Pipe:
    """An anonymous pipe: queued bytes and the holders of its write end."""

    holders: set[str] = field(default_factory=lambda: {"parent"})
    data: bytearray = field(default_factory=bytearray)
    condition: threading.Condition = field(default_factory=threading.Condition)

    def write(self, data: bytes) -> None:
        """Queue bytes for the reader."""
        with self.condition:
            self.data.extend(data)
            self.condition.notify_all()

    def drop(self, *holders: str) -> None:
        """End some holders of the write end."""
        with self.condition:
            self.holders.difference_update(holders)
            self.condition.notify_all()


@dataclass
class _Process:
    """The root child, its job and the pipes it writes into."""

    child: FakeChild
    job: int
    pipes: dict[str, _Pipe]
    state: str = "suspended"
    status: int = _STILL_ACTIVE
    descendant: bool = False


@dataclass
class _File:
    """A file object: its bytes and the position its handles share."""

    data: bytes
    position: int = 0


class FakeKernel:
    """The declared kernel32 functions the Windows child layer calls, simulated in memory."""

    def __init__(self, child: FakeChild | None = None) -> None:
        """Start with no handle, the standard handles of a console and `child` as the next child."""
        self.child = child or FakeChild()
        self.calls: list[tuple[str, tuple[Any, ...]]] = []
        self.created: list[int] = []
        self.closed: list[int] = []
        self.inheritable: dict[int, bool] = {STDIN: True, STDOUT: True}
        self.limits: dict[int, int] = {}
        self.files: dict[str, bytes] = {}
        self.denied: set[str] = set()
        self.std = {native.STD_INPUT_HANDLE: STDIN, native.STD_OUTPUT_HANDLE: STDOUT, native.STD_ERROR_HANDLE: STDERR}
        self.lingering = 0
        self.creation: Creation | None = None
        self.readers: list[tuple[int, threading.Thread, object]] = []
        self.handlers: list[tuple[object, int]] = []
        self.lists: dict[int, list[tuple[int, tuple[int, ...]]]] = {}
        self._failures: dict[tuple[str, int], int] = {}
        self._interrupts: set[tuple[str, int]] = set()
        self._counts: Counter[str] = Counter()
        self._lock = threading.Lock()
        self._next = _FIRST_HANDLE
        self._pipes: dict[int, _Pipe] = {}
        self._writes: dict[int, _Pipe] = {}
        self._files: dict[int, _File] = {}
        self._processes: dict[int, _Process] = {}
        self._threads: dict[int, _Process] = {}

    def __getattr__(self, name: str) -> Callable[..., Any]:
        """Return the logged, failure-aware simulation of one declared kernel32 function."""
        implementation = _IMPLEMENTATIONS.get(name)
        if implementation is None:
            raise AttributeError(name)

        def call(*args: Any) -> object:
            with self._lock:
                self.calls.append((name, args))
                self._counts[name] += 1
                error = self._failures.get((name, self._counts[name]))
                interrupted = (name, self._counts[name]) in self._interrupts
            if error is not None:
                raise NativeCallError(name, error)
            result = implementation(self, *args)
            if interrupted:
                deliver_ctrl_c()
            return result

        return call

    def fail(self, name: str, *, occurrence: int = 1, error: int = native.ERROR_ACCESS_DENIED) -> None:
        """Make the given call of `name` raise `NativeCallError` with `error`."""
        self._failures[name, occurrence] = error

    def interrupt(self, name: str, *, occurrence: int = 1) -> None:
        """Deliver a Ctrl+C once the given call of `name` ran, as CPython does after a native call returns."""
        self._interrupts.add((name, occurrence))

    def names(self) -> list[str]:
        """Return the logged call names, in order."""
        with self._lock:
            return [name for name, _ in self.calls]

    def index(self, name: str, occurrence: int = 1) -> int:
        """Return the log position of the given call of `name`."""
        positions = [position for position, called in enumerate(self.names()) if called == name]
        return positions[occurrence - 1]

    def arguments(self, name: str, occurrence: int = 1) -> tuple[Any, ...]:
        """Return the arguments of the given call of `name`."""
        return self.calls[self.index(name, occurrence)][1]

    def open_handles(self) -> set[int]:
        """Return the handles created and not closed."""
        return set(self.created) - set(self.closed)

    def release(self) -> None:
        """End every write-end holder, as process exit would, so blocked readers finish."""
        for pipe in self._pipes.values():
            pipe.drop("parent", "root", "descendant")

    def _new(self) -> int:
        """Allocate a handle value."""
        handle = self._next
        self._next += _HANDLE_STEP
        self.created.append(handle)
        return handle

    def _close_handle(self, handle: int) -> int:
        """Close a handle; the parent's write end of a pipe stops holding it."""
        self.closed.append(handle)
        pipe = self._writes.get(handle)
        if pipe is not None:
            pipe.drop("parent")
        return 1

    def _create_job(self, security: object, name: object) -> int:
        """Create a job; the arguments are checked through the call log."""
        del security, name
        return self._new()

    def _set_job_information(self, job: int, kind: int, information: native.JOBOBJECT_EXTENDED_LIMIT_INFORMATION, size: int) -> int:
        """Keep the limit flags a job was configured with."""
        del kind, size
        self.limits[job] = information.BasicLimitInformation.LimitFlags
        return 1

    def _query_job_information(self, job: int, kind: int, information: native.JOBOBJECT_BASIC_ACCOUNTING_INFORMATION,
                               *_arguments: object) -> int:
        """Report the live members of a job, with `lingering` extra readings after termination."""
        del kind
        live = sum(process.state != "exited" or process.descendant for process in self._processes.values() if process.job == job)
        if not live and self.lingering:
            self.lingering -= 1
            live = 1
        information.ActiveProcesses = live
        return 1

    def _terminate_job(self, job: int, status: int) -> int:
        """End every remaining member of a job and its hold on the pipes."""
        for process in self._processes.values():
            if process.job != job:
                continue
            if process.state != "exited":
                process.state, process.status = "exited", status
            process.descendant = False
            for pipe in process.pipes.values():
                pipe.drop("root", "descendant")
        return 1

    def _create_pipe(self, read: wintypes.HANDLE, write: wintypes.HANDLE, *_arguments: object) -> int:
        """Create a pipe whose two ends are not inheritable."""
        pipe = _Pipe()
        read_end, write_end = self._new(), self._new()
        read.value, write.value = read_end, write_end
        self._pipes[read_end] = pipe
        self._writes[write_end] = pipe
        return 1

    def _create_file(self, path: str, *_arguments: object) -> int:
        """Open `NUL` or a declared file; a denied path is a sharing violation."""
        if path == "NUL":
            return self._new()
        if path in self.denied:
            raise NativeCallError(_CREATE_FILE, native.ERROR_SHARING_VIOLATION)
        data = self.files.get(path)
        if data is None:
            raise NativeCallError(_CREATE_FILE, native.ERROR_FILE_NOT_FOUND)
        handle = self._new()
        self._files[handle] = _File(data)
        return handle

    def _get_std_handle(self, which: int) -> int:
        """Return the console's standard handle."""
        return self.std[which]

    def _get_handle_information(self, handle: int, flags: wintypes.DWORD) -> int:
        """Report whether a handle is inheritable."""
        flags.value = int(self.inheritable.get(handle, False))
        return 1

    def _set_handle_information(self, handle: int, mask: int, flags: int) -> int:
        """Change the inheritance of a handle."""
        self.inheritable[handle] = bool(flags & mask)
        return 1

    def _initialize_list(self, attributes: _Buffer | None, count: int, flags: int, size: ctypes.c_size_t) -> int:
        """Size a list (insufficient buffer, as Windows answers), then initialize it."""
        del flags
        if attributes is None:
            size.value = _ATTRIBUTE_SIZE * count
            return 0
        self.lists[ctypes.addressof(attributes)] = []
        return 1

    def _update_list(self, attributes: _Buffer, flags: int, attribute: int, value: ctypes.Array[ctypes.c_void_p],
                     *_arguments: object) -> int:
        """Record the handles of one attribute."""
        del flags
        self.lists[ctypes.addressof(attributes)].append((attribute, tuple(value)))
        return 1

    def _delete_list(self, attributes: _Buffer) -> None:
        """Delete a list; the call log shows it."""

    def _create_process(self, application: str, command_line: ctypes.Array[ctypes.c_wchar], *arguments: Any) -> int:
        """Create the declared child suspended, in the job its attribute list names."""
        inherit, flags, environment, cwd, startup, information = arguments[2:]
        listed = dict(self.lists.get(startup.lpAttributeList or 0, []))
        standard = (startup.StartupInfo.hStdInput, startup.StartupInfo.hStdOutput, startup.StartupInfo.hStdError)
        self.creation = Creation(
            application, command_line.value, inherit, flags, None if environment is None else environment[:], cwd, standard,
            tuple(self.lists.get(startup.lpAttributeList or 0, [])),
            {handle: self.inheritable.get(handle, False) for handle in listed.get(native.PROC_THREAD_ATTRIBUTE_HANDLE_LIST, ())},
        )
        pipes = {name: self._writes[handle] for name, handle in zip(("stdout", "stderr"), standard[1:], strict=True) if handle in self._writes}
        process = _Process(self.child, listed[native.PROC_THREAD_ATTRIBUTE_JOB_LIST][0], pipes)
        for pipe in pipes.values():
            pipe.holders.add("root")
        information.hProcess, information.hThread = self._new(), self._new()
        information.dwProcessId, information.dwThreadId = self.child.pid, self.child.pid + 1
        self._processes[information.hProcess] = process
        self._threads[information.hThread] = process
        return 1

    def _get_process_times(self, handle: int, created: wintypes.FILETIME, *_times: object) -> int:
        """Report the declared creation time."""
        value = self._processes[handle].child.created
        created.dwHighDateTime, created.dwLowDateTime = value >> _HIGH_WORD_SHIFT, value & _LOW_WORD
        return 1

    def _resume_thread(self, thread: int) -> int:
        """Run the child: it writes its output, then exits unless it never finishes."""
        process = self._threads[thread]
        process.state = "running"
        process.descendant = process.child.descendant
        if process.descendant and "stdout" in process.pipes:
            process.pipes["stdout"].holders.add("descendant")
        for name, data in (("stdout", process.child.stdout), ("stderr", process.child.stderr)):
            if name in process.pipes:
                process.pipes[name].write(data)
        if process.child.exits:
            process.state, process.status = "exited", process.child.status
            for pipe in process.pipes.values():
                pipe.drop("root")
        return 1

    def _wait(self, handle: int, milliseconds: int) -> int:
        """Signal an exited child; an unbounded wait on a running one is a test defect."""
        process = self._processes[handle]
        if process.state == "exited":
            return native.WAIT_OBJECT_0
        if milliseconds == native.INFINITE:
            msg = "an unbounded wait on a child that never ends"
            raise AssertionError(msg)
        return native.WAIT_TIMEOUT

    def _exit_code(self, handle: int, status: wintypes.DWORD) -> int:
        """Report the child's status."""
        status.value = self._processes[handle].status
        return 1

    def _read(self, handle: int, buffer: _Buffer, size: int, count: wintypes.DWORD, *_arguments: object) -> int:
        """Read a file at its shared position, or a pipe once data or its end arrives."""
        file = self._files.get(handle)
        if file is not None:
            chunk = file.data[file.position:file.position + size]
            file.position += len(chunk)
            return self._deliver(buffer, count, chunk)
        pipe = self._pipes[handle]
        self.readers.append((handle, threading.current_thread(), buffer))
        with pipe.condition:
            if not pipe.condition.wait_for(lambda: pipe.data or not pipe.holders, timeout=_STALL_SECONDS):
                raise NativeCallError(_READ_FILE, STALLED)
            if not pipe.data:
                with self._lock:
                    self.calls.append(("pipe-end", (handle,)))
                raise NativeCallError(_READ_FILE, native.ERROR_BROKEN_PIPE)
            chunk = bytes(pipe.data[:size])
            del pipe.data[:size]
        return self._deliver(buffer, count, chunk)

    @staticmethod
    def _deliver(buffer: _Buffer, count: wintypes.DWORD, chunk: bytes) -> int:
        """Copy a chunk into the caller's buffer."""
        ctypes.memmove(buffer, chunk, len(chunk))
        count.value = len(chunk)
        return 1

    def _duplicate(self, source_process: int, source: int, target_process: int, target: wintypes.HANDLE, *_arguments: object) -> int:
        """Duplicate a file handle: the new handle shares the file object and its position."""
        del source_process, target_process
        duplicate = self._new()
        target.value = duplicate
        self._files[duplicate] = self._files[source]
        return 1

    def _seek(self, handle: int, distance: int, *_arguments: object) -> int:
        """Move the shared position of a file object."""
        self._files[handle].position = distance
        return 1

    def _in_job(self, handle: int, job: object, result: wintypes.BOOL) -> int:
        """Report membership of the declared child in its job."""
        result.value = int(self._processes[handle].job == job)
        return 1

    def _console_handler(self, handler: object, add: int) -> int:
        """Record a handler registration or removal."""
        self.handlers.append((handler, add))
        return 1


_IMPLEMENTATIONS: dict[str, Callable[..., Any]] = {
    "CloseHandle": FakeKernel._close_handle,
    "CreateFileW": FakeKernel._create_file,
    "CreateJobObjectW": FakeKernel._create_job,
    "CreatePipe": FakeKernel._create_pipe,
    "CreateProcessW": FakeKernel._create_process,
    "DeleteProcThreadAttributeList": FakeKernel._delete_list,
    "DuplicateHandle": FakeKernel._duplicate,
    "GetExitCodeProcess": FakeKernel._exit_code,
    "GetHandleInformation": FakeKernel._get_handle_information,
    "GetProcessTimes": FakeKernel._get_process_times,
    "GetStdHandle": FakeKernel._get_std_handle,
    "InitializeProcThreadAttributeList": FakeKernel._initialize_list,
    "IsProcessInJob": FakeKernel._in_job,
    "QueryInformationJobObject": FakeKernel._query_job_information,
    "ReadFile": FakeKernel._read,
    "ResumeThread": FakeKernel._resume_thread,
    "SetConsoleCtrlHandler": FakeKernel._console_handler,
    "SetFilePointerEx": FakeKernel._seek,
    "SetHandleInformation": FakeKernel._set_handle_information,
    "SetInformationJobObject": FakeKernel._set_job_information,
    "TerminateJobObject": FakeKernel._terminate_job,
    "UpdateProcThreadAttribute": FakeKernel._update_list,
    "WaitForSingleObject": FakeKernel._wait,
}


# eof
