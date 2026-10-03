"""The detached ghog day walk: a survivor process polled through ghog status (Q32).

Fix (v0.13.0 full_suite_levels, Step 4): Detach a walk with explicit whole scope or a bound group capture before spawn.

``ghog day --detach`` spawns the walk as a survivor process — a hidden
console, broken away from the harness job object when allowed — wired by the
tool itself to ``a.ghog.log`` (the parked senv preamble folded in first), and
acknowledges with exit 6 once the child has written its first status line.

Fix: the survivor used to start with DETACHED_PROCESS — no console at all — so
its console children (check.bat, pytest) allocated a fresh visible console
window on the user's desktop for the whole walk. CREATE_NO_WINDOW gives the
survivor a hidden console those children inherit: a detached walk no longer
pops any window.

Fix (v0.13.0 full_suite_levels, Step 2): split out of ``status.py``, which the
status evidence keys took past the 550-line extraction trigger of the plan;
``status.py`` keeps the ``a.ghog.status`` contract, the ``ghog status``
reporter, the live-run refusal and the lifecycle bracket. The detached walk
now forwards ``--full=<level>`` only when the level came from the parameter,
and relies on the inherited environment otherwise, so the survivor resolves
the same level from the same source.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final

from tools.groundhog import commands, redirect, reporting, runner, scope, status
from tools.groundhog.levels import LevelSource, level_selector
from tools.groundhog.models import EXIT_RUN_LIVE, EXIT_SETUP_ERROR
from tools.scope_capture import ScopeKind

if TYPE_CHECKING:
    from typing import TextIO

    from tools.groundhog.context import Deps, Invocation

# The detach handshake: how many short naps the launcher waits for the
# survivor's first a.ghog.status write before calling it silent.
_HANDSHAKE_TRIES: Final = 50
_HANDSHAKE_PAUSE_SECONDS: Final = 0.2


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
    status.clear_status(invocation.root)
    try:
        pid = deps.detach_factory(
            _detached_day_command(invocation),
            invocation.root / redirect.LOG_NAME,
            preamble,
            invocation.root,
        )
    except (OSError, ValueError) as error:
        commands.emit_summary([f"ghog: detached walk failed to start: {error}"])
        return EXIT_SETUP_ERROR
    for _ in range(_HANDSHAKE_TRIES):
        if status.read_status(invocation.root) is not None:
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

    A level selected by ``--full`` is forwarded as is; a level from
    ``GHOG_FULL`` or the default is not, since the survivor inherits the
    launching environment and so resolves the same level from the same
    source.

    Args:
        invocation: The parsed invocation carrying root, force and level.

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
    if invocation.level is not None and invocation.level_source is LevelSource.PARAM:
        command.append(level_selector(invocation.level))
    if invocation.scope.kind is ScopeKind.GROUP:
        command.append(f"--scope-file={scope.write_detach_capture(invocation.root, invocation.scope)}")
    else:
        command.append("--whole-suite")
    return command


# eof
