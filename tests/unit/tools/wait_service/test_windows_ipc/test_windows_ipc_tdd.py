"""Exercise explicit native-call errors without real Windows resources."""

# ruff: noqa: PLR2004 - Assertions spell out native boundary values.

from __future__ import annotations

import ctypes
import subprocess
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock

import pytest

from tools.wait_service import windows_ipc as win
from tools.wait_service.models import WaitError
from tools.wait_service.windows_ipc import WindowsIPC

if TYPE_CHECKING:
    from pathlib import Path

SID = "S-1-5-21-1"
ENDPOINT = "\\\\.\\pipe\\llm-shared-wait-test"


class FakeNative:
    """Native pointer outputs and errors are explicit, with a complete call ledger."""

    def __init__(self) -> None:
        """Default calls succeed without creating any operating-system resources."""
        self.calls: list[tuple[str, tuple[object, ...]]] = []
        self.fail: dict[str, int] = {}
        self.last_error = 0
        self.sid_buffer = ctypes.create_unicode_buffer(SID)
        self.pending: str | None = None
        self.wait_result = 0
        self.connected = False
        self.short_write = False
        self.token_sizing = 122

    def error(self) -> int:
        """Return the error retained by the immediately preceding native call."""
        return self.last_error

    def call(self, name: str, *args: object) -> int:
        """Emulate only documented outputs at the native function boundary."""
        self.calls.append((name, args))
        if name in self.fail:
            self.last_error = self.fail[name]
            return 0
        self.last_error = 0
        if name in {"OpenProcessToken", "GetTokenInformation", "ConvertSidToStringSidW", "ConvertStringSecurityDescriptorToSecurityDescriptorW"}:
            return self.security_call(name, args)
        return self.pipe_call(name, args)

    def security_call(self, name: str, args: tuple[object, ...]) -> int:
        """Set token and security-descriptor output pointers."""
        if name == "OpenProcessToken":
            ctypes.cast(cast("Any", args[2]), ctypes.POINTER(win.HANDLE))[0] = win.HANDLE(12)
        elif name == "GetTokenInformation":
            ctypes.cast(cast("Any", args[4]), ctypes.POINTER(win.DWORD))[0] = win.DWORD(ctypes.sizeof(win.TokenUser))
            if args[2] is None:
                self.last_error = self.token_sizing
                return 0
            ctypes.cast(cast("Any", args[2]), ctypes.POINTER(win.TokenUser))[0] = win.TokenUser(1, 0)
        elif name == "ConvertSidToStringSidW":
            ctypes.cast(cast("Any", args[1]), ctypes.POINTER(win.POINTER))[0] = ctypes.cast(self.sid_buffer, win.POINTER)
        elif name == "ConvertStringSecurityDescriptorToSecurityDescriptorW":
            ctypes.cast(cast("Any", args[2]), ctypes.POINTER(win.POINTER))[0] = win.POINTER(21)
        return 1

    def pipe_call(self, name: str, args: tuple[object, ...]) -> int:  # noqa: PLR0911 - Native error codes are returned at their boundary.
        """Model immediate, pending and already-connected pipe operations."""
        if name.startswith("GetNamedPipe"):
            ctypes.cast(cast("Any", args[1]), ctypes.POINTER(win.DWORD))[0] = win.DWORD(123)
        elif name == "GetDriveTypeW":
            return 3
        elif name == "WaitForSingleObject":
            return self.wait_result
        elif name == "ConnectNamedPipe" and self.connected:
            self.last_error = win.ERROR_PIPE_CONNECTED
            return 0
        elif name == self.pending:
            self.last_error = win.ERROR_IO_PENDING
            return 0
        else:
            return self.transfer_call(name, args)
        return 1

    def transfer_call(self, name: str, args: tuple[object, ...]) -> int:
        """Fill immediate or completed overlapped transfer counts."""
        if name == "ReadFile":
            ctypes.memmove(cast("Any", args[1]), b"hi", 2)
            ctypes.cast(cast("Any", args[3]), ctypes.POINTER(win.DWORD))[0] = win.DWORD(2)
        elif name == "WriteFile":
            ctypes.cast(cast("Any", args[3]), ctypes.POINTER(win.DWORD))[0] = win.DWORD(1 if self.short_write else cast("int", args[2]))
        elif name == "GetOverlappedResult":
            ctypes.cast(cast("Any", args[2]), ctypes.POINTER(win.DWORD))[0] = win.DWORD(2)
        return 1

    def names(self) -> list[str]:
        """Expose call ordering without pointer representation noise."""
        return [name for name, _args in self.calls]


class TestWindowsIPC:
    """Non-Windows collection stays safe and construction fails explicitly."""

    def test_unsupported_platform(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Importing the module never loads Windows DLLs."""
        monkeypatch.setattr("tools.wait_service.windows_ipc.sys.platform", "linux")
        with pytest.raises(WaitError, match="platform-unsupported"):
            WindowsIPC()

    def test_signatures_bind_lazily_and_preserve_wide_handles(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The actual Native wrapper binds every signature and handles null pointers."""
        libraries = MagicMock()
        monkeypatch.setattr(win.ctypes, "WinDLL", libraries, raising=False)
        monkeypatch.setattr(win.ctypes, "get_last_error", lambda: 5, raising=False)
        native = win.Native()
        assert native.functions["CreateFileW"].restype is win.HANDLE
        libraries.return_value.CreateFileW.return_value = 1 << 48
        assert native.call("CreateFileW") == 1 << 48
        libraries.return_value.CreateFileW.return_value = None
        assert native.call("CreateFileW") == 0
        assert native.error() == 5

    def test_token_sid_and_mutual_peer_provenance(self) -> None:
        """Both sides use token users; no read/write happens while authenticating."""
        native = FakeNative()
        ipc = WindowsIPC(native)
        assert ipc.current_sid() == SID
        for server in (True, False):
            assert ipc.verify_peer(9, SID, server=server) == win.Peer(123, SID)
        assert "GetNamedPipeServerProcessId" in native.names()
        assert "GetNamedPipeClientProcessId" in native.names()
        assert "ReadFile" not in native.names()
        assert native.names().count("CloseHandle") == 5
        assert native.names().count("LocalFree") == 3

    @pytest.mark.parametrize("name", ["GetNamedPipeServerProcessId", "OpenProcess", "OpenProcessToken", "GetTokenInformation", "ConvertSidToStringSidW"])
    def test_peer_native_failure_closes_connection(self, name: str) -> None:
        """An unverifiable server never receives a hello, even after partial setup."""
        native = FakeNative()
        native.fail[name] = 5
        with pytest.raises(WaitError):
            WindowsIPC(native).connect(ENDPOINT, SID, 1)
        assert "ReadFile" not in native.names()
        assert "WriteFile" not in native.names()
        assert native.names()[-1] == "CloseHandle"

    def test_verified_client_connection_owns_only_its_handle(self) -> None:
        """A same-user server permits I/O after token verification and closes once."""
        native = FakeNative()
        connection = WindowsIPC(native).connect(ENDPOINT, SID, 1)
        assert connection.verified_sid == SID
        assert "ReadFile" not in native.names()
        connection.write(b"hello")
        assert native.names().index("GetNamedPipeServerProcessId") < native.names().index("WriteFile")
        before = native.names().count("CloseHandle")
        connection.close()
        connection.close()
        assert native.names().count("CloseHandle") == before + 1

    @pytest.mark.parametrize("sid", ["S-1-5-21-foreign", "", "nonsense"])
    def test_foreign_or_invalid_token_user_is_refused(self, sid: str) -> None:
        """Even an openable process cannot bypass the verified user comparison."""
        native = FakeNative()
        native.sid_buffer = ctypes.create_unicode_buffer(sid)
        with pytest.raises(WaitError, match="peer-refused"):
            WindowsIPC(native).connect(ENDPOINT, SID, 1)
        assert "ReadFile" not in native.names()
        assert native.names()[-1] == "CloseHandle"

    def test_unexpected_token_sizing_is_refused(self) -> None:
        """Token allocation requires the documented bounded sizing response."""
        native = FakeNative()
        native.token_sizing = 5
        with pytest.raises(WaitError, match="peer-refused"):
            WindowsIPC(native).current_sid()
        assert native.names()[-1] == "CloseHandle"

    @pytest.mark.parametrize(("error", "code"), [(2, "endpoint-unavailable"), (231, "endpoint-unavailable"), (5, "peer-refused")])
    def test_connect_errors_and_remote_rejection(self, error: int, code: str) -> None:
        """Only missing/busy local endpoints are startup retry candidates."""
        native = FakeNative()
        native.fail["CreateFileW"] = error
        ipc = WindowsIPC(native)
        with pytest.raises(WaitError, match=code):
            ipc.connect(ENDPOINT, SID, 1)
        native.calls.clear()
        with pytest.raises(WaitError, match="peer-refused"):
            ipc.connect("\\\\remote\\pipe\\test", SID, 1)
        assert native.calls == []

    def test_private_home_and_existing_database_acl(self, tmp_path: Path) -> None:
        """The home and existing durable files receive a protected user-only ACL."""
        native = FakeNative()
        home = tmp_path / "home"
        home.mkdir()
        (home / "store.sqlite3").touch()
        WindowsIPC(native).secure_home(home, SID)
        acl_calls = [args for name, args in native.calls if name == "SetFileSecurityW"]
        assert [args[0] for args in acl_calls] == [str(home), str(home / "store.sqlite3")]
        assert all(args[1] == win.DACL_SECURITY_INFORMATION | win.PROTECTED_DACL_SECURITY_INFORMATION for args in acl_calls)
        sddl = next(args[0] for name, args in native.calls if name == "ConvertStringSecurityDescriptorToSecurityDescriptorW")
        assert sddl == f"D:P(A;OICI;FA;;;{SID})"
        assert native.names()[-1] == "LocalFree"

    @pytest.mark.parametrize(("operation", "code"), [("GetDriveTypeW", "invalid-home"), ("CreateDirectoryW", "storage-unavailable"), ("SetFileSecurityW", "ipc-unavailable"), ("ConvertStringSecurityDescriptorToSecurityDescriptorW", "ipc-unavailable")])
    def test_home_native_failure(self, tmp_path: Path, operation: str, code: str) -> None:
        """Security or locality failures never continue to database creation."""
        native = FakeNative()
        native.fail[operation] = 5
        with pytest.raises(WaitError, match=code):
            WindowsIPC(native).secure_home(tmp_path / "home", SID)
        assert "CreateFileW" not in native.names()

    def test_existing_home_and_invalid_sddl_identity(self, tmp_path: Path) -> None:
        """Already-existing directories are secured; SDDL injection is refused."""
        native = FakeNative()
        native.fail["CreateDirectoryW"] = 183
        ipc = WindowsIPC(native)
        ipc.secure_home(tmp_path, SID)
        with pytest.raises(WaitError, match="peer-refused"):
            ipc.try_lock(tmp_path, "S-1-5);evil")

    def test_singleton_release_and_offline_contention(self, tmp_path: Path) -> None:
        """Share mode zero serializes owners and releases once without deletion."""
        native = FakeNative()
        ipc = WindowsIPC(native)
        lock = ipc.try_lock(tmp_path, SID)
        assert lock is not None
        args = next(args for name, args in native.calls if name == "CreateFileW")
        assert args[2] == 0
        lock.close()
        lock.close()
        assert native.names().count("CloseHandle") == 1
        native.fail["CreateFileW"] = 32
        assert ipc.try_lock(tmp_path, SID) is None
        native.fail["CreateFileW"] = 5
        with pytest.raises(WaitError, match="storage-unavailable"):
            ipc.try_lock(tmp_path, SID)

    def test_first_instance_remote_flags_and_squatting(self) -> None:
        """The first-instance flag and user ACL are mandatory, not default security."""
        native = FakeNative()
        ipc = WindowsIPC(native)
        listener = ipc.listen(ENDPOINT, SID)
        args = next(args for name, args in native.calls if name == "CreateNamedPipeW")
        assert cast("int", args[1]) & win.FILE_FLAG_FIRST_PIPE_INSTANCE
        assert cast("int", args[1]) & win.FILE_FLAG_OVERLAPPED
        assert args[2] == win.PIPE_REJECT_REMOTE_CLIENTS
        listener.close()
        native.fail["CreateNamedPipeW"] = 5
        with pytest.raises(WaitError, match="endpoint-conflict"):
            ipc.listen(ENDPOINT, SID)

    @pytest.mark.timeout(5)
    def test_accept_authenticates_before_io_and_keeps_first_instance(self) -> None:
        """Disconnecting a client retains the listener's exclusive endpoint claim."""
        native = FakeNative()
        listener = WindowsIPC(native).listen(ENDPOINT, SID)
        with listener.accept(1) as connection:
            assert connection.verified_sid == SID
            assert "ReadFile" not in native.names()
            assert connection.read(3) == b"hi"
            connection.write(b"ok")
            calls = len(native.calls)
            connection.close()
            assert len(native.calls) == calls
        assert native.names()[-1] == "DisconnectNamedPipe"
        assert listener.value != 0
        native.sid_buffer = ctypes.create_unicode_buffer("S-1-5-21-2")
        with pytest.raises(WaitError, match="peer-refused"), listener.accept(1):
            pytest.fail("foreign peer reached application")
        assert native.names()[-1] == "DisconnectNamedPipe"
        listener.close()

    def test_connection_bounds_deadline_and_partial_write(self) -> None:
        """A slow stream cannot renew its deadline for every fragment."""
        native = FakeNative()
        clock = [0.0]
        connection = win.PipeConnection(WindowsIPC(native), win.Handle(native, 9), win.Peer(1, SID), 1, clock=lambda: clock[0])
        for count in [0, 65537]:
            with pytest.raises(WaitError, match="invalid-frame"):
                connection.read(count)
        for data in [b"", b"x" * 65541]:
            with pytest.raises(WaitError, match="invalid-frame"):
                connection.write(data)
        native.short_write = True
        with pytest.raises(WaitError, match="partial pipe write"):
            connection.write(b"abcd")
        clock[0] = 1.0
        with pytest.raises(WaitError, match="ipc-timeout"):
            connection.read(1)
        connection.close()
        assert native.names()[-1] == "CloseHandle"

    @pytest.mark.parametrize("operation", ["ReadFile", "WriteFile", "ConnectNamedPipe"])
    def test_overlapped_completion(self, operation: str) -> None:
        """Pending work completes through a bounded event wait and result retrieval."""
        native = FakeNative()
        native.pending = operation
        assert WindowsIPC(native).perform(operation, 9, ctypes.create_string_buffer(3), 3, 0.25) == 2
        assert next(args[1] for name, args in native.calls if name == "WaitForSingleObject") == 250
        assert "CancelIoEx" not in native.names()
        assert native.names()[-1] == "CloseHandle"

    @pytest.mark.parametrize("wait", [win.WAIT_TIMEOUT, 0xFFFFFFFF])
    def test_timeout_drains_before_event_close(self, wait: int) -> None:
        """Cancel and drain before releasing OVERLAPPED memory and event handles."""
        native = FakeNative()
        native.pending = "ReadFile"
        native.wait_result = wait
        with pytest.raises(WaitError):
            WindowsIPC(native).perform("ReadFile", 9, ctypes.create_string_buffer(3), 3, 0.25)
        assert native.names()[-3:] == ["CancelIoEx", "GetOverlappedResult", "CloseHandle"]
        assert native.calls[-2][1][-1] == 1

    def test_connected_race_and_native_io_errors(self) -> None:
        """Already-connected clients work; all other native failures release handles."""
        native = FakeNative()
        native.connected = True
        ipc = WindowsIPC(native)
        assert ipc.perform("ConnectNamedPipe", 9, None, 0, 1) == 0
        native.fail["ReadFile"] = 109
        with pytest.raises(WaitError, match="ipc-unavailable"):
            ipc.perform("ReadFile", 9, None, 0, 1)
        assert native.names()[-1] == "CloseHandle"
        native.fail.clear()
        native.pending = "ReadFile"
        native.fail["GetOverlappedResult"] = 5
        with pytest.raises(WaitError, match="ipc-unavailable"):
            ipc.perform("ReadFile", 9, None, 0, 1)
        assert native.names()[-3:] == ["CancelIoEx", "GetOverlappedResult", "CloseHandle"]
        native.fail["CreateEventW"] = 5
        with pytest.raises(WaitError, match="ipc-unavailable"):
            ipc.perform("ReadFile", 9, None, 0, 1)

    def test_hidden_survivor_spawn_and_breakaway_refusal(self, tmp_path: Path) -> None:
        """No shell/standard stream/handle ties remain to the initiating parent."""
        popen = MagicMock(return_value=MagicMock(pid=42))
        command = ["C:/verified/python.exe", "-m", "tools.wait_service.runtime", "--home", str(tmp_path)]
        assert win.launch_hidden(command, tmp_path, popen=popen) == 42
        kwargs = popen.call_args.kwargs
        assert kwargs["creationflags"] == win.CREATE_NO_WINDOW | win.CREATE_NEW_PROCESS_GROUP | win.CREATE_BREAKAWAY_FROM_JOB
        assert kwargs["close_fds"] is True
        assert kwargs["stdin"] == kwargs["stdout"] == kwargs["stderr"] == subprocess.DEVNULL
        popen.side_effect = OSError("job disallows breakaway")
        with pytest.raises(WaitError, match="startup-unavailable"):
            win.launch_hidden(command, tmp_path, popen=popen)


# eof
