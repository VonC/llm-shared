"""Count selected tests before a day walk repeats most of its full suite.

Collection uses the project's ordinary pytest configuration and scope, but
never runs fixtures or test bodies. Testmon data collection is disabled in
the affected probe; the full probe disables testmon entirely. Neither probe
resets the dependency map. Unavailable evidence keeps the ordinary walk.

Fix: a probe over a group of a few hundred test files failed to spawn
(``[WinError 206]``), so a large group silently lost its estimate. Each probe
now spawns inside ``args_file.spilled``, which moves the group paths of a
command longer than its budget into an ``@<file>`` argument, in order. An
unusable artifact home for that file also means no estimate.

Step 5 prepares both children; binding and preparation errors stop the walk.
"""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

from tools.groundhog import args_file, pytest_environment, runner

if TYPE_CHECKING:
    from tools.groundhog.context import Deps, Invocation

_COLLECTED = re.compile(r"\bcollected (\d+) items?\b")
_DESELECTED = re.compile(r"\b(\d+) deselected\b")
ENV_PERCENT = "GHOG_AFFECTED_MAX_PERCENT"
DEFAULT_PERCENT = 75.0
DISABLED_PERCENT = 100.0


def threshold(deps: Deps) -> float | None:
    """Return the threshold; 100 disables probes, invalid values fall back."""
    raw = deps.environ(ENV_PERCENT)
    try:
        value = DEFAULT_PERCENT if raw is None else float(raw)
    except ValueError:
        return None
    return value if math.isfinite(value) and 0 <= value <= DISABLED_PERCENT else None


def counts(invocation: Invocation, deps: Deps) -> tuple[int, int] | None:
    """Return affected and full selected counts, or no trustworthy estimate."""
    pytest_environment.validate_binding(invocation.root, deps.environ)
    executable = deps.which("pytest")
    if executable is None or not deps.pytest_project(invocation.root):
        return None
    try:
        total = _collect(invocation, deps, executable, affected=False)
        if total is None or total == 0:
            return None
        affected = _collect(invocation, deps, executable, affected=True)
    except pytest_environment.PreparationError:
        raise
    except (OSError, ValueError):
        return None
    if affected is None or not 0 <= affected <= total:
        return None
    return affected, total


def _collect(invocation: Invocation, deps: Deps, executable: str, *, affected: bool) -> int | None:
    """Count a successful collection header, subtracting ordinary deselection."""
    selected = None

    def receive(line: str) -> None:
        nonlocal selected
        match = _COLLECTED.search(line)
        if match is not None:
            dropped = _DESELECTED.search(line)
            selected = int(match[1]) - (int(dropped[1]) if dropped else 0)

    options = ["--testmon", "--testmon-nocollect"] if affected else ["--no-testmon"]
    command = [executable, "--collect-only", "--no-cov", "--no-header", "--color=no", "-v",
               *options, *invocation.scope.test_files]
    with args_file.spilled(command, frozenset(invocation.scope.test_files), invocation.root) as spawned:
        config = runner.StreamConfig(
            command=spawned,
            cwd=invocation.root,
            popen_factory=deps.popen_factory,
            env_overrides=pytest_environment.child_environment(invocation, deps),
        )
        code = runner.run_streaming(config, receive)
    return selected if code in (0, 5) else None


# eof
