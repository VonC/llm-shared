"""Self-redirect guard for unredirected LLM runs (Q31).

The invocation contract sends every LLM-driven ghog call through a
caller-side redirect to ``a.ghog.log``. A caller that forgets it streams
the senv preamble, the check.bat output and the whole pytest run into
its own context window, and a harness timeout loses the report
entirely. The guard closes that hole: when stdout is a harness capture
— a pipe, or a regular file that is not ``a.ghog.log`` itself (some
harnesses capture into a temp file) — the full report is written to
``a.ghog.log`` at the project root and only the envelope reaches the
captured stdout: a notice naming the log, then the next-step and
closing lines mirrored by ``commands.emit_summary``. The caller still
branches on the exit code and the next-step message without one
unbounded line landing in its context. A stdout that already is the
project's ``a.ghog.log`` — the caller-side redirect of the contract —
streams as before: it lands in the log either way.

The senv.bat preamble of ``ghog.bat`` streams before this process
exists, so the wrapper parks it in the side file named by the
``GHOG_SENV_LOG`` environment variable; :func:`replay_senv_log` folds
it back into the report stream — stdout normally, ``a.ghog.log`` when
the guard armed — and deletes it. A side file still present after the
python call tells ghog.bat this process never ran, and the wrapper
types it itself so the sandbox-block markers stay visible.

Fix: the side-log consumption is split out as :func:`consume_senv_log`
so the Q32 paths can reuse it — the detach launcher folds the preamble
into the log it opens for the survivor child, and the status reporter
discards it to keep its envelope bounded — and :func:`disarm` drops a
mirror left armed by an earlier in-process run, since those paths never
call :func:`activate_if_captured` themselves.
"""

from __future__ import annotations

import contextlib
import logging
import os
import re
import stat
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final

from tools.groundhog.models import Mode

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import TextIO

LOGGER = logging.getLogger("groundhog")

# The report log of the guard, the same file as the caller-side redirect.
LOG_NAME: Final = "a.ghog.log"
# The environment variable naming the senv side log parked by ghog.bat.
SENV_LOG_ENV: Final = "GHOG_SENV_LOG"
# The envelope notice naming the log on the captured stdout.
MSG_SELF_REDIRECT: Final = (
    "ghog: stdout not redirected - full report written to a.ghog.log; "
    "read only its tail (Q31)"
)
# ANSI escape sequences from colored senv.bat output, stripped before replay so
# in-process LLM runs and tests see the same plain report stream as check lines.
_ANSI_ESCAPE_RE: Final = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# The captured stdout mirrored by emit_summary, None while inactive.
_summary: TextIO | None = None


def stdout_is_captured(root: Path) -> bool:
    """Tell whether stdout is a harness capture instead of the log.

    A terminal keeps user mode (Q03), so only captured streams reach
    this probe in practice: a pipe always arms the guard, and a regular
    file arms it too unless it is the project's ``a.ghog.log`` itself —
    the caller-side redirect of the contract, where streaming already
    lands in the log.

    Args:
        root: The consuming project root, hosting ``a.ghog.log``.

    Returns:
        True when stdout is a pipe or a capture file, False otherwise —
        including streams without a real file descriptor, such as test
        captures, and character devices such as a console or NUL.
    """
    try:
        fd = sys.stdout.fileno()
    except (AttributeError, OSError, ValueError):
        return False
    try:
        stdout_stat = os.fstat(fd)
    except OSError:
        return False
    if stat.S_ISFIFO(stdout_stat.st_mode):
        return True
    if not stat.S_ISREG(stdout_stat.st_mode):
        return False
    return not _is_the_log_file(stdout_stat, root / LOG_NAME)


def _is_the_log_file(stdout_stat: os.stat_result, log_path: Path) -> bool:
    """Tell whether a stat result points at the project log file.

    Args:
        stdout_stat: The fstat result of the stdout file descriptor.
        log_path: The ``a.ghog.log`` path at the project root.

    Returns:
        True when both name the same file (device and inode match).
    """
    try:
        log_stat = log_path.stat()
    except OSError:
        return False
    return (stdout_stat.st_dev, stdout_stat.st_ino) == (
        log_stat.st_dev,
        log_stat.st_ino,
    )


def activate_if_captured(mode: Mode, root: Path) -> bool:
    """Arm the guard when an LLM run streams into a harness capture.

    Args:
        mode: The picked output mode (Q03).
        root: The consuming project root, hosting ``a.ghog.log``.

    Returns:
        True when the guard armed: the report now goes to the log and
        the envelope lines mirror to the captured stdout. False in user
        mode, on a stdout already redirected to the log, or when the
        log cannot be opened — the run then streams as before.
    """
    global _summary  # noqa: PLW0603 - the one process-wide guard state
    _summary = None
    if mode is not Mode.LLM or not stdout_is_captured(root):
        return False
    try:
        handler = logging.FileHandler(
            root / LOG_NAME,
            mode="w",
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return False
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    for old_handler in root_logger.handlers:
        old_handler.close()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    _summary = sys.stdout
    mirror([MSG_SELF_REDIRECT])
    return True


def disarm() -> None:
    """Drop the envelope mirror of an earlier in-process run (Q32).

    The status, refusal and detach paths never arm the guard; a mirror
    left armed by a previous :func:`activate_if_captured` call in the
    same process (tests, embedders) must not leak into their bounded
    envelopes.
    """
    global _summary  # noqa: PLW0603 - the one process-wide guard state
    _summary = None


def mirror(lines: Sequence[str]) -> None:
    """Echo envelope lines to the captured stdout of an armed guard.

    Args:
        lines: The notice, next-step and closing lines to echo.
    """
    if _summary is None:
        return
    for line in lines:
        print(line, file=_summary)
    with contextlib.suppress(OSError, ValueError):
        _summary.flush()


def consume_senv_log() -> str:
    """Read and delete the parked senv side log of ghog.bat (Q31, Q32).

    The wrapper parks the senv.bat output in the ``GHOG_SENV_LOG`` file
    because that output streams before this process exists. Deleting it
    tells ghog.bat it was consumed; an unreadable file is left for the
    wrapper to type, so the sandbox-block markers stay visible.

    Returns:
        The side-log text, empty when absent or unreadable.
    """
    path_text = os.environ.get(SENV_LOG_ENV, "")
    if not path_text:
        return ""
    path = Path(path_text)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    with contextlib.suppress(OSError):
        path.unlink()
    return text


def replay_senv_log() -> None:
    """Fold the senv side log of ghog.bat back into the report stream.

    The replay sends the consumed text wherever the report goes —
    stdout normally, ``a.ghog.log`` when the guard armed.
    """
    for line in consume_senv_log().splitlines():
        LOGGER.info("%s", _ANSI_ESCAPE_RE.sub("", line))


# eof
