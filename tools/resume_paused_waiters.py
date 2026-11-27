"""Observe shared exchange waiter processes through the current OS process table."""

from __future__ import annotations

from itertools import pairwise
from pathlib import Path
from typing import TYPE_CHECKING

import psutil

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from tools.resume_paused_models import CanonicalRoot


def _wait_command(args: list[str]) -> bool:
    """Identify the shared review CLI and its reviewer wait verb as adjacent arguments."""
    scripts = {"review_exchange_cli.py", "tools.review_exchange_cli"}
    verbs = {"wait-request", "wait-any-request"}
    return any(Path(arg).name.casefold() in scripts and verb in verbs for arg, verb in pairwise(args))


def _process_reason(process: psutil.Process, checkout: Path) -> str:
    """Conservatively include both checkout sources used by review_exchange_cli."""
    if not process.name().lower().startswith(("python", "pypy")):
        return ""
    args = process.cmdline()
    if not args:
        return "reviewer-wait-unknown"
    if not _wait_command(args):
        return ""
    return _checkout_reason(process, checkout)


def _checkout_reason(process: psutil.Process, checkout: Path) -> str:
    """Attribute the wait to its working directory and configured project root."""
    cwd = Path(process.cwd()).resolve()
    if cwd.is_relative_to(checkout):
        return "reviewer-wait-active"
    project = process.environ().get("PRJ_DIR")
    if project and Path(project).resolve() == checkout:
        return "reviewer-wait-active"
    if not any((parent / ".git").exists() for parent in (cwd, *cwd.parents)) and not (project and (Path(project) / ".git").exists()):
        return "reviewer-wait-unknown"
    return ""


def waiter_reason(root: CanonicalRoot, processes: Callable[[], Iterable[psutil.Process]] = psutil.process_iter) -> str:
    """Return a pending reason for an active or unobservable shared reviewer waiter."""
    checkout = Path(root.display)
    try:
        for process in processes():
            try:
                reason = _process_reason(process, checkout)
                if reason:
                    return reason
            except psutil.NoSuchProcess:
                continue
    except (OSError, psutil.Error):
        return "reviewer-wait-unknown"
    return ""


# eof
