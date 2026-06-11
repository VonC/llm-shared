"""Wrap-list config discovery of the wrap-commit tool.

Finds and reads the ``wrap-list.backtick`` files whose lines are extra
string literals to backtick in commit bodies: the wrap tool's own
folder, the calling folder and every parent up to and including the
project root, and the user home folder are scanned in that order. See
``tools.wrap_commit`` for the full tool description.

Fix: split for the repo line budget -- the wrap-list search and load
helpers moved here from ``tools.wrap_commit``, which stays the script
entry point and import hub.
"""

from __future__ import annotations

import os
from pathlib import Path

from tools import find_project_root

# Config file name whose lines are extra string literals to backtick in
# commit bodies. Searched in the tool folder, the calling folder and its
# parents up to the project root, and the user home folder.
WRAP_LIST_FILE_NAME = "wrap-list.backtick"


def _wrap_list_search_dirs(
    tool_dir: Path,
    start_dir: Path,
    project_root: Path,
    home: Path,
) -> list[Path]:
    """Return the ordered, de-duplicated dirs to scan for wrap-list files.

    The order is: the wrap tool's own folder, then the calling folder and
    each parent up to and including the project root, then the project
    root, then the user home folder. The walk also stops at the
    filesystem root, so a calling folder that is not under the project
    root still terminates. Duplicates are dropped while keeping the first
    occurrence, so a directory that plays several of these roles is
    scanned once.

    Args:
        tool_dir: The folder that holds this wrap tool.
        start_dir: The calling folder (already resolved).
        project_root: The resolved project root.
        home: The resolved user home folder.

    Returns:
        The de-duplicated directories to scan, in scan order.
    """
    candidates: list[Path] = [tool_dir]
    current = start_dir
    while True:
        candidates.append(current)
        parent = current.parent
        # Stop at the project root, or at the filesystem root when the
        # calling folder is not under the project root.
        if current in (project_root, parent):
            break
        current = parent
    candidates.append(project_root)
    candidates.append(home)

    ordered: list[Path] = []
    seen: set[Path] = set()
    for directory in candidates:
        if directory not in seen:
            seen.add(directory)
            ordered.append(directory)
    return ordered


def _load_wrap_list_literals(directories: list[Path]) -> list[str]:
    """Read every ``wrap-list.backtick`` found across ``directories``.

    Each file contributes one literal per non-blank line, with leading
    and trailing whitespace stripped. The literals from all files are
    concatenated in directory order. A directory without the file is
    skipped, and a file that cannot be read is skipped too, so one
    unreadable config never aborts the format.

    Args:
        directories: The folders to scan, in scan order.

    Returns:
        The concatenated list of literal strings.
    """
    literals: list[str] = []
    for directory in directories:
        path = directory / WRAP_LIST_FILE_NAME
        try:
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if stripped:
                literals.append(stripped)
    return literals


def collect_wrap_list_literals(start_dir: Path) -> list[str]:
    """Gather wrap-list literals visible from ``start_dir``.

    Scans the wrap tool folder, the calling folder and its parents up to
    the project root, the project root, and the user home folder. The
    home folder is taken from the ``HOME`` environment variable when it
    is set (matching ``%HOME%`` / ``$HOME``), otherwise from the OS home
    (``Path.home()``). When the project root cannot be located, the
    search falls back to the calling folder as the upper bound, so the
    tool folder, the calling folder and its parents, and the home folder
    are still scanned.

    Args:
        start_dir: The calling folder (typically the current directory).

    Returns:
        The concatenated wrap-list literals, possibly empty.
    """
    tool_dir = Path(__file__).resolve().parent
    home_env = os.environ.get("HOME")
    home = Path(home_env).resolve() if home_env else Path.home()
    resolved_start = start_dir.resolve()
    try:
        project_root = find_project_root(start_dir).resolve()
    except (FileNotFoundError, OSError, ValueError):
        project_root = resolved_start
    directories = _wrap_list_search_dirs(
        tool_dir, resolved_start, project_root, home,
    )
    return _load_wrap_list_literals(directories)


# eof
