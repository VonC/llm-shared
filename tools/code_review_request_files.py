"""Validate and read caller-owned review inputs; write their paired outputs."""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from tools.review_artifact_configuration import caller_file_parents
from tools.review_exchange_models import ReviewExchangeError


def is_effectively_ignored(project_root: Path, path: Path) -> bool:
    """Ask Git whether one exact caller-owned root path is ignored."""
    git_executable = shutil.which("git")
    if git_executable is None:
        raise ReviewExchangeError("cannot validate ignored file: git was not found")
    try:
        result = subprocess.run(  # noqa: S603 - fixed Git executable and arguments
            [
                git_executable,
                "-C",
                str(project_root),
                "check-ignore",
                "-q",
                "--",
                str(path.relative_to(project_root)),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise ReviewExchangeError(f"cannot validate ignored file: {error}") from error
    return result.returncode == 0


def root_file(
    project_root: Path,
    value: str | Path,
    label: str,
    *,
    input_file: bool,
) -> Path:
    """Validate one ignored caller-owned home-local input or output path."""
    path = Path(value).expanduser().resolve()
    if path.parent not in caller_file_parents(project_root):
        raise ReviewExchangeError(f"{label} must be in the review artifact home")
    if not path.name.startswith("a."):
        raise ReviewExchangeError(f"{label} must use an a.* name")
    if input_file and not path.is_file():
        raise ReviewExchangeError(f"{label} does not exist")
    if not input_file and path.exists() and not path.is_file():
        raise ReviewExchangeError(f"{label} must not be a directory")
    if not is_effectively_ignored(project_root, path):
        raise ReviewExchangeError(f"{label} is not effectively ignored")
    return path


def read_utf8(path: Path, label: str) -> str:
    """Read one validated caller-owned input exactly once as UTF-8."""
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            return stream.read()
    except UnicodeError as error:
        raise ReviewExchangeError(f"{label} is not valid UTF-8") from error
    except OSError as error:
        raise ReviewExchangeError(f"cannot read {label}: {error}") from error


def write_utf8(path: Path, content: str, label: str) -> None:
    """Write one validated caller-owned output in one UTF-8 operation."""
    try:
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    except OSError as error:
        raise ReviewExchangeError(f"cannot write {label}: {error}") from error


# eof
