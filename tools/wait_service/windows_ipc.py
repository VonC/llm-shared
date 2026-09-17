"""Windows-only resource adapter with a directly injectable native-call seam.

The singleton is an OS-held, nonshared file handle. Named pipes reject remote
clients and verify both process token users before any application frame.
Overlapped operations have finite deadlines and drain cancellation before
freeing their buffers. Importing this module never loads Windows libraries.
"""

# ruff: noqa: EM101 - Typed WaitError codes are part of the public contract.

from __future__ import annotations

import ctypes
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast

from tools.wait_service.models import WaitError
from tools.wait_service.protocol import HEADER_SIZE, MAX_FRAME

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

DWORD = ctypes.c_uint32
HANDLE = ctypes.c_void_p
POINTER = ctypes.c_void_p
BOOL = ctypes.c_int
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
GENERIC_RW = 0xC0000000
FILE_FLAG_FIRST_PIPE_INSTANCE = 0x00080000
FILE_FLAG_OVERLAPPED = 0x40000000
PIPE_REJECT_REMOTE_CLIENTS = 0x00000008
ERROR_IO_PENDING = 997
ERROR_PIPE_CONNECTED = 535
WAIT_TIMEOUT = 258
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_ALREADY_EXISTS = 183
ERROR_SHARING_VIOLATION = 32
DRIVE_FIXED = 3
DACL_SECURITY_INFORMATION = 0x00000004
PROTECTED_DACL_SECURITY_INFORMATION = 0x80000000
CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000


class SecurityAttributes(ctypes.Structure):
    """Non-inheritable handle creation with an explicit security descriptor."""

    _fields_ = [("length", DWORD), ("descriptor", POINTER), ("inherit", BOOL)]


class Overlapped(ctypes.Structure):
    """Pointer-sized Win32 asynchronous I/O state held until cancellation drains."""

    _fields_ = [("internal", ctypes.c_size_t), ("internal_high", ctypes.c_size_t), ("offset", DWORD), ("offset_high", DWORD), ("event", HANDLE)]


class TokenUser(ctypes.Structure):
    """TOKEN_USER begins with one SID_AND_ATTRIBUTES record."""

    _fields_ = [("sid", POINTER), ("attributes", DWORD)]


class NativeCalls(Protocol):
    """All native calls and last-error reads are replaceable by deterministic fakes."""

    def call(self, name: str, *args: object) -> int:
        """Call a signature-bound Windows function."""
        ...

    def error(self) -> int:
        """Return the thread-local Windows error captured by ctypes."""
        ...


class NativeFunction(Protocol):
    """Typed seam for ctypes function-pointer configuration and invocation."""

    argtypes: list[object]
    restype: object

    def __call__(self, *args: object) -> int:
        """Return the native integral or pointer result."""
        ...


# Explicit pointer signatures prevent the default ctypes int return from
# truncating handles on 64-bit Windows. DLLs are loaded only in Native.__init__.
SIGNATURES: dict[str, tuple[str, object, list[object]]] = {
    "CloseHandle": ("kernel32", BOOL, [HANDLE]),
    "LocalFree": ("kernel32", HANDLE, [HANDLE]),
    "GetCurrentProcess": ("kernel32", HANDLE, []),
    "OpenProcess": ("kernel32", HANDLE, [DWORD, BOOL, DWORD]),
    "GetNamedPipeServerProcessId": ("kernel32", BOOL, [HANDLE, POINTER]),
    "GetNamedPipeClientProcessId": ("kernel32", BOOL, [HANDLE, POINTER]),
    "CreateFileW": ("kernel32", HANDLE, [ctypes.c_wchar_p, DWORD, DWORD, POINTER, DWORD, DWORD, HANDLE]),
    "CreateDirectoryW": ("kernel32", BOOL, [ctypes.c_wchar_p, POINTER]),
    "GetDriveTypeW": ("kernel32", DWORD, [ctypes.c_wchar_p]),
    "CreateNamedPipeW": ("kernel32", HANDLE, [ctypes.c_wchar_p, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, POINTER]),
    "ConnectNamedPipe": ("kernel32", BOOL, [HANDLE, POINTER]),
    "DisconnectNamedPipe": ("kernel32", BOOL, [HANDLE]),
    "CreateEventW": ("kernel32", HANDLE, [POINTER, BOOL, BOOL, ctypes.c_wchar_p]),
    "ReadFile": ("kernel32", BOOL, [HANDLE, POINTER, DWORD, POINTER, POINTER]),
    "WriteFile": ("kernel32", BOOL, [HANDLE, POINTER, DWORD, POINTER, POINTER]),
    "WaitForSingleObject": ("kernel32", DWORD, [HANDLE, DWORD]),
    "GetOverlappedResult": ("kernel32", BOOL, [HANDLE, POINTER, POINTER, BOOL]),
    "CancelIoEx": ("kernel32", BOOL, [HANDLE, POINTER]),
    "OpenProcessToken": ("advapi32", BOOL, [HANDLE, DWORD, POINTER]),
    "GetTokenInformation": ("advapi32", BOOL, [HANDLE, DWORD, POINTER, DWORD, POINTER]),
    "ConvertSidToStringSidW": ("advapi32", BOOL, [POINTER, POINTER]),
    "ConvertStringSecurityDescriptorToSecurityDescriptorW": ("advapi32", BOOL, [ctypes.c_wchar_p, DWORD, POINTER, POINTER]),
    "SetFileSecurityW": ("advapi32", BOOL, [ctypes.c_wchar_p, DWORD, POINTER]),
}


class Native:
    """Lazily bind Win32 functions; unit tests replace libraries or NativeCalls."""

    def __init__(self) -> None:
        """Load signatures only when constructing a Windows adapter."""
        if sys.platform != "win32":
            raise WaitError("platform-unsupported", "Windows required")
        loader = cast("Callable[..., object]", ctypes.WinDLL)
        libraries = {name: loader(name, use_last_error=True) for name in ("kernel32", "advapi32")}
        self.functions: dict[str, NativeFunction] = {}
        for name, (library, result, arguments) in SIGNATURES.items():
            function = cast("NativeFunction", getattr(libraries[library], name))
            function.argtypes = arguments
            function.restype = result
            self.functions[name] = function

    def call(self, name: str, *args: object) -> int:
        """Normalize a null pointer return to zero without losing handle width."""
        return self.functions[name](*args) or 0

    def error(self) -> int:
        """Read the saved Windows error immediately after a failed call."""
        return ctypes.get_last_error()


@dataclass(frozen=True)
class Peer:
    """OS-verified provenance, separate from any claimed workflow recipient."""

    pid: int
    sid: str


class Handle:
    """Idempotent ownership of exactly one OS handle, including failure cleanup."""

    def __init__(self, native: NativeCalls, value: int, *, owns_handle: bool = True) -> None:
        """Adopt a checked handle or borrow one without acquiring its lifetime."""
        self.native = native
        self.value = value
        self.owns_handle = owns_handle

    def close(self) -> None:
        """Release once; no file deletion can invalidate another owner's lock."""
        if self.value:
            value, self.value = self.value, 0
            if self.owns_handle:
                self.native.call("CloseHandle", value)


class WindowsIPC:
    """Enforce private state, singleton ownership and authenticated bounded pipes."""

    def __init__(self, native: NativeCalls | None = None) -> None:
        """Injection covers native success, error and cleanup paths on any OS."""
        self.native = native if native is not None else Native()

    def _checked(self, name: str, *args: object) -> int:
        result = self.native.call(name, *args)
        if not result or result == INVALID_HANDLE_VALUE:
            raise WaitError("ipc-unavailable", f"{name}: winerror={self.native.error()}")
        return result

    def current_sid(self) -> str:
        """Read the process token's user, never an environment username."""
        return self._process_sid(self.native.call("GetCurrentProcess"))

    def _process_sid(self, process: int) -> str:
        token = HANDLE()
        self._checked("OpenProcessToken", process, 0x0008, ctypes.byref(token))
        try:
            needed = DWORD()
            result = self.native.call("GetTokenInformation", token, 1, None, 0, ctypes.byref(needed))
            if result or self.native.error() != ERROR_INSUFFICIENT_BUFFER or not 0 < needed.value <= MAX_FRAME:
                raise WaitError("peer-refused", "invalid token sizing")
            buffer = ctypes.create_string_buffer(needed.value)
            self._checked("GetTokenInformation", token, 1, buffer, needed.value, ctypes.byref(needed))
            user = TokenUser.from_buffer(buffer)
            text = ctypes.c_wchar_p()
            self._checked("ConvertSidToStringSidW", user.sid, ctypes.byref(text))
            try:
                sid = text.value
                if not sid or not sid.startswith("S-1-"):
                    raise WaitError("peer-refused", "invalid token user SID")
                return sid
            finally:
                self.native.call("LocalFree", ctypes.cast(text, POINTER))
        finally:
            self.native.call("CloseHandle", token)

    def verify_peer(self, pipe: int, sid: str, *, server: bool) -> Peer:
        """Resolve the connected process and compare its token before frame I/O."""
        pid = DWORD()
        query = "GetNamedPipeServerProcessId" if server else "GetNamedPipeClientProcessId"
        self._checked(query, pipe, ctypes.byref(pid))
        process = self._checked("OpenProcess", 0x1000, 0, pid.value)
        try:
            peer_sid = self._process_sid(process)
            if peer_sid != sid:
                raise WaitError("peer-refused", "foreign OS user")
            return Peer(pid.value, peer_sid)
        finally:
            self.native.call("CloseHandle", process)

    @contextmanager
    def _security(self, sid: str) -> Generator[SecurityAttributes]:
        # Only an OS-derived numeric SID can enter SDDL, not caller-authored ACEs.
        if not sid.startswith("S-1-") or not all(part.isdecimal() for part in sid[4:].split("-")):
            raise WaitError("peer-refused", "invalid SID")
        descriptor = POINTER()
        sddl = f"D:P(A;OICI;FA;;;{sid})"
        self._checked("ConvertStringSecurityDescriptorToSecurityDescriptorW", sddl, 1, ctypes.byref(descriptor), None)
        try:
            yield SecurityAttributes(ctypes.sizeof(SecurityAttributes), descriptor, 0)
        finally:
            self.native.call("LocalFree", descriptor)

    def secure_home(self, home: Path, sid: str) -> None:
        """Create a private local state home and protect known preexisting artifacts."""
        if self.native.call("GetDriveTypeW", home.anchor) != DRIVE_FIXED:
            raise WaitError("invalid-home", "a local fixed drive is required")
        home.parent.mkdir(parents=True, exist_ok=True)
        with self._security(sid) as security:
            if not self.native.call("CreateDirectoryW", str(home), ctypes.byref(security)) and self.native.error() != ERROR_ALREADY_EXISTS:
                raise WaitError("storage-unavailable", "cannot create state home")
            for path in (home, *(home / name for name in ("store.sqlite3", "store.sqlite3-journal", "store.sqlite3-wal", "store.sqlite3-shm", "singleton.lock", "discovery.json"))):
                if path == home or path.exists():
                    self._checked("SetFileSecurityW", str(path), DACL_SECURITY_INFORMATION | PROTECTED_DACL_SECURITY_INFORMATION, security.descriptor)

    def try_lock(self, home: Path, sid: str) -> Handle | None:
        """Hold a nonshared handle for the authority/offline-reader lifetime."""
        with self._security(sid) as security:
            value = self.native.call("CreateFileW", str(home / "singleton.lock"), GENERIC_RW, 0, ctypes.byref(security), 4, 0x80, None)
            error = self.native.error()
        if value == INVALID_HANDLE_VALUE or not value:
            if error == ERROR_SHARING_VIOLATION:
                return None
            raise WaitError("storage-unavailable", f"singleton: winerror={error}")
        return Handle(self.native, value)

    def listen(self, endpoint: str, sid: str) -> PipeListener:
        """Reserve the first instance for the entire authority lifetime."""
        with self._security(sid) as security:
            value = self.native.call("CreateNamedPipeW", endpoint, 3 | FILE_FLAG_OVERLAPPED | FILE_FLAG_FIRST_PIPE_INSTANCE, PIPE_REJECT_REMOTE_CLIENTS, 1, MAX_FRAME, MAX_FRAME, 0, ctypes.byref(security))
            error = self.native.error()
        if not value or value == INVALID_HANDLE_VALUE:
            raise WaitError("endpoint-conflict", f"first pipe instance: winerror={error}")
        return PipeListener(self, value, sid)

    def connect(self, endpoint: str, sid: str, timeout: float) -> PipeConnection:
        """Connect locally and verify the server before permitting even hello."""
        if not endpoint.startswith("\\\\.\\pipe\\llm-shared-wait-"):
            raise WaitError("peer-refused", "nonlocal or invalid endpoint")
        value = self.native.call("CreateFileW", endpoint, GENERIC_RW, 0, None, 3, FILE_FLAG_OVERLAPPED | 0x00100000, None)
        if not value or value == INVALID_HANDLE_VALUE:
            error = self.native.error()
            code = "endpoint-unavailable" if error in {2, 231} else "peer-refused"
            raise WaitError(code, f"connect: winerror={error}")
        handle = Handle(self.native, value)
        try:
            peer = self.verify_peer(value, sid, server=True)
            return PipeConnection(self, handle, peer, timeout)
        except BaseException:
            handle.close()
            raise

    def perform(self, operation: str, handle: int, buffer: object, count: int, timeout: float) -> int:
        """Run finite overlapped I/O and drain pending work before buffer release."""
        event = Handle(self.native, self._checked("CreateEventW", None, 1, 0, None))
        overlap = Overlapped(event=event.value)
        transferred = DWORD()
        pending = False
        try:
            args = (handle, ctypes.byref(overlap)) if operation == "ConnectNamedPipe" else (handle, buffer, count, ctypes.byref(transferred), ctypes.byref(overlap))
            if self.native.call(operation, *args):
                return transferred.value
            error = self.native.error()
            if operation == "ConnectNamedPipe" and error == ERROR_PIPE_CONNECTED:
                return 0
            if error != ERROR_IO_PENDING:
                raise WaitError("ipc-unavailable", f"{operation}: winerror={error}")
            pending = True
            wait = self.native.call("WaitForSingleObject", event.value, max(0, int(timeout * 1000)))
            if wait != 0:
                code = "ipc-timeout" if wait == WAIT_TIMEOUT else "ipc-unavailable"
                raise WaitError(code, "bounded pipe operation did not complete")
            self._checked("GetOverlappedResult", handle, ctypes.byref(overlap), ctypes.byref(transferred), 0)
            pending = False
            return transferred.value
        finally:
            if pending:
                self.native.call("CancelIoEx", handle, ctypes.byref(overlap))
                self.native.call("GetOverlappedResult", handle, ctypes.byref(overlap), ctypes.byref(transferred), 1)
            event.close()


class PipeConnection:
    """Authenticated bounded stream; closing never affects singleton ownership."""

    def __init__(self, ipc: WindowsIPC, handle: Handle, peer: Peer, timeout: float, *, clock: Callable[[], float] = time.monotonic) -> None:
        """Adopt an authenticated client handle or a borrowed listener handle."""
        self.ipc, self.handle, self.peer = ipc, handle, peer
        self.clock, self.deadline = clock, clock() + timeout

    @property
    def verified_sid(self) -> str:
        """Expose only the SID obtained from the connected process token."""
        return self.peer.sid

    def _remaining(self) -> float:
        remaining = self.deadline - self.clock()
        if remaining <= 0:
            raise WaitError("ipc-timeout", "connection deadline exhausted")
        return remaining

    def read(self, count: int) -> bytes:
        """Read at most one bounded frame-sized chunk."""
        if not 0 < count <= MAX_FRAME:
            raise WaitError("invalid-frame", "invalid read size")
        buffer = ctypes.create_string_buffer(count)
        size = self.ipc.perform("ReadFile", self.handle.value, buffer, count, self._remaining())
        return buffer.raw[:size]

    def write(self, data: bytes) -> None:
        """Write one complete encoded frame, rejecting partial native writes."""
        if not 0 < len(data) <= MAX_FRAME + HEADER_SIZE:
            raise WaitError("invalid-frame", "invalid write size")
        buffer = ctypes.create_string_buffer(data)
        size = self.ipc.perform("WriteFile", self.handle.value, buffer, len(data), self._remaining())
        if size != len(data):
            raise WaitError("ipc-unavailable", "partial pipe write")

    def close(self) -> None:
        """Release client ownership; borrowed listener handles stay reserved."""
        self.handle.close()


class PipeListener(Handle):
    """One reusable first-instance handle keeps squatted successors out."""

    def __init__(self, ipc: WindowsIPC, value: int, sid: str) -> None:
        """Keep native first-instance ownership across sequential connections."""
        super().__init__(ipc.native, value)
        self.ipc, self.sid = ipc, sid

    @contextmanager
    def accept(self, timeout: float) -> Generator[PipeConnection]:
        """Authenticate the connected client before exposing read/write methods."""
        try:
            self.ipc.perform("ConnectNamedPipe", self.value, None, 0, timeout)
            peer = self.ipc.verify_peer(self.value, self.sid, server=False)
            yield PipeConnection(self.ipc, Handle(self.native, self.value, owns_handle=False), peer, timeout)
        finally:
            self.native.call("DisconnectNamedPipe", self.value)


def launch_hidden(command: list[str], cwd: Path, *, popen: Callable[..., subprocess.Popen[bytes]] = subprocess.Popen) -> int:
    """Launch a hidden survivor without inherited streams, handles or a shell.

    Breakaway refusal is explicit: silently retrying inside a kill-on-close job
    would report success while losing the service when its initiating shell exits.
    """
    try:
        child = popen(command, cwd=str(cwd), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True, creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB)
    except OSError as error:
        raise WaitError("startup-unavailable", "hidden survivor launch failed") from error
    return child.pid


# eof
