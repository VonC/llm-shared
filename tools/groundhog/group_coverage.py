"""Measure exact group sources from fresh, isolated coverage evidence.

The coverage API retains project branch and omit settings. Explicit morfs
include sources outside the configured source folders and never-executed files.
The child's TOTAL and project fail-under threshold do not decide this gate.
Unusable sources fail evidence validation even when reports normally ignore errors.
Coverage data is closed even when corrupt input fails while opening its database.
"""

from __future__ import annotations

import io
import time
from contextlib import chdir, closing
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from coverage import Coverage
from coverage.exceptions import CoverageException

from tools.artifact_home import artifact_path
from tools.linear_order import ordered_strings

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.scope_capture import ResolvedScope


@dataclass(frozen=True)
class GroupCoverage:
    """A group percentage and gap rows, or a named unusable-evidence error."""

    percent: float | None
    gap_rows: tuple[str, ...] = ()
    error: str = ""


def cov_folders(sources: Sequence[str]) -> tuple[str, ...]:
    """Reduce containing folders by a prefix scan in linear total path size."""
    folders = {str(PurePosixPath(source).parent) for source in sources}
    if "." in folders:
        return (".",)
    kept: list[str] = []
    ancestor = ""
    for folder in ordered_strings(folder + "/" for folder in folders):
        if not ancestor or not folder.startswith(ancestor):
            kept.append(folder[:-1])
            ancestor = folder
    return tuple(kept)


def data_file(root: Path, name: str) -> Path:
    """Return the scope-owned data file in the project's artifact home."""
    return artifact_path(root, f"a.ghog.coverage.{name}")


def prepare(root: Path, name: str, *, fresh: bool) -> tuple[Path, float]:
    """Reset full coverage; affected runs retain data for pytest-cov append."""
    path = data_file(root, name)
    if fresh:
        path.unlink(missing_ok=True)
    return path, time.time()


def environment(path: Path) -> dict[str, str]:
    """Give the streaming runner its spawn-only coverage destination override."""
    return {"COVERAGE_FILE": str(path)}


def judge(root: Path, scope: ResolvedScope, data_path: Path, started: float) -> GroupCoverage:
    """Read fresh coverage and report exactly the resolved source membership.

    A missing, stale or unreadable data file is evidence failure, never a gap.
    The full-precision API percentage gates at 100, independently of display rounding.
    """
    try:
        if data_path.stat().st_mtime < started:
            return GroupCoverage(None, error=f"coverage evidence stale: {data_path}")
        with chdir(root):
            return _report(scope, data_path)
    except (OSError, CoverageException, ValueError) as error:
        return GroupCoverage(None, error=f"coverage evidence unusable: {data_path}: {error}")


def _report(scope: ResolvedScope, data_path: Path) -> GroupCoverage:
    """Honor coverage's config search and relative-file mapping in the project cwd."""
    coverage = Coverage(data_file=str(data_path), config_file=True)
    with closing(coverage.get_data()) as data:
        coverage.load()
        if coverage.get_option("run:branch") and not data.has_arcs():
            return GroupCoverage(None, error=f"coverage evidence lacks required branch data: {data_path}")
        report = io.StringIO()
        # Membership already applied project omissions. Disable report filters
        # so capture execution judges that bound list even after config edits.
        percent = coverage.report(
            morfs=list(scope.source_files), file=report, show_missing=True,
            skip_covered=True, omit=[], include=[], ignore_errors=False,
        )
        return GroupCoverage(percent, tuple(report.getvalue().splitlines()))


# eof
