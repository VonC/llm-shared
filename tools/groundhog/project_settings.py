"""Read pytest collection and coverage settings used to resolve group membership.

One Settings load reads each candidate file at most once. The public accessors
serve callers needing a single setting; group listing shares one load across
all groups. Missing or malformed optional configuration falls back as the
coverage-gate reader historically does.
"""

from __future__ import annotations

import configparser
import contextlib
import shlex
import tomllib
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path


def dict_get(mapping: object, key: str) -> object | None:
    """Read a TOML table key while tolerating non-table values.

    Args:
        mapping: A candidate TOML table.
        key: The key to look up.

    Returns:
        Its value, or None for an absent table or key.
    """
    if not isinstance(mapping, dict):
        return None
    return cast("dict[str, object]", mapping).get(key)


@dataclass(frozen=True)
class Settings:
    """Collection and coverage options shared by one group-resolution phase."""

    python_files: tuple[str, ...] = ("test_*.py", "*_test.py")
    omit: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    branch: bool = False

    @classmethod
    def load(cls, root: Path) -> Settings:
        """Read project settings once, preserving explicit empty settings."""
        toml = _toml(root)
        ini = {name: _ini(root / name) for name in ("pytest.ini", ".coveragerc", "setup.cfg", "tox.ini")}
        pytest_table = dict_get(dict_get(toml, "pytest"), "ini_options")
        pytest_options = _pytest_options(ini, pytest_table)
        coverage = dict_get(dict_get(toml, "coverage"), "run")
        candidates: tuple[object, ...] = (coverage, ini[".coveragerc"].get("run"),
                                        ini["setup.cfg"].get("coverage:run"), ini["tox.ini"].get("coverage:run"))
        python = dict_get(pytest_options, "python_files")
        return cls(
            _words(python) if python is not None else cls().python_files,
            _coverage_list(_first(candidates, "omit")), _coverage_list(_first(candidates, "source")),
            str(_first(candidates, "branch")).lower() in ("true", "1", "yes", "on"),
        )


def _toml(root: Path) -> object:
    """Read the optional TOML tool table."""
    with contextlib.suppress(OSError, ValueError):
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        return dict_get(data, "tool")
    return None


def _ini(path: Path) -> dict[str, dict[str, str]]:
    """Read optional INI sections with interpolation disabled."""
    parser = configparser.ConfigParser(interpolation=None)
    with contextlib.suppress(OSError, ValueError, configparser.Error):
        parser.read_string(path.read_text(encoding="utf-8"))
        return {section: dict(parser[section]) for section in parser.sections()}
    return {}


def _pytest_options(ini: dict[str, dict[str, dict[str, str]]], toml: object) -> object:
    """Honor pytest's INI, TOML, tox and setup precedence."""
    if "pytest" in ini["pytest.ini"]:
        return ini["pytest.ini"]["pytest"]
    if isinstance(toml, dict):
        return cast("dict[str, object]", toml)
    return ini["tox.ini"].get("pytest", ini["setup.cfg"].get("tool:pytest", {}))


def _first(candidates: tuple[object, ...], key: str) -> object:
    """Take the first declared option, including an explicit empty list."""
    for candidate in candidates:
        value = dict_get(candidate, key)
        if value is not None:
            return value
    return None


def _words(value: object) -> tuple[str, ...]:
    """Read TOML arrays or INI whitespace/newline-separated options."""
    if isinstance(value, list):
        return tuple(item for item in cast("list[object]", value) if isinstance(item, str))
    if isinstance(value, str):
        with contextlib.suppress(ValueError):
            return tuple(shlex.split(value, comments=True))
    return ()


def _coverage_list(value: object) -> tuple[str, ...]:
    """Preserve path spaces and backslashes in coverage comma/newline lists."""
    if isinstance(value, str):
        return tuple(part.strip() for part in value.replace("\n", ",").split(",") if part.strip())
    return _words(value)


def python_files(root: Path) -> tuple[str, ...]:
    """Return the configured pytest filename patterns or pytest defaults."""
    return Settings.load(root).python_files


def coverage_omit(root: Path) -> tuple[str, ...]:
    """Return the configured coverage run omissions."""
    return Settings.load(root).omit


def coverage_sources(root: Path) -> tuple[str, ...]:
    """Return coverage sources for subsequent group measurement."""
    return Settings.load(root).sources


def coverage_branch(root: Path) -> bool:
    """Return whether coverage measures branches."""
    return Settings.load(root).branch


# eof
