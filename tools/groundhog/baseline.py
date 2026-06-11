"""Failure baseline shared between the full and focus runs (Q07, Q18).

``ghog full`` writes the failing test node ids to ``a.ghog.failures`` at the
project root, refreshed on every full run and emptied on a green one.
``ghog single`` reads that baseline to print the Q07 comparison as two named
lists: the tests still failing in focus, and the tests passing in focus but
failing in the full suite (the interaction or ordering suspects).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

# Name of the baseline scratch file at the project root (Q18).
BASELINE_FILE_NAME: Final = "a.ghog.failures"


@dataclass(frozen=True)
class FocusComparison:
    """The two Q07 lists produced by a focus run against the baseline.

    Attributes:
        still_failing: Node ids failing in the focus run, fixed first.
        suspects: Baseline node ids in the focus scope that passed in
            focus — the test interaction or ordering suspects, fixed second.
    """

    still_failing: tuple[str, ...]
    suspects: tuple[str, ...]


def baseline_path(root: Path) -> Path:
    """Return the baseline file path for a project root.

    Args:
        root: The project root directory.

    Returns:
        The ``a.ghog.failures`` path under that root.
    """
    return root / BASELINE_FILE_NAME


def write_baseline(root: Path, failed_ids: Sequence[str]) -> Path:
    """Write the full-run failing node ids, emptying the file on green.

    Args:
        root: The project root directory.
        failed_ids: The failing node ids of the full run, possibly empty.

    Returns:
        The written baseline path.
    """
    path = baseline_path(root)
    content = "".join(f"{node_id}\n" for node_id in failed_ids)
    path.write_text(content, encoding="utf-8")
    return path


def read_baseline(root: Path) -> tuple[str, ...] | None:
    """Read the baseline node ids, or None when no baseline exists.

    Args:
        root: The project root directory.

    Returns:
        The node ids of the last full run (possibly empty when that run
        was green), or ``None`` when no full run wrote a baseline yet.
    """
    path = baseline_path(root)
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    return tuple(line.strip() for line in lines if line.strip())


def failing_files(failed_ids: Sequence[str]) -> tuple[str, ...]:
    """Return the unique test files of failing node ids, in order.

    Args:
        failed_ids: Failing node ids, such as ``tests/test_a.py::test_x``.

    Returns:
        The unique file parts, first occurrence order preserved.
    """
    seen: dict[str, None] = {}
    for node_id in failed_ids:
        seen.setdefault(_file_part(node_id), None)
    return tuple(seen)


def compare_focus(
    baseline_ids: Sequence[str],
    focus_files: Sequence[str],
    focus_failed: Sequence[str],
) -> FocusComparison:
    """Compare a focus run with the full-run baseline per node id (Q07).

    Args:
        baseline_ids: The failing node ids of the last full run.
        focus_files: The test files the focus run was called with.
        focus_failed: The node ids failing in the focus run.

    Returns:
        The two named lists: still failing in focus, and passing in focus
        but failing in the full suite.
    """
    failed_now = {_normalize(node_id) for node_id in focus_failed}
    suspects = tuple(
        node_id
        for node_id in baseline_ids
        if _in_focus_scope(node_id, focus_files)
        and _normalize(node_id) not in failed_now
    )
    return FocusComparison(still_failing=tuple(focus_failed), suspects=suspects)


def _in_focus_scope(node_id: str, focus_files: Sequence[str]) -> bool:
    """Tell whether a baseline node id belongs to the focused files.

    Args:
        node_id: One baseline node id.
        focus_files: The test files the focus run was called with.

    Returns:
        True when the node id file part matches one focused file.
    """
    file_part = _file_part(node_id)
    return any(_same_file(file_part, _normalize(focus)) for focus in focus_files)


def _same_file(file_part: str, focus_file: str) -> bool:
    """Match a node id file part against a focused file path.

    Args:
        file_part: The normalized file part of a node id.
        focus_file: The normalized focused file path.

    Returns:
        True when both name the same file, whatever the path prefix.
    """
    return (
        file_part == focus_file
        or file_part.endswith(f"/{focus_file}")
        or focus_file.endswith(f"/{file_part}")
    )


def _file_part(node_id: str) -> str:
    r"""Return the normalized file part of a node id.

    Args:
        node_id: A node id such as ``tests\test_a.py::test_x``.

    Returns:
        The file part with forward slashes.
    """
    return _normalize(node_id.split("::", 1)[0])


def _normalize(path_text: str) -> str:
    """Normalize a path-like text to forward slashes.

    Args:
        path_text: A path or node id in either separator style.

    Returns:
        The same text with forward slashes only.
    """
    return path_text.replace("\\", "/")


# eof
