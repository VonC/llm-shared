"""Share strict parsing, path, and Git primitives for code-review evidence.

The evidence hub and validation-state module use this single boundary so path
containment, digest validation, and Git error handling cannot drift apart.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from tools.git_command import GitCommandOptions, run_cross_platform_git_command
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Iterable

TREE_OBJECT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def payload_path(value: object, label: str) -> str:
    """Return one canonical repository-relative path from retained JSON."""
    if not isinstance(value, str) or not value:
        raise ReviewExchangeError(f"{label} is invalid")
    normalized = PurePosixPath(value.replace("\\", "/"))
    unsafe = (
        normalized.is_absolute()
        or normalized == PurePosixPath(".")
        or ".." in normalized.parts
        or re.match(r"^[A-Za-z]:", value) is not None
    )
    if unsafe:
        raise ReviewExchangeError(f"{label} must be repository-relative")
    return normalized.as_posix()


def unique_paths(values: Iterable[object], label: str) -> tuple[str, ...]:
    """Return unique canonical paths while preserving caller order."""
    paths = tuple(payload_path(value, label) for value in values)
    if len(set(paths)) != len(paths):
        raise ReviewExchangeError(f"{label} contains duplicate paths")
    return paths


def repository_root(repository: str | Path) -> Path:
    """Return an existing repository directory used by evidence operations."""
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ReviewExchangeError("repository is not a directory")
    return root


def run_git_evidence(
    root: Path,
    arguments: tuple[str, ...],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run one bounded Git evidence command through the shared adapter."""
    try:
        return run_cross_platform_git_command(
            arguments,
            cwd=root,
            options=GitCommandOptions(
                check=check,
                capture_output=True,
                encoding="utf-8",
            ),
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ReviewExchangeError(f"Git evidence command failed: {error}") from error


def relative_path(root: Path, value: str | Path) -> tuple[str, Path]:
    """Resolve one file operand while keeping it inside the repository."""
    supplied = Path(value)
    if supplied.is_absolute():
        raise ReviewExchangeError("evidence path must be repository-relative")
    candidate = (root / supplied).resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ReviewExchangeError("evidence path must be repository-relative") from error
    if not relative.parts:
        raise ReviewExchangeError("evidence path must name a file")
    return relative.as_posix(), candidate


__all__ = [
    "SHA256_RE",
    "TREE_OBJECT_RE",
    "payload_path",
    "relative_path",
    "repository_root",
    "run_git_evidence",
    "unique_paths",
]


# eof
