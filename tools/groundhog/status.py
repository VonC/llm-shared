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

``ghog day --detach`` spawns the walk as a survivor process polled through
``ghog status``; the launch and the survivor spawn live in ``detach.py``.

Fix (v0.13.0 full_suite_levels, Step 1): the lifecycle bracket takes its
subcommand label from ``progress.sub_label``, where the label moved with the
progress sink out of ``commands.py``.

Fix (v0.13.0 full_suite_levels, Step 2): the status lines carry the run
evidence. The running line adds ``full=``, ``src=``, ``scope=`` and
``proof=pending`` (``scope=`` alone for a run without a level), and the done
line adds the closing keys before ``exit=``, so ``ghog status`` replays the
same evidence a foreground walk prints. The dispatch returns a
``RunOutcome``. A killed run is relaunched at the level its recorded running
line carried. The detached launch, the survivor spawn and their handshake
moved to ``detach.py``, the plan's extraction once this module passed 550
lines.
"""

from __future__ import annotations

import ctypes
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final

from tools.groundhog import commands, day, evidence, progress, reporting, runner
from tools.groundhog.levels import FullLevel, level_from_token
from tools.groundhog.models import EXIT_RUN_LIVE, EXIT_RUN_LOST, EXIT_SETUP_ERROR

if TYPE_CHECKING:
    from pathlib import Path

    from tools.groundhog.context import Deps, Invocation
    from tools.groundhog.evidence import RunOutcome

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

# The status-line keys, the same key=value grammar as Q16.
_STATE_RE: Final = re.compile(r"\bstate=(running|done)\b")
_PID_RE: Final = re.compile(r"\bpid=(\d+)\b")
_EXIT_RE: Final = re.compile(r"\bexit=(\d+)\b")
# The recorded objective of a running line, for the killed-run relaunch.
_FULL_RE: Final = re.compile(r"\bfull=([a-z]+)\b")


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


def write_running(root: Path, label: str, keys: str = "") -> None:
    """Record that a run started, with the pid owning it (Q32).

    Args:
        root: The project root directory.
        label: The subcommand label of the run.
        keys: The running evidence keys, such as ``full=cov src=param
            scope=whole proof=pending``; empty for none.
    """
    _write(
        root,
        f"{root.name}: ghog {label} state={STATE_RUNNING}{_spaced(keys)} "
        f"pid={os.getpid()} started={_now()}",
    )


def write_done(root: Path, label: str, exit_code: int, keys: str = "") -> None:
    """Record that a run ended, with its evidence and exit code (Q32).

    Args:
        root: The project root directory.
        label: The subcommand label of the run.
        exit_code: The contract exit code of the run.
        keys: The closing evidence keys, written before ``exit=``; empty for
            none.
    """
    _write(
        root,
        f"{root.name}: ghog {label} state={STATE_DONE}{_spaced(keys)} "
        f"exit={exit_code} ended={_now()}",
    )


def _spaced(keys: str) -> str:
    """Return evidence keys with their leading separator, empty for none."""
    return f" {keys}" if keys else ""


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
    commands.emit_summary([recorded.line, reporting.status_killed_line(_recorded_level(recorded.line))])
    return EXIT_RUN_LOST


def _recorded_level(line: str) -> FullLevel:
    """Read the objective a recorded status line carried.

    Args:
        line: The recorded status line.

    Returns:
        The ``full=`` level of the line, ``none`` when it carries none or an
        unknown value, so the relaunch never invents a level.
    """
    match = _FULL_RE.search(line)
    level = level_from_token(match.group(1)) if match else None
    return FullLevel.NONE if level is None else level


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
    label = progress.sub_label(invocation)
    write_running(invocation.root, label, evidence.for_invocation(invocation).running_keys())
    code, keys = EXIT_SETUP_ERROR, ""
    try:
        outcome = _dispatch(invocation, deps)
        code, keys = outcome.code, outcome.evidence.closing_keys()
    finally:
        write_done(invocation.root, label, code, keys)
    return code


def _dispatch(invocation: Invocation, deps: Deps) -> RunOutcome:
    """Route one run subcommand to its executor.

    ``init`` and ``status`` never reach this: the CLI routes them
    outside the lifecycle bracket.

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The executor's outcome: exit code and evidence.
    """
    if invocation.sub == runner.SUB_CHECK:
        code = commands.run_check(invocation, deps)
        return evidence.RunOutcome(code, evidence.for_invocation(invocation))
    if invocation.sub == runner.SUB_DAY:
        return day.walk(invocation, deps)
    return commands.run_tests_outcome(invocation, deps)


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
