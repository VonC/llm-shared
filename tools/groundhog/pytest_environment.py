"""Prepare every pytest child while preserving project and spawn boundaries.

Binding validation also runs at invocation setup, before checks, detached
launches and proof reuse. The shared builder owns activation; this adapter
combines its delta with groundhog's coverage and worker settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from tools import pytest_plugin_environment as environment
from tools.groundhog import group_coverage, runner

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from tools.groundhog.context import Deps, Invocation

_PYTEST_COMMANDS = frozenset(("day", "full", "affected", "single", "timings"))
_INPUTS = (environment.SELECTION, environment.ROOT, environment.POLICY_DIR,
           "PYTHONPATH", "PYTEST_ADDOPTS", "LOCALAPPDATA")
PreparationError = environment.PreparationError


def validate_binding(root: Path, lookup: Callable[[str], str | None]) -> None:
    """Reject another project's whole normalized root, including nested roots."""
    bound = lookup(environment.ROOT)
    if bound and os.path.normcase(str(Path(bound).resolve())) != os.path.normcase(str(root.resolve())):
        message = (f"pytest shell is bound to {bound}; target project is {root}. "
                   f"Run the target project's environment setup: {root / 'senv.bat'}")
        raise PreparationError(message)


def validate_invocation(invocation: Invocation, deps: Deps) -> None:
    """Check pytest-capable invocations before any dispatch or detached launch."""
    if invocation.sub in _PYTEST_COMMANDS:
        validate_binding(invocation.root, deps.environ)


def prepare(root: Path, inherited: Mapping[str, str]) -> dict[str, str]:
    """Use this checkout's live shared sources without importing their bodies."""
    return environment.prepare_environment(root, Path(__file__).resolve().parents[2], inherited)


def child_environment(
    invocation: Invocation, deps: Deps, measure: tuple[Path, float] | None = None, *, parallel: bool = False,
) -> dict[str, str | None]:
    """Return spawn-only activation, removals, coverage and bounded workers.

    Only inputs owned/read by the shared builder need copying; unrelated
    variables stay inherited by the process factory. An I/O preparation error
    is a setup failure, distinct from an unavailable collection child.
    """
    validate_binding(invocation.root, deps.environ)
    inherited = {name: value for name in _INPUTS if (value := deps.environ(name)) is not None}
    try:
        prepared = deps.prepare_pytest(invocation.root, inherited)
    except OSError as error:
        message = f"pytest environment preparation failed: {error}"
        raise PreparationError(message) from error
    overrides: dict[str, str | None] = {
        name: prepared.get(name) for name in inherited.keys() | prepared.keys()
        if inherited.get(name) != prepared.get(name)
    }
    if measure is not None:
        overrides.update(group_coverage.environment(measure[0]))
    overrides.update(runner.worker_environment(
        deps.environ, parallel=parallel and invocation.sub == runner.SUB_FULL, cpu_count=os.cpu_count(),
    ))
    return overrides


# eof
