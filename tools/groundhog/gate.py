"""Coverage gate resolution for groundhog (Q14).

The gate is the ``fail_under`` value the project already declares in its
coverage configuration — ``pyproject.toml`` first, then ``.coveragerc``,
then ``setup.cfg`` — with a default of 100 when no file declares one. The
tool never demands more than the project's own gate.
"""

from __future__ import annotations

import configparser
import contextlib
import tomllib
from typing import TYPE_CHECKING, Final, cast

if TYPE_CHECKING:
    from pathlib import Path

# The gate applied when no project configuration declares one (Q14).
DEFAULT_COVERAGE_GATE: Final = 100.0
# The coverage option carrying the gate.
_FAIL_UNDER: Final = "fail_under"


def read_coverage_gate(root: Path) -> float:
    """Return the project coverage gate, default 100 (Q14).

    Args:
        root: The project root directory.

    Returns:
        The ``fail_under`` value of the first configuration file that
        declares one, or ``DEFAULT_COVERAGE_GATE``.
    """
    readers = (
        _from_pyproject(root),
        _from_ini(root / ".coveragerc", "report"),
        _from_ini(root / "setup.cfg", "coverage:report"),
    )
    for value in readers:
        if value is not None:
            return value
    return DEFAULT_COVERAGE_GATE


def _from_pyproject(root: Path) -> float | None:
    """Read the gate from ``[tool.coverage.report]`` in pyproject.toml.

    Args:
        root: The project root directory.

    Returns:
        The declared gate, or ``None`` when absent or unreadable.
    """
    path = root / "pyproject.toml"
    if not path.is_file():
        return None
    with contextlib.suppress(OSError, tomllib.TOMLDecodeError):
        data: dict[str, object] = tomllib.loads(path.read_text(encoding="utf-8"))
        report = _dict_get(_dict_get(data.get("tool"), "coverage"), "report")
        return _as_gate(_dict_get(report, _FAIL_UNDER))
    return None


def _dict_get(mapping: object, key: str) -> object | None:
    """Read one key of a TOML table, tolerating any non-table value.

    Args:
        mapping: The candidate table, of any TOML type.
        key: The key to read.

    Returns:
        The value, or ``None`` when the candidate is not a table or has
        no such key.
    """
    if not isinstance(mapping, dict):
        return None
    return cast("dict[str, object]", mapping).get(key)


def _from_ini(path: Path, section: str) -> float | None:
    """Read the gate from one ini-style coverage configuration file.

    Args:
        path: The candidate configuration file.
        section: The section carrying the coverage report options.

    Returns:
        The declared gate, or ``None`` when absent or unreadable.
    """
    if not path.is_file():
        return None
    config = configparser.ConfigParser()
    with contextlib.suppress(OSError, configparser.Error):
        config.read_string(path.read_text(encoding="utf-8"))
        if config.has_option(section, _FAIL_UNDER):
            return _as_gate(config.get(section, _FAIL_UNDER))
    return None


def _as_gate(value: object) -> float | None:
    """Convert a configuration value to a gate percentage.

    Args:
        value: The raw ``fail_under`` value, of any configuration type.

    Returns:
        The value as a float, or ``None`` when it is not a number.
    """
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        with contextlib.suppress(ValueError):
            return float(value)
    return None


# eof
