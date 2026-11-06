r"""program_status.py.

Report an agent's state to the terminal that hosts it with OSC 7501, the
Program Status Protocol:
<https://www.superlogical.com/rex/docs/build/program-status>.

An agent that ends its turn on a pending decision without a blocking picker
reports ``blocked`` with ``kind=question`` (``rules/interactive_menu.md``).
tuios and Windows Terminal then show it as waiting for the user, until it
reports ``working`` again.

The bytes must reach the terminal, not the agent's captured command output:

- On Windows, a command an agent runs has a console of its own: hidden, or a
  pseudo console the agent reads back. The report goes to the console of the
  nearest ancestor attached to another console window, the agent's own, which
  its terminal (a tuios pane, a Windows Terminal tab) hosts. When every
  ancestor shares the command's console window, that console is the terminal.
  The walk never passes an ancestor without a console: a background server
  running the command, such as the shared Codex app-server daemon, descends
  from another session, whose terminal must not get this report.
- Elsewhere it goes to ``/dev/tty`` or, for a command without a controlling
  terminal, to the terminal device of the nearest ancestor that has one.

Usage::

    program_status.py STATE [--app APP] [--kind KIND] [--msg TEXT] [--id ID]

STATE is idle, working, done, blocked, error or clear. A report replaces the
record it names (the main record without ``--id``), so send ``--app`` each
time. Exit status: 0 delivered, 2 invalid report, 3 no terminal took it.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import ctypes
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, TextIO

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping, Sequence

STATES = ("idle", "working", "done", "blocked", "error", "clear")
KINDS = ("permission", "question", "auth")
MSG_LIMIT = 2048
ID_LIMIT = 128
ID_DEPTH = 8
OSC_PREFIX = b"\x1b]7501;"
STRING_TERMINATOR = b"\x1b\\"
EXIT_DELIVERED = 0
EXIT_INVALID = 2
EXIT_UNREACHED = 3

_TOKEN = re.compile(r"[A-Za-z0-9_.+-]{1,32}")
_DROPPED_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn"})
_NO_TTY = frozenset({"", "?", "??", "-"})
_MAX_ANCESTORS = 32
_ATTACH_PARENT_PROCESS = 0xFFFFFFFF
_TH32CS_SNAPPROCESS = 0x2
_GENERIC_READ_WRITE = 0xC0000000
_FILE_SHARE_READ_WRITE = 0x3
_OPEN_EXISTING = 3
_INVALID_HANDLE = ctypes.c_void_p(-1).value


class ProgramStatusError(ValueError):
    """A report the protocol would reject."""


@dataclass(frozen=True)
class Report:
    """One OSC 7501 report: its state, record id and the keys it carries."""

    state: str
    app: str = ""
    kind: str = ""
    msg: str = ""
    record_id: str = ""


@dataclass(frozen=True)
class Delivery:
    """Where a report went, and how many of its bytes the terminal took."""

    target: str
    written: int


def one_line(text: str, limit: int = MSG_LIMIT) -> str:
    """Return ``text`` as one printable line of at most ``limit`` UTF-8 bytes.

    Args:
        text: Any text, possibly with line breaks or control characters.
        limit: The largest UTF-8 size the line may have.

    Returns:
        The words of ``text`` joined by single spaces, without control or
        invisible formatting characters, cut on a character boundary.
    """
    kept = "".join(
        char for char in text if char.isspace() or unicodedata.category(char) not in _DROPPED_CATEGORIES
    )
    data = " ".join(kept.split()).encode("utf-8")[:limit]
    return data.decode("utf-8", errors="ignore").rstrip()


def _check_token(name: str, value: str) -> None:
    if not _TOKEN.fullmatch(value):
        message = f"{name} must be 1 to 32 letters, digits, '_', '.', '+' or '-', not {value!r}"
        raise ProgramStatusError(message)


def _check_record_id(record_id: str) -> None:
    segments = record_id.split("/")
    if len(segments) > ID_DEPTH or len(record_id.encode("utf-8")) > ID_LIMIT:
        message = f"--id holds at most {ID_DEPTH} segments and {ID_LIMIT} bytes, not {record_id!r}"
        raise ProgramStatusError(message)
    for segment in segments:
        _check_token("each --id segment", segment)


def _check_state(report: Report) -> None:
    if report.state not in STATES:
        message = f"unknown state {report.state!r}; use one of {', '.join(STATES)}"
        raise ProgramStatusError(message)
    if report.kind and report.state != "blocked":
        message = "--kind applies to the blocked state only"
        raise ProgramStatusError(message)
    if report.kind and report.kind not in KINDS:
        message = f"unknown kind {report.kind!r}; use one of {', '.join(KINDS)}"
        raise ProgramStatusError(message)


def encode(report: Report) -> bytes:
    r"""Return the OSC 7501 bytes of ``report``, terminated by ESC backslash.

    Args:
        report: The report to encode.

    Returns:
        ``ESC ] 7501 ; key=value:... ESC \\``, with ``msg`` as standard Base64
        of its one-line UTF-8 text.

    Raises:
        ProgramStatusError: The state, kind, app or id breaks the protocol.
    """
    _check_state(report)
    pairs = [f"state={report.state}"]
    if report.record_id:
        _check_record_id(report.record_id)
        pairs.append(f"id={report.record_id}")
    if report.kind:
        pairs.append(f"kind={report.kind}")
    if report.app:
        _check_token("--app", report.app)
        pairs.append(f"app={report.app}")
    text = one_line(report.msg)
    if text:
        pairs.append("msg=" + base64.b64encode(text.encode("utf-8")).decode("ascii"))
    return OSC_PREFIX + ":".join(pairs).encode("ascii") + STRING_TERMINATOR


class ConsoleApi(Protocol):
    """The Windows console calls the delivery needs."""

    def current_pid(self) -> int:
        """Return this process's id."""
        ...

    def processes(self) -> Mapping[int, tuple[int, str]]:
        """Return each running process id with its parent id and executable."""
        ...

    def window(self) -> int:
        """Return the window of the console this process is attached to, or 0."""
        ...

    def detach(self) -> None:
        """Detach this process from its console."""
        ...

    def attach(self, pid: int) -> bool:
        """Attach this process to the console of ``pid``."""
        ...

    def write(self, data: bytes) -> int:
        """Write ``data`` to the attached console's output, returning the bytes taken."""
        ...


def ancestors(table: Mapping[int, tuple[int, str]], pid: int) -> Iterator[tuple[int, str]]:
    """Yield each ancestor of ``pid`` with its executable name, nearest first.

    Args:
        table: Each process id with its parent id and executable name.
        pid: The process whose ancestors to walk.

    Yields:
        ``(pid, executable)`` for the parent, the grandparent, and so on,
        until a parent has exited or the walk would loop.
    """
    seen = {pid}
    parent = table.get(pid, (0, ""))[0]
    while parent in table and parent not in seen and len(seen) <= _MAX_ANCESTORS:
        seen.add(parent)
        yield parent, table[parent][1]
        parent = table[parent][0]


def _terminal_console(api: ConsoleApi, own: int, chain: Iterator[tuple[int, str]]) -> tuple[int, str] | None:
    """Return the ancestor whose console is the agent's terminal.

    The first ancestor with a console window other than ``own`` wins. An
    ancestor sharing ``own`` is kept as the answer when none differs. The walk
    stops at the first ancestor without a console. Above the agent, that is the
    process hosting the terminal (tuios, Windows Terminal). Below it, that is a
    background server running the command for the agent, such as the shared
    Codex app-server daemon: its own ancestors belong to another session, whose
    terminal must never receive this report.
    """
    shared: tuple[int, str] | None = None
    for pid, name in chain:
        api.detach()
        if not api.attach(pid):
            break
        window = api.window()
        if window and window != own:
            return pid, name
        if window and shared is None:
            shared = pid, name
    return shared


def deliver_to_console(api: ConsoleApi, data: bytes) -> Delivery | None:
    """Write ``data`` to the console of the terminal that hosts the agent.

    Args:
        api: The console calls, kernel32 or a stand-in.
        data: The bytes of one report.

    Returns:
        The console written to and the bytes it took, or None when no
        ancestor's console could be reached. This process attaches to its
        parent's console again before returning.
    """
    own = api.window()
    chain = ancestors(api.processes(), api.current_pid())
    try:
        target = _terminal_console(api, own, chain)
        if target is None:
            return None
        pid, name = target
        api.detach()
        if not api.attach(pid):
            return None
        return Delivery(f"the console of {name} (pid {pid})", api.write(data))
    finally:
        api.detach()
        api.attach(_ATTACH_PARENT_PROCESS)


class _ProcessEntry(ctypes.Structure):
    """PROCESSENTRY32W, as CreateToolhelp32Snapshot lists the processes."""

    dwSize: int  # noqa: N815 - the Windows structure's field names
    th32ProcessID: int  # noqa: N815
    th32ParentProcessID: int  # noqa: N815
    szExeFile: str  # noqa: N815
    _fields_: ClassVar = [
        ("dwSize", ctypes.c_uint32),
        ("cntUsage", ctypes.c_uint32),
        ("th32ProcessID", ctypes.c_uint32),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", ctypes.c_uint32),
        ("cntThreads", ctypes.c_uint32),
        ("th32ParentProcessID", ctypes.c_uint32),
        ("pcPriClassBase", ctypes.c_int32),
        ("dwFlags", ctypes.c_uint32),
        ("szExeFile", ctypes.c_wchar * 260),
    ]


def _load_kernel32() -> Any:  # noqa: ANN401 - a ctypes DLL
    """Load kernel32 with the handle-sized signatures the console calls need."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
    handle = ctypes.c_void_p
    kernel32.GetConsoleWindow.restype = handle
    kernel32.AttachConsole.argtypes = (ctypes.c_uint32,)
    kernel32.CreateToolhelp32Snapshot.argtypes = (ctypes.c_uint32, ctypes.c_uint32)
    kernel32.CreateToolhelp32Snapshot.restype = handle
    entry = ctypes.POINTER(_ProcessEntry)
    kernel32.Process32FirstW.argtypes = (handle, entry)
    kernel32.Process32NextW.argtypes = (handle, entry)
    kernel32.CloseHandle.argtypes = (handle,)
    kernel32.CreateFileW.argtypes = (
        ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, handle,
    )
    kernel32.CreateFileW.restype = handle
    kernel32.WriteFile.argtypes = (handle, ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p)
    return kernel32


class Kernel32Console:
    """The console calls of kernel32, as ``deliver_to_console`` needs them."""

    def __init__(self, kernel32: Any) -> None:  # noqa: ANN401 - a ctypes DLL
        """Keep the kernel32 functions (or a stand-in) to call."""
        self._kernel32 = kernel32

    def current_pid(self) -> int:
        """Return this process's id."""
        return os.getpid()

    def processes(self) -> dict[int, tuple[int, str]]:
        """Return each running process id with its parent id and executable."""
        snapshot = self._kernel32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
        if snapshot in {None, _INVALID_HANDLE}:
            return {}
        entry = _ProcessEntry()
        entry.dwSize = ctypes.sizeof(entry)
        table: dict[int, tuple[int, str]] = {}
        try:
            found = self._kernel32.Process32FirstW(snapshot, ctypes.pointer(entry))
            while found:
                table[entry.th32ProcessID] = (entry.th32ParentProcessID, entry.szExeFile)
                found = self._kernel32.Process32NextW(snapshot, ctypes.pointer(entry))
        finally:
            self._kernel32.CloseHandle(snapshot)
        return table

    def window(self) -> int:
        """Return the window of the attached console, or 0 for none or a hidden one."""
        return int(self._kernel32.GetConsoleWindow() or 0)

    def detach(self) -> None:
        """Detach this process from its console."""
        self._kernel32.FreeConsole()

    def attach(self, pid: int) -> bool:
        """Attach this process to the console of ``pid``."""
        return bool(self._kernel32.AttachConsole(pid))

    def write(self, data: bytes) -> int:
        """Write ``data`` to the attached console's output, returning the bytes taken."""
        handle = self._kernel32.CreateFileW(
            "CONOUT$", _GENERIC_READ_WRITE, _FILE_SHARE_READ_WRITE, None, _OPEN_EXISTING, 0, None,
        )
        if handle in {None, _INVALID_HANDLE}:
            return 0
        written = ctypes.c_uint32()
        try:
            if not self._kernel32.WriteFile(handle, data, len(data), ctypes.pointer(written), None):
                return 0
        finally:
            self._kernel32.CloseHandle(handle)
        return written.value


def _write_device(path: str, data: bytes) -> int:
    descriptor = os.open(path, os.O_WRONLY | getattr(os, "O_NOCTTY", 0))
    try:
        return os.write(descriptor, data)
    finally:
        os.close(descriptor)


def _process_tty(pid: int) -> tuple[int, str] | None:
    """Return the parent id and terminal name of ``pid``, as ``ps`` reports them."""
    result = subprocess.run(  # noqa: S603 - fixed arguments, no shell
        ["ps", "-o", "ppid=,tty=", "-p", str(pid)],  # noqa: S607 - ps from PATH
        capture_output=True,
        text=True,
        check=False,
    )
    fields = result.stdout.split()
    if result.returncode or len(fields) != 2 or not fields[0].isdigit():  # noqa: PLR2004 - ppid and tty
        return None
    return int(fields[0]), fields[1]


def deliver_to_tty(
    data: bytes,
    *,
    write_device: Callable[[str, bytes], int] = _write_device,
    process_tty: Callable[[int], tuple[int, str] | None] = _process_tty,
    pid: int | None = None,
) -> Delivery | None:
    """Write ``data`` to the controlling terminal, or to the nearest ancestor's.

    Args:
        data: The bytes of one report.
        write_device: Writes bytes to a device path and returns the count.
        process_tty: Returns the parent id and terminal name of a process.
        pid: The process to start the walk from; this process by default.

    Returns:
        The device written to and the bytes it took, or None when neither this
        process nor an ancestor has a terminal it can write to.
    """
    with contextlib.suppress(OSError):
        return Delivery("/dev/tty", write_device("/dev/tty", data))
    current = os.getpid() if pid is None else pid
    for _ in range(_MAX_ANCESTORS):
        info = process_tty(current)
        if info is None:
            return None
        parent, tty = info
        if tty not in _NO_TTY:
            device = f"/dev/{tty}"
            with contextlib.suppress(OSError):
                return Delivery(device, write_device(device, data))
            return None
        if parent <= 1:
            return None
        current = parent
    return None


def deliver(data: bytes) -> Delivery | None:
    """Write ``data`` to the terminal that hosts the agent, on this system."""
    if os.name == "nt":
        return deliver_to_console(Kernel32Console(_load_kernel32()), data)
    return deliver_to_tty(data)


def describe(report: Report) -> str:
    """Name a report's keys for a one-line confirmation, without its message."""
    parts = [f"state={report.state}"]
    parts += [f"{key}={value}" for key, value in (("id", report.record_id), ("kind", report.kind), ("app", report.app)) if value]
    return " ".join(parts)


def _say(text: str, stream: TextIO) -> None:
    """Print a line; a stream lost with this process's console is not an error."""
    with contextlib.suppress(OSError, ValueError):
        print(text, file=stream, flush=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command line of one report."""
    parser = argparse.ArgumentParser(
        prog="program_status",
        description="Report this agent's state to its terminal with OSC 7501 (Program Status Protocol).",
    )
    parser.add_argument("state", help=f"one of {', '.join(STATES)}")
    parser.add_argument("--app", default="", help="stable program id, such as codex or claude; send it every time")
    parser.add_argument("--kind", default="", help=f"what a blocked program waits for: {', '.join(KINDS)}")
    parser.add_argument("--msg", default="", help="one line naming what the program does or waits for")
    parser.add_argument("--id", dest="record_id", default="", help="record to address, such as build/test; the main record by default")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None, *, send: Callable[[bytes], Delivery | None] = deliver) -> int:
    """Encode one report, write it to the hosting terminal, and say where it went.

    Args:
        argv: The command line arguments, ``sys.argv[1:]`` by default.
        send: Writes the report's bytes to the terminal.

    Returns:
        0 once the terminal took every byte, 2 for an invalid report, 3 when
        no terminal could be reached.
    """
    args = parse_args(argv)
    report = Report(args.state, args.app, args.kind, args.msg, args.record_id)
    try:
        data = encode(report)
    except ProgramStatusError as error:
        _say(f"program-status: {error}", sys.stderr)
        return EXIT_INVALID
    delivery = send(data)
    if delivery is None or delivery.written != len(data):
        _say(
            f"program-status: no terminal took the report; {describe(report)} was not delivered."
            " No console window was found among this command's ancestors before a process without a console,"
            " such as a background server running the command (the shared Codex app-server daemon).",
            sys.stderr,
        )
        return EXIT_UNREACHED
    _say(f"program-status: delivered {describe(report)} ({len(data)} bytes) to {delivery.target}", sys.stdout)
    return EXIT_DELIVERED


if __name__ == "__main__":
    raise SystemExit(main())


# eof
