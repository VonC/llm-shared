"""Repair activation scaffolding without replacing a live venv interpreter."""

from __future__ import annotations

import logging
import os
import sys
import venv
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


LOGGER = logging.getLogger(__name__)


class VenvScaffoldError(RuntimeError):
    """Raised when the standard-library repair leaves required files missing."""


def _required_paths(env_dir: Path) -> tuple[Path, Path, Path]:
    """Return the configuration, interpreter, and activation paths."""
    scripts_dir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python_name = "python.exe" if os.name == "nt" else "python"
    activate_name = "activate.bat" if os.name == "nt" else "activate"
    return env_dir / "pyvenv.cfg", scripts_dir / python_name, scripts_dir / activate_name


def repair_scaffold(env_dir: Path) -> tuple[Path, ...]:
    """Restore missing venv files while preserving an existing interpreter."""
    required = _required_paths(env_dir)
    missing_before = tuple(path for path in required if not path.is_file())
    if not missing_before:
        return ()

    builder = venv.EnvBuilder(with_pip=False, clear=False)
    context = builder.ensure_directories(str(env_dir))
    builder.create_configuration(context)
    if not required[1].is_file():
        builder.setup_python(context)
    builder.setup_scripts(context)

    missing_after = tuple(path for path in required if not path.is_file())
    if missing_after:
        missing = ", ".join(path.name for path in missing_after)
        msg = f"venv scaffold repair left required files missing: {missing}"
        raise VenvScaffoldError(msg)
    return missing_before


def main(argv: Sequence[str] | None = None) -> int:
    """Repair the one venv path supplied by ``senv.bat``."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        msg = "usage: repair_venv_scaffold.py VENV_DIR"
        raise SystemExit(msg)
    env_dir = Path(arguments[0]).resolve()
    try:
        repaired = repair_scaffold(env_dir)
    except (OSError, VenvScaffoldError):
        LOGGER.exception("Venv scaffold repair failed")
        return 1
    names = ", ".join(path.name for path in repaired) or "nothing"
    LOGGER.info("Venv scaffold repair completed: %s", names)
    return 0


if __name__ == "__main__":  # pragma: no cover - batch entry point
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
