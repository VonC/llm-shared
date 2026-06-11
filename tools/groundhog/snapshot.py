"""Source snapshot behind the ghog day noop (Q28).

A fully green ``ghog day`` walk records a digest of the project's Python
files (plus the gate configuration files) into ``a.ghog.day.ok`` at the
project root. The next walk recomputes the digest first: when nothing
changed, the walk is a noop — chained instructions that each call the
walk (implement-missing-step routing through split-large-file, for
example) pay for it once. Any file change, addition or removal moves the
digest and the walk runs again; ``--force`` overrides the marker.

The digest reads file paths, sizes and mtimes only (no content), so it
stays fast on large trees; unreadable files are skipped, which biases
toward re-walking, never toward a wrong noop.
"""

from __future__ import annotations

import contextlib
import hashlib
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path

# The marker written by a green ghog day walk (Q28).
MARKER_FILE_NAME: Final = "a.ghog.day.ok"
# Folders never part of the source snapshot.
_EXCLUDED_DIRS: Final = frozenset(
    {
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "htmlcov",
        "node_modules",
        "venv",
        "venvs",
    },
)
# Non-Python files that move the gates, part of the snapshot.
_CONFIG_FILES: Final = ("pyproject.toml", ".coveragerc", "setup.cfg", "check.bat")


def marker_path(root: Path) -> Path:
    """Return the day marker path for a project root.

    Args:
        root: The project root directory.

    Returns:
        The ``a.ghog.day.ok`` path under that root.
    """
    return root / MARKER_FILE_NAME


def source_digest(root: Path) -> str:
    """Digest the project's Python files and gate configuration.

    Args:
        root: The project root directory.

    Returns:
        A hex digest over the sorted (path, mtime, size) of every
        Python file outside the excluded folders, plus the gate
        configuration files; unreadable files are skipped.
    """
    hasher = hashlib.sha256()
    for path in _source_files(root):
        with contextlib.suppress(OSError):
            stat = path.stat()
            rel = path.relative_to(root).as_posix()
            hasher.update(f"{rel}|{stat.st_mtime_ns}|{stat.st_size}\n".encode())
    return hasher.hexdigest()


def write_marker(root: Path) -> Path:
    """Record the current source digest after a green walk (Q28).

    Args:
        root: The project root directory.

    Returns:
        The written marker path.
    """
    path = marker_path(root)
    path.write_text(f"{source_digest(root)}\n", encoding="utf-8")
    return path


def is_unchanged(root: Path) -> bool:
    """Tell whether the source matches the last green walk (Q28).

    Args:
        root: The project root directory.

    Returns:
        True when the marker exists and the recomputed digest matches;
        False without a marker, on a mismatch, or on an unreadable
        marker (the safe direction is to walk again).
    """
    path = marker_path(root)
    if not path.is_file():
        return False
    with contextlib.suppress(OSError, UnicodeDecodeError):
        recorded = path.read_text(encoding="utf-8").strip()
        return recorded == source_digest(root)
    return False


def _source_files(root: Path) -> list[Path]:
    """List the snapshot files, sorted for a stable digest.

    Args:
        root: The project root directory.

    Returns:
        The Python files outside the excluded folders, plus the gate
        configuration files that exist.
    """
    files = [
        path
        for path in root.rglob("*.py")
        if not _excluded(path, root)
    ]
    files.extend(
        root / name for name in _CONFIG_FILES if (root / name).is_file()
    )
    return sorted(files)


def _excluded(path: Path, root: Path) -> bool:
    """Tell whether a file sits under an excluded folder.

    Args:
        path: The candidate file.
        root: The project root directory.

    Returns:
        True when any parent folder below the root is excluded.
    """
    return any(
        part in _EXCLUDED_DIRS for part in path.relative_to(root).parts[:-1]
    )


# eof
