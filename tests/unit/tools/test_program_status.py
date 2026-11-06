"""Tests for `tools.program_status`, the OSC 7501 report an agent sends its terminal.

The report must reach the terminal hosting the agent, not the captured output
of the command that sends it. These tests pin the encoded bytes against the
Program Status Protocol, the choice of the console to write to (hidden,
shared or private consoles of an agent's commands), the POSIX terminal walk
and the command line. No test detaches or attaches the test process's own
console: every console call goes to a stand-in.
"""

from __future__ import annotations

import base64
import ctypes
import io
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tests.script_entry import run_main
from tools import program_status as ps

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001, N802

_PARENT = ps._ATTACH_PARENT_PROCESS
_AGENT = 12
_ABC = b"abc"


def _msg(data: bytes) -> str:
    """Decode the msg value of an encoded report."""
    body = data.removeprefix(ps.OSC_PREFIX).removesuffix(ps.STRING_TERMINATOR).decode("ascii")
    value = dict(pair.split("=", 1) for pair in body.split(":"))["msg"]
    return base64.b64decode(value).decode("utf-8")


def test_blocked_question_encodes_the_protocol_bytes() -> None:
    """A question report is ESC ] 7501 ; pairs ESC backslash, msg in Base64."""
    data = ps.encode(ps.Report("blocked", app="codex", kind="question", msg="Q60/Q73 13%: retry policy?"))

    assert data == (
        b"\x1b]7501;state=blocked:kind=question:app=codex:msg="
        + base64.b64encode(b"Q60/Q73 13%: retry policy?")
        + b"\x1b\\"
    )


def test_record_id_comes_after_the_state_and_clear_needs_no_other_key() -> None:
    """The id addresses a child record; a clear report carries nothing else."""
    assert ps.encode(ps.Report("working", app="claude", record_id="review/q60")) == (
        b"\x1b]7501;state=working:id=review/q60:app=claude\x1b\\"
    )
    assert ps.encode(ps.Report("clear")) == b"\x1b]7501;state=clear\x1b\\"


def test_message_becomes_one_printable_line() -> None:
    """Line breaks fold into spaces; control and invisible characters go."""
    text = "Pick\n\tA\x1b[31m or\N{ZERO WIDTH SPACE} B?\N{LINE SEPARATOR} "
    data = ps.encode(ps.Report("blocked", kind="question", msg=text))

    assert _msg(data) == "Pick A[31m or B?"


def test_message_is_cut_on_a_character_boundary() -> None:
    """A long message keeps whole UTF-8 characters within the limit."""
    assert ps.one_line("é" * 5, limit=5) == "éé"
    assert ps.one_line("  \n ") == ""
    assert len(ps.one_line("x" * 5000).encode("utf-8")) == ps.MSG_LIMIT


@pytest.mark.parametrize(
    ("report", "error"),
    [
        (ps.Report("waiting"), "unknown state 'waiting'"),
        (ps.Report("working", kind="question"), "blocked state only"),
        (ps.Report("blocked", kind="input"), "unknown kind 'input'"),
        (ps.Report("blocked", app="co:dex"), "--app must be"),
        (ps.Report("blocked", app="a" * 33), "--app must be"),
        (ps.Report("done", record_id="a//b"), "each --id segment"),
        (ps.Report("done", record_id="/".join("a" * 9)), "at most 8 segments"),
        (ps.Report("done", record_id="/".join(["a" * 32] * 4) + "/b"), "128 bytes"),
    ],
)
def test_reports_the_protocol_would_drop_are_refused(report: ps.Report, error: str) -> None:
    """Every key the terminal would reject is caught before anything is written."""
    with pytest.raises(ps.ProgramStatusError, match=error):
        ps.encode(report)


_TABLE: Mapping[int, tuple[int, str]] = {
    10: (11, "python.exe"),
    11: (12, "cmd.exe"),
    12: (13, "codex.exe"),
    13: (14, "cmd.exe"),
    14: (99, "tuios.exe"),
}


def test_ancestors_walk_up_until_a_parent_is_gone() -> None:
    """The walk lists each living ancestor, nearest first, and never loops."""
    assert list(ps.ancestors(_TABLE, 10)) == [(11, "cmd.exe"), (12, "codex.exe"), (13, "cmd.exe"), (14, "tuios.exe")]
    assert list(ps.ancestors({1: (2, "a"), 2: (1, "b")}, 1)) == [(2, "b")]
    assert list(ps.ancestors(_TABLE, 42)) == []


class _FakeConsoles:
    """Stand in for the console calls: which process has which console window.

    A window of None means no console at all (attach fails); 0 means a hidden
    console, with no window.
    """

    def __init__(self, own: int, windows: Mapping[int, int | None]) -> None:
        self.own, self.windows = own, windows
        self.attached: int | None = 1
        self.calls: list[tuple[str, int]] = []
        self.data = b""

    def current_pid(self) -> int:
        return 10

    def processes(self) -> Mapping[int, tuple[int, str]]:
        return _TABLE

    def window(self) -> int:
        if self.attached == 1:
            return self.own
        return self.windows.get(self.attached or 0) or 0

    def detach(self) -> None:
        self.calls.append(("detach", 0))
        self.attached = None

    def attach(self, pid: int) -> bool:
        self.calls.append(("attach", pid))
        if pid == _PARENT or self.windows.get(pid) is not None:
            self.attached = pid
            return True
        return False

    def write(self, data: bytes) -> int:
        self.calls.append(("write", self.attached or 0))
        self.data = data
        return len(data)


@pytest.mark.parametrize(
    ("own", "windows", "target"),
    [
        (0, {11: 0, 12: 7, 13: 7, 14: None}, 12),
        (7, {11: 7, 12: 7, 13: 7, 14: None}, 11),
        (5, {11: 5, 12: 7, 13: 7, 14: None}, 12),
    ],
    ids=["hidden-command-console", "shared-console", "private-pseudo-console"],
)
def test_console_delivery_reaches_the_agents_terminal(own: int, windows: Mapping[int, int | None], target: int) -> None:
    """The report lands on the agent's console window, then the parent's console is restored."""
    api = _FakeConsoles(own, windows)

    delivery = ps.deliver_to_console(api, b"report")

    assert delivery == ps.Delivery(f"the console of {_TABLE[target][1]} (pid {target})", 6)
    assert ("write", target) in api.calls
    assert api.calls[-2:] == [("detach", 0), ("attach", _PARENT)]


def test_console_delivery_stops_at_the_terminal_host() -> None:
    """Past the console windows, a consoleless host ends the walk: nothing beyond it is written."""
    api = _FakeConsoles(7, {11: 7, 12: 7, 13: None, 14: 9})

    assert ps.deliver_to_console(api, b"report") == ps.Delivery("the console of cmd.exe (pid 11)", 6)
    assert ("attach", 14) not in api.calls


@pytest.mark.parametrize(
    "windows",
    [{11: 0, 12: None, 13: None, 14: None}, {11: 0, 12: None, 13: 7, 14: None}],
    ids=["no-console-window", "background-server"],
)
def test_console_delivery_reports_an_unreachable_terminal(windows: Mapping[int, int | None]) -> None:
    """A consoleless ancestor ends the walk: another session's console above it gets nothing.

    The second case is the shared Codex app-server daemon: it has no console,
    and its parent is the Codex session that started it, in another pane.
    """
    api = _FakeConsoles(0, windows)

    assert ps.deliver_to_console(api, b"report") is None
    assert all(call[0] != "write" for call in api.calls)
    assert ("attach", 13) not in api.calls
    assert api.calls[-2:] == [("detach", 0), ("attach", _PARENT)]


def test_console_delivery_gives_up_when_the_console_vanishes() -> None:
    """The chosen console refusing the second attach gives no delivery."""

    class _Vanishing(_FakeConsoles):
        def attach(self, pid: int) -> bool:
            attached = super().attach(pid)
            if pid == _AGENT and ("attach", _AGENT) in self.calls[:-1]:
                return False
            return attached

    api = _Vanishing(0, {11: 0, 12: 7, 13: None, 14: None})

    assert ps.deliver_to_console(api, b"report") is None
    assert all(call[0] != "write" for call in api.calls)


class _FakeKernel32:
    """Stand in for kernel32: a process snapshot, a console and its output."""

    def __init__(self, *, snapshot: int | None = 3, handle: int | None = 5, writes: bool = True) -> None:
        self.snapshot, self.handle, self.writes = snapshot, handle, writes
        self.rows = [(10, 11, "python.exe"), (11, 12, "cmd.exe")]
        self.calls: list[tuple[object, ...]] = []

    def CreateToolhelp32Snapshot(self, flags: int, pid: int) -> int | None:
        self.calls.append(("snapshot", flags, pid))
        return self.snapshot

    def _fill(self, entry: ctypes._Pointer[ps._ProcessEntry]) -> int:
        if not self.rows:
            return 0
        pid, parent, name = self.rows.pop(0)
        entry.contents.th32ProcessID, entry.contents.th32ParentProcessID, entry.contents.szExeFile = pid, parent, name
        return 1

    def Process32FirstW(self, snapshot: int, entry: ctypes._Pointer[ps._ProcessEntry]) -> int:
        assert entry.contents.dwSize == ctypes.sizeof(ps._ProcessEntry)
        return self._fill(entry) if snapshot else 0

    def Process32NextW(self, snapshot: int, entry: ctypes._Pointer[ps._ProcessEntry]) -> int:
        return self._fill(entry) if snapshot else 0

    def CloseHandle(self, handle: int) -> int:
        self.calls.append(("close", handle))
        return 1

    def GetConsoleWindow(self) -> int | None:
        return None

    def FreeConsole(self) -> int:
        self.calls.append(("free",))
        return 1

    def AttachConsole(self, pid: int) -> int:
        self.calls.append(("attach", pid))
        return int(pid == _AGENT)

    def CreateFileW(self, *args: object) -> int | None:
        self.calls.append(("open", *args))
        return self.handle

    def WriteFile(
        self, handle: int, data: bytes, size: int, written: ctypes._Pointer[ctypes.c_uint32], overlapped: None,
    ) -> int:
        self.calls.append(("write", handle, data, size, overlapped))
        written.contents.value = size
        return int(self.writes)


def test_kernel32_console_lists_processes_and_closes_the_snapshot() -> None:
    """Each snapshot entry gives its parent and executable; the snapshot is closed."""
    kernel32 = _FakeKernel32()
    console = ps.Kernel32Console(kernel32)

    assert console.processes() == {10: (11, "python.exe"), 11: (12, "cmd.exe")}
    assert kernel32.calls == [("snapshot", ps._TH32CS_SNAPPROCESS, 0), ("close", 3)]
    assert console.current_pid() == os.getpid()


@pytest.mark.parametrize("snapshot", [None, ps._INVALID_HANDLE])
def test_kernel32_console_without_a_snapshot_lists_nothing(snapshot: int | None) -> None:
    """A failed snapshot gives an empty table rather than an error."""
    assert ps.Kernel32Console(_FakeKernel32(snapshot=snapshot)).processes() == {}


def test_kernel32_console_attaches_and_writes_to_the_console_output() -> None:
    """Attach, window and write map to AttachConsole, GetConsoleWindow and CONOUT$."""
    kernel32 = _FakeKernel32()
    console = ps.Kernel32Console(kernel32)

    console.detach()
    assert console.attach(12)
    assert not console.attach(13)
    assert console.window() == 0
    assert console.write(_ABC) == len(_ABC)
    assert kernel32.calls[-2:] == [("write", 5, _ABC, len(_ABC), None), ("close", 5)]
    assert ("open", "CONOUT$", ps._GENERIC_READ_WRITE, ps._FILE_SHARE_READ_WRITE, None, ps._OPEN_EXISTING, 0, None) in kernel32.calls


@pytest.mark.parametrize(("handle", "writes"), [(None, True), (ps._INVALID_HANDLE, True), (5, False)])
def test_kernel32_console_reports_no_bytes_for_a_refused_write(handle: int | None, writes: bool) -> None:  # noqa: FBT001
    """No console output handle, or a failed write, counts zero bytes taken."""
    assert ps.Kernel32Console(_FakeKernel32(handle=handle, writes=writes)).write(b"abc") == 0


@pytest.mark.skipif(os.name != "nt", reason="kernel32 exists on Windows only")
def test_real_kernel32_lists_this_process_with_its_parent() -> None:
    """The real snapshot finds this process, and handle results are not truncated."""
    kernel32 = ps._load_kernel32()

    assert kernel32.CreateFileW.restype is ctypes.c_void_p
    assert ps.Kernel32Console(kernel32).processes()[os.getpid()][0] == os.getppid()


def _fail_device(path: str, data: bytes) -> int:
    raise OSError(path, len(data))


def test_tty_delivery_prefers_the_controlling_terminal() -> None:
    """A command with a controlling terminal writes to /dev/tty."""
    written: list[str] = []

    def _device(path: str, data: bytes) -> int:
        written.append(path)
        return len(data)

    assert ps.deliver_to_tty(b"abc", write_device=_device) == ps.Delivery("/dev/tty", 3)
    assert written == ["/dev/tty"]


def test_tty_delivery_falls_back_to_the_nearest_ancestor_terminal() -> None:
    """Without a controlling terminal, the first ancestor with one takes the report."""
    tree = {10: (11, "?"), 11: (12, "??"), 12: (13, "pts/3")}

    def _device(path: str, data: bytes) -> int:
        if path == "/dev/tty":
            raise OSError(path)
        return len(data)

    assert ps.deliver_to_tty(b"abc", write_device=_device, process_tty=tree.get, pid=10) == ps.Delivery("/dev/pts/3", 3)


@pytest.mark.parametrize(
    "tree",
    [{}, {10: (1, "?")}, {10: (11, "pts/3")}],
    ids=["ps-failed", "reached-init", "ancestor-terminal-refused"],
)
def test_tty_delivery_reports_an_unreachable_terminal(tree: Mapping[int, tuple[int, str]]) -> None:
    """No ancestor terminal, or one refusing the write, gives no delivery."""
    assert ps.deliver_to_tty(b"abc", write_device=_fail_device, process_tty=tree.get, pid=10) is None


def test_tty_delivery_stops_after_a_bounded_walk() -> None:
    """An endless chain without a terminal ends after a bounded number of ancestors."""

    def _endless(pid: int) -> tuple[int, str]:
        return pid + 1, "?"

    assert ps.deliver_to_tty(b"abc", write_device=_fail_device, process_tty=_endless, pid=10) is None


def test_write_device_writes_the_bytes(tmp_path: Path) -> None:
    """The device writer opens, writes and closes the path."""
    device = tmp_path / "tty"
    device.write_bytes(b"")

    assert ps._write_device(str(device), _ABC) == len(_ABC)
    assert device.read_bytes() == _ABC


@pytest.mark.parametrize(
    ("stdout", "returncode", "expected"),
    [("  1234 pts/3\n", 0, (1234, "pts/3")), ("", 1, None), ("1234\n", 0, None), ("x pts/3", 0, None)],
)
def test_process_tty_reads_ps(
    monkeypatch: pytest.MonkeyPatch, stdout: str, returncode: int, expected: tuple[int, str] | None,
) -> None:
    """The parent id and terminal come from one ps call; anything else is no answer."""
    seen: list[list[str]] = []

    def _run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        seen.append(command)
        return subprocess.CompletedProcess(command, returncode, stdout, "")

    monkeypatch.setattr(ps.subprocess, "run", _run)

    assert ps._process_tty(77) == expected
    assert seen == [["ps", "-o", "ppid=,tty=", "-p", "77"]]


@pytest.mark.parametrize(("os_name", "used"), [("nt", "console"), ("posix", "tty")])
def test_deliver_picks_the_system_terminal(monkeypatch: pytest.MonkeyPatch, os_name: str, used: str) -> None:
    """Windows goes through kernel32 consoles; other systems through terminal devices."""
    seen: list[str] = []
    kernel32 = _FakeKernel32()

    def _console(api: ps.ConsoleApi, data: bytes) -> ps.Delivery:
        assert isinstance(api, ps.Kernel32Console)
        assert api._kernel32 is kernel32
        seen.append("console")
        return ps.Delivery("console", len(data))

    def _tty(data: bytes) -> ps.Delivery:
        seen.append("tty")
        return ps.Delivery("tty", len(data))

    def _load() -> _FakeKernel32:
        return kernel32

    monkeypatch.setattr(ps, "_load_kernel32", _load)
    monkeypatch.setattr(ps, "deliver_to_console", _console)
    monkeypatch.setattr(ps, "deliver_to_tty", _tty)
    monkeypatch.setattr(ps.os, "name", os_name)

    assert ps.deliver(b"abc") == ps.Delivery(used, 3)
    assert seen == [used]


def test_main_reports_where_the_report_went(capsys: pytest.CaptureFixture[str]) -> None:
    """A delivered report exits 0 and names its keys and target, not its message."""
    sent: list[bytes] = []

    def _send(data: bytes) -> ps.Delivery:
        sent.append(data)
        return ps.Delivery("the console of codex.exe (pid 12)", len(data))

    code = ps.main(["blocked", "--kind", "question", "--app", "codex", "--msg", "Pick A or B?"], send=_send)

    assert code == ps.EXIT_DELIVERED
    assert _msg(sent[0]) == "Pick A or B?"
    out = capsys.readouterr().out
    assert out == (
        f"program-status: delivered state=blocked kind=question app=codex ({len(sent[0])} bytes)"
        " to the console of codex.exe (pid 12)\n"
    )


@pytest.mark.parametrize("delivery", [None, ps.Delivery("the console of codex.exe (pid 12)", 1)])
def test_main_reports_an_undelivered_report(capsys: pytest.CaptureFixture[str], delivery: ps.Delivery | None) -> None:
    """No terminal, or a short write, exits 3 and says the state was not delivered."""

    def _send(data: bytes) -> ps.Delivery | None:
        del data
        return delivery

    assert ps.main(["working", "--app", "codex", "--id", "q60"], send=_send) == ps.EXIT_UNREACHED
    err = capsys.readouterr().err
    assert err.startswith("program-status: no terminal took the report; state=working id=q60 app=codex was not delivered.")
    assert "the shared Codex app-server daemon" in err


def test_main_refuses_an_invalid_report_before_sending(capsys: pytest.CaptureFixture[str]) -> None:
    """An invalid key exits 2 and sends nothing."""

    def _send(data: bytes) -> ps.Delivery:
        raise AssertionError(data)

    assert ps.main(["done", "--kind", "question"], send=_send) == ps.EXIT_INVALID
    assert capsys.readouterr().err == "program-status: --kind applies to the blocked state only\n"


def test_say_ignores_a_stream_lost_with_the_console() -> None:
    """A stream that broke while the process was attached elsewhere is not an error."""

    class _Broken(io.StringIO):
        def write(self, s: str) -> int:
            raise OSError(s)

    ps._say("lost", _Broken())


def test_script_guard_runs_main(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Running the file, as the launcher does, delegates to main and exits with its status."""
    monkeypatch.setattr(sys, "argv", ["program_status.py", "idle", "--kind", "auth"])

    with pytest.raises(SystemExit) as raised:
        run_main(ps)

    assert raised.value.code == ps.EXIT_INVALID
    assert "blocked state only" in capsys.readouterr().err


# eof
