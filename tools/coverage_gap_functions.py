"""coverage_gap_functions.py.

Map uncovered line ranges (or missing lines from coverage.json) to the enclosing
function/method name, and optionally to a nearby branch context (if/else/except/etc).

Fix: Split the shared helpers, AST mapping logic, and CLI support into smaller
modules while keeping this file as the script and import hub.
"""

from __future__ import annotations

import contextlib
import logging
import sys
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))
        sys.path.insert(0, str((_project_root / "src").resolve()))

from tools.coverage_gap_functions_cli import main as _workflow_main
from tools.coverage_gap_functions_mapping import (
    BranchCollector,
    collect_functions,
    find_containing_func,
    render_mapping,
)
from tools.coverage_gap_functions_shared import (
    POST_COVERAGE_LINES,
    ROOT_MARKERS_DIR,
    ROOT_MARKERS_FILE,
    BranchBlock,
    CoverageGapError,
    CoverageJsonFileMatchError,
    CoverageJsonFormatError,
    CoverageJsonNotFoundError,
    Detail,
    FuncInfo,
    InputFileNotFoundError,
    InvalidRangeError,
    LineRange,
    compress_lines_to_ranges,
    find_project_root,
    load_missing_ranges_from_coverage_json,
)

LOGGER = logging.getLogger("coverage_gap_functions")


def _configure_logging() -> None:
    """Configure fatal-error logging for direct script execution."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with code 2 when the script hub is executed directly."""
    _configure_logging()
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(2) from err


def main(argv: list[str] | None = None) -> int:
    """Delegate CLI execution to the split CLI module."""
    return _workflow_main(argv)


__all__ = [
    "POST_COVERAGE_LINES",
    "ROOT_MARKERS_DIR",
    "ROOT_MARKERS_FILE",
    "BranchBlock",
    "BranchCollector",
    "CoverageGapError",
    "CoverageJsonFileMatchError",
    "CoverageJsonFormatError",
    "CoverageJsonNotFoundError",
    "Detail",
    "FuncInfo",
    "InputFileNotFoundError",
    "InvalidRangeError",
    "LineRange",
    "collect_functions",
    "compress_lines_to_ranges",
    "find_containing_func",
    "find_project_root",
    "load_missing_ranges_from_coverage_json",
    "main",
    "render_mapping",
]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CoverageGapError, OSError) as err:
        _log_fatal(err)


# eof
