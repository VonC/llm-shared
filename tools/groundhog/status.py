"""Run lifecycle of groundhog: ``a.ghog.status`` and survivors (Q32).

A harness tool timeout killed a real ``ghog day`` walk mid-suite while
the orphaned pytest child kept feeding ``a.ghog.log``: the log looked
alive, but the report, the coverage step and the exit code never came,
and the caller — with no way to tell a finished walk from a killed
one — guessed from tails and process listings, then replayed the whole
walk. The exit code and the log tail are completion proofs that die
with the foreground call; this module makes the lifecycle a file
contract instead, with no per-call timeout anywhere: walks have no
portable upper bound.

Every run subcommand (check, full, affected, single, day) brackets
itself in ``a.ghog.status`` at the project root: one ``state=running``
line with its pid at start, one ``state=done`` line with its exit code
at the end of every exit path, both written atomically. A hard kill is
the one event that leaves ``state=running`` behind with a dead pid —
exactly the verdict the read-only ``ghog status`` reporter turns into
exit codes: the recorded code passes through once done, 6 says a run
is live (wait, poll again, start nothing), 7 says the last run is lost
(killed or never recorded — relaunch ``ghog day``). The same exit 6
backs the live-run refusal: no run command starts while another one is
alive, so a second walk can never trample the first one's log or
testmon state.

``ghog day --detach`` spawns the walk as a survivor process — a
hidden console, broken away from the harness job object when
allowed — wired by the tool itself to ``a.ghog.log`` (the parked senv
preamble folded in first), and acknowledges with exit 6 once the
child has written its first status line.

Fix: the survivor used to start with DETACHED_PROCESS — no console at
all — so its console children (check.bat, pytest) allocated a fresh
visible console window on the user's desktop for the whole walk.
CREATE_NO_WINDOW gives the survivor a hidden console those children
inherit: a detached walk no longer pops any window.
"""

from __future__ import annotations

import ctypes
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final

from tools.groundhog import commands, redirect, reporting, runner
from tools.groundhog.models import EXIT_RUN_LIVE, EXIT_RUN_LOST, EXIT_SETUP_ERROR

if TYPE_CHECKING:
    from typing import TextIO

    from tools.groundhog.context import Deps, Invocation

LOGGER = logging.getLogger("groundhog")

# The run lifecycle file at the project root (Q32).
STATUS_FILE_NAME: Final = "a.ghog.status"
# The two lifecycle states; a hard kill leaves "running" behind.
STATE_RUNNING: Final = "running"
STATE_DONE: Final = "done"
# Windows process-probe constants: the access right any live pid
# grants, and the GetExitCodeProcess value of a still-running process.
_PROCESS_QUERY_LIMITED_INFORMATION: Final = 0x1000
_STILL_ACTIVE: Final = 259
# The detach handshake: how many short naps the launcher waits for the
# survivor's first a.ghog.status write before calling it silent.
_HANDSHAKE_TRIES: Final = 50
_HANDSHAKE_PAUSE_SECONDS: Final = 0.2

# The status-line keys, the same key=value grammar as Q16.
_STATE_RE: Final = re.compile(r"\bstate=(running|done)\b")
_PID_RE: Final = re.compile(r"\bpid=(\d+)\b")
_EXIT_RE: Final = re.compile(r"\bexit=(\d+)\b")


@dataclass(frozen=True)
class RunStatus:
    """One parsed ``a.ghog.status`` line.

    Attributes:
        line: The raw status line, replayed verbatim by the reporter.
        state: ``running`` or ``done``.
        pid: The recorded pid of a running state, ``None`` otherwise.
        exit_code: The recorded exit of a done state, ``None`` otherwise.
    """

    line: str
    state: str
    pid: int | None
    exit_code: int | None


def status_path(root: Path) -> Path:
    """Return the lifecycle file path for a project root.

    Args:
        root: The project root directory.

    Returns:
        The ``a.ghog.status`` path under that root.
    """
    return root / STATUS_FILE_NAME


def clear_status(root: Path) -> None:
    """Drop a stale lifecycle file before a detached launch (Q32).

    Args:
        root: The project root directory.
    """
    status_path(root).unlink(missing_ok=True)


def write_running(root: Path, label: str) -> None:
    """Record that a run started, with the pid owning it (Q32).

    Args:
        root: The project root directory.
        label: The subcommand label of the run.
    """
    _write(
        root,
        f"{root.name}: ghog {label} state={STATE_RUNNING} "
        f"pid={os.getpid()} started={_now()}",
    )


def write_done(root: Path, label: str, exit_code: int) -> None:
    """Record that a run ended, with its exit code (Q32).

    Args:
        root: The project root directory.
        label: The subcommand label of the run.
        exit_code: The contract exit code of the run.
    """
    _write(
        root,
        f"{root.name}: ghog {label} state={STATE_DONE} exit={exit_code} ended={_now()}",
    )


def read_status(root: Path) -> RunStatus | None:
    """Parse the recorded lifecycle line, if any.

    Args:
        root: The project root directory.

    Returns:
        The parsed status, or ``None`` on a missing, unreadable or
        key-free file — the no-proof direction (Q32).
    """
    try:
        text = status_path(root).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    state_match = _STATE_RE.search(text)
    if state_match is None:
        return None
    pid_match = _PID_RE.search(text)
    exit_match = _EXIT_RE.search(text)
    return RunStatus(
        line=text,
        state=state_match.group(1),
        pid=int(pid_match.group(1)) if pid_match else None,
        exit_code=int(exit_match.group(1)) if exit_match else None,
    )


def live_run(root: Path) -> RunStatus | None:
    """Return the recorded run only while it is provably alive (Q32).

    Args:
        root: The project root directory.

    Returns:
        The running status whose pid is alive, ``None`` otherwise.
    """
    recorded = read_status(root)
    if recorded is None or recorded.state != STATE_RUNNING:
        return None
    if recorded.pid is None or not pid_alive(recorded.pid):
        return None
    return recorded


def pid_alive(pid: int) -> bool:
    """Tell whether a recorded pid still names a live process (Q32).

    A recycled pid keeps the verdict at "live" — the conservative
    direction, broken by deleting ``a.ghog.status`` — and a process
    that exits with the STILL_ACTIVE sentinel (259) reads as alive,
    the documented Windows caveat of GetExitCodeProcess.

    Args:
        pid: The recorded pid.

    Returns:
        True when the pid names a live process, False otherwise.
    """
    if pid <= 0:
        return False
    if sys.platform == "win32":
        return _pid_alive_windows(pid)
    return _pid_alive_posix(pid)


def _pid_alive_windows(pid: int) -> bool:
    """Probe a pid through OpenProcess and GetExitCodeProcess.

    Args:
        pid: The recorded pid.

    Returns:
        True when the process exists and is still active.
    """
    kernel32 = ctypes.windll.kernel32
    handle: int = kernel32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
    if not handle:
        return False
    try:
        exit_code = ctypes.c_ulong()
        queried: int = kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        return bool(queried) and exit_code.value == _STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)


def _pid_alive_posix(pid: int) -> bool:
    """Probe a pid with the no-op signal 0.

    Args:
        pid: The recorded pid.

    Returns:
        True when the process exists, even when owned by another user.
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def run_status(invocation: Invocation) -> int:
    """Report the recorded run lifecycle, the read-only poll (Q32).

    Args:
        invocation: The parsed invocation.

    Returns:
        The recorded exit code on ``state=done``, ``EXIT_RUN_LIVE``
        while the run is alive, ``EXIT_RUN_LOST`` on a killed run, a
        missing file or an unreadable done code.
    """
    recorded = read_status(invocation.root)
    if recorded is None:
        commands.emit_summary([reporting.MSG_STATUS_NONE])
        return EXIT_RUN_LOST
    if recorded.state == STATE_DONE:
        commands.emit_summary([recorded.line, reporting.MSG_STATUS_DONE])
        return recorded.exit_code if recorded.exit_code is not None else EXIT_RUN_LOST
    if recorded.pid is not None and pid_alive(recorded.pid):
        commands.emit_summary([recorded.line, reporting.MSG_STATUS_RUNNING])
        return EXIT_RUN_LIVE
    commands.emit_summary([recorded.line, reporting.MSG_STATUS_KILLED])
    return EXIT_RUN_LOST


def refuse_live_run(live: RunStatus) -> int:
    """Refuse to start a run while another one is alive (Q32).

    Args:
        live: The live status recorded by the other run.

    Returns:
        ``EXIT_RUN_LIVE``; nothing was spawned, nothing was written.
    """
    commands.emit_summary([live.line, reporting.run_live_line(live.pid)])
    return EXIT_RUN_LIVE


def run_with_lifecycle(invocation: Invocation, deps: Deps) -> int:
    """Run one subcommand inside the running/done bracket (Q32).

    The done line lands on every exit path, even a crashing dispatch
    (recorded as the setup-error code before the exception travels
    on); only a hard kill of this process leaves ``running`` behind.

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The dispatched contract exit code.
    """
    label = commands.sub_label(invocation)
    write_running(invocation.root, label)
    code = EXIT_SETUP_ERROR
    try:
        code = _dispatch(invocation, deps)
    finally:
        write_done(invocation.root, label, code)
    return code


def _dispatch(invocation: Invocation, deps: Deps) -> int:
    """Route one run subcommand to its executor.

    ``init`` and ``status`` never reach this: the CLI routes them
    outside the lifecycle bracket.

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The executor's contract exit code.
    """
    if invocation.sub == runner.SUB_CHECK:
        return commands.run_check(invocation, deps)
    if invocation.sub == runner.SUB_DAY:
        return commands.run_day(invocation, deps)
    return commands.run_tests(invocation, deps)


def run_day_detached(invocation: Invocation, deps: Deps) -> int:
    """Launch the day walk as a survivor process (Q32).

    The launcher consumes the parked senv preamble for the child's
    log, clears any stale lifecycle file, spawns the survivor, then
    waits for the child's first status write — the start handshake —
    before acknowledging, so a caller polling right away never reads
    the void between the spawn and the child's first write.

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        ``EXIT_RUN_LIVE`` once the walk is provably started, the
        setup-error code on a spawn failure or a silent child.
    """
    preamble = redirect.consume_senv_log()
    clear_status(invocation.root)
    try:
        pid = deps.detach_factory(
            _detached_day_command(invocation),
            invocation.root / redirect.LOG_NAME,
            preamble,
            invocation.root,
        )
    except OSError as error:
        commands.emit_summary([f"ghog: detached walk failed to start: {error}"])
        return EXIT_SETUP_ERROR
    for _ in range(_HANDSHAKE_TRIES):
        if read_status(invocation.root) is not None:
            commands.emit_summary([reporting.detached_line(pid)])
            return EXIT_RUN_LIVE
        deps.sleep(_HANDSHAKE_PAUSE_SECONDS)
    commands.emit_summary([reporting.MSG_DETACH_SILENT])
    return EXIT_SETUP_ERROR


def default_detach_factory(
    command: list[str],
    log_path: Path,
    preamble: str,
    cwd: Path,
) -> int:
    """Spawn a survivor child wired to the report log (Q32).

    The tool opens the log itself — no caller redirect exists to be
    truncated — writes the senv preamble first, then hands the file
    position to the child; the parent handle closes right after the
    spawn, leaving the child as the only writer.

    Args:
        command: The survivor command line.
        log_path: The report log the child writes to.
        preamble: The parked senv text folded in before the child.
        cwd: The working directory, the consuming project root.

    Returns:
        The survivor pid.

    Raises:
        OSError: When the log cannot be opened or the spawn fails.
    """
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        if preamble:
            log.write(preamble if preamble.endswith("\n") else f"{preamble}\n")
            log.flush()
        return _spawn_survivor(command, log, cwd).pid


def _spawn_survivor(
    command: list[str],
    log: TextIO,
    cwd: Path,
) -> subprocess.Popen[bytes]:
    """Start the detached child, breaking away from the job if allowed.

    The Windows spawn hides the console with CREATE_NO_WINDOW instead
    of dropping it with DETACHED_PROCESS: a console-free survivor
    hands its console children (check.bat, pytest) a fresh visible
    console window, while a hidden console is inherited silently.

    Args:
        command: The survivor command line.
        log: The opened report log receiving stdout and stderr.
        cwd: The working directory of the child.

    Returns:
        The started survivor process.
    """
    if sys.platform != "win32":
        return subprocess.Popen(  # noqa: S603
            command,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        return subprocess.Popen(  # noqa: S603
            command,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=flags | subprocess.CREATE_BREAKAWAY_FROM_JOB,
        )
    except OSError:
        return subprocess.Popen(  # noqa: S603
            command,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )


def _detached_day_command(invocation: Invocation) -> list[str]:
    """Build the survivor command of a detached day walk (Q32).

    Args:
        invocation: The parsed invocation carrying root and force.

    Returns:
        The python command running ``cli.py day`` in LLM mode.
    """
    command = [
        sys.executable,
        str(Path(__file__).resolve().with_name("cli.py")),
        runner.SUB_DAY,
        "--root",
        str(invocation.root),
        "--llm",
    ]
    if invocation.force:
        command.append("--force")
    return command


def _now() -> str:
    """Return the local-time stamp of a lifecycle line.

    Returns:
        The ISO timestamp, second precision, with the UTC offset.
    """
    return datetime.now(tz=UTC).astimezone().isoformat(timespec="seconds")


def _write(root: Path, line: str) -> None:
    """Write one lifecycle line atomically, never killing the run.

    Args:
        root: The project root directory.
        line: The status line to record.
    """
    path = status_path(root)
    side = path.with_name(f"{STATUS_FILE_NAME}.tmp")
    try:
        side.write_text(f"{line}\n", encoding="utf-8")
        side.replace(path)
    except OSError as error:
        LOGGER.info("ghog: could not write %s: %s", STATUS_FILE_NAME, error)


# eof
