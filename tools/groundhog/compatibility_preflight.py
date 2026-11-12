"""Obtain fresh executable evidence from the declared project, before proof reuse.

The declaration contains only a literal applicability boolean. The target
checkout owns the fixed entrypoint, environment and dependency manifest.
Consumers without a declaration acquire no compatibility prerequisites.
Compatibility failures have a dedicated type for narrow CLI setup handling.
"""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, cast

from tools.groundhog import pytest_environment, runner

if TYPE_CHECKING:
    from pathlib import Path

    from tools.groundhog.context import Deps

_TABLE = "lifecycle-compatibility"


class CompatibilityError(ValueError):
    """Identify invalid declarations or unsuccessful executable evidence."""


def _enabled(data: object) -> bool:
    """Validate every table boundary and the optional literal applicability flag."""
    for key in ("tool", "llm-shared", _TABLE):
        if not isinstance(data, dict):
            raise TypeError
        table = cast("dict[str, object]", data)
        if key not in table:
            return False
        data = table[key]
    if not isinstance(data, dict):
        raise TypeError
    declaration = cast("dict[str, object]", data)
    enabled = declaration.get("enabled", False)
    if type(enabled) is not bool:
        raise TypeError
    return enabled


def entrypoint(root: Path) -> Path | None:
    """Parse strict applicability and resolve only the fixed local launcher."""
    path = root / "pyproject.toml"
    if not path.exists():
        return None
    try:
        enabled = _enabled(tomllib.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError) as error:
        message = f"{_TABLE}: malformed declaration in {path}; require literal boolean enabled"
        raise CompatibilityError(message) from error
    if not enabled:
        return None
    entry = root / "bin" / "lifecycle_compatibility.bat"
    if not entry.is_file():
        message = f"{_TABLE}: enabled project is missing {entry}"
        raise CompatibilityError(message)
    return entry


def run(root: Path, deps: Deps) -> None:
    """Reject foreign bindings first; execute fresh evidence without caching."""
    pytest_environment.validate_binding(root, deps.environ)
    entry = entrypoint(root)
    if entry is None:
        return
    config = runner.StreamConfig(
        command=["cmd.exe", "/d", "/c", str(entry)], cwd=root,
        popen_factory=deps.popen_factory,
    )
    code = runner.run_streaming(config, print)
    if code:
        message = f"{_TABLE}: fresh executable preflight failed (exit={code}); run {entry}"
        raise CompatibilityError(message)


# eof
