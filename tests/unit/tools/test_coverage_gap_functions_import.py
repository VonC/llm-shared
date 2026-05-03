"""Tests for coverage gap helper hub import coverage.

Fix: Cover the module-scope initialization in the split
`tools.coverage_gap_functions` hub.
"""

from __future__ import annotations

from tools import coverage_gap_functions


def test_coverage_gap_functions_module_import_exposes_cli_constants() -> None:
    """Importing the module should initialize its public CLI constants."""
    assert coverage_gap_functions.ROOT_MARKERS_DIR == (".git",)
    assert coverage_gap_functions.POST_COVERAGE_LINES[0].startswith(
        "Make sure check.bat is passing",
    )


# eof
