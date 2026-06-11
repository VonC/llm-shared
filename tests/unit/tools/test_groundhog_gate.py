"""Unit tests for the groundhog coverage gate resolution (Q14).

Cover the pyproject.toml, .coveragerc and setup.cfg readers, their
precedence, the default of 100, and the value conversion guards.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.groundhog import gate

if TYPE_CHECKING:
    from pathlib import Path

_GATE_95 = 95.0
_GATE_90 = 90.0
_GATE_80 = 80.0


def test_default_gate_without_configuration(tmp_path: Path) -> None:
    """No configuration file means the default gate of 100 (Q14)."""
    assert gate.read_coverage_gate(tmp_path) == gate.DEFAULT_COVERAGE_GATE


def test_gate_from_pyproject(tmp_path: Path) -> None:
    """pyproject.toml [tool.coverage.report] fail_under wins first."""
    (tmp_path / "pyproject.toml").write_text(
        "[tool.coverage.report]\nfail_under = 95\n",
        encoding="utf-8",
    )
    assert gate.read_coverage_gate(tmp_path) == _GATE_95


def test_gate_from_coveragerc(tmp_path: Path) -> None:
    """.coveragerc [report] fail_under is read when pyproject is silent."""
    (tmp_path / "pyproject.toml").write_text("[tool.other]\n", encoding="utf-8")
    (tmp_path / ".coveragerc").write_text(
        "[report]\nfail_under = 90\n",
        encoding="utf-8",
    )
    assert gate.read_coverage_gate(tmp_path) == _GATE_90


def test_gate_from_setup_cfg(tmp_path: Path) -> None:
    """setup.cfg [coverage:report] fail_under is the last fallback."""
    (tmp_path / "setup.cfg").write_text(
        "[coverage:report]\nfail_under = 80\n",
        encoding="utf-8",
    )
    assert gate.read_coverage_gate(tmp_path) == _GATE_80


def test_pyproject_without_report_section(tmp_path: Path) -> None:
    """A pyproject with [tool.coverage] but no report section is skipped."""
    (tmp_path / "pyproject.toml").write_text(
        "[tool.coverage.run]\nbranch = true\n",
        encoding="utf-8",
    )
    assert gate.read_coverage_gate(tmp_path) == gate.DEFAULT_COVERAGE_GATE


def test_pyproject_without_coverage_tool(tmp_path: Path) -> None:
    """A pyproject with a tool table but no coverage entry is skipped."""
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\naddopts = []\n",
        encoding="utf-8",
    )
    assert gate.read_coverage_gate(tmp_path) == gate.DEFAULT_COVERAGE_GATE


def test_pyproject_without_tool_table(tmp_path: Path) -> None:
    """A pyproject without any tool table is skipped."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n',
        encoding="utf-8",
    )
    assert gate.read_coverage_gate(tmp_path) == gate.DEFAULT_COVERAGE_GATE


def test_malformed_pyproject_is_skipped(tmp_path: Path) -> None:
    """A TOML parse error falls back to the next configuration source."""
    (tmp_path / "pyproject.toml").write_text("[broken", encoding="utf-8")
    assert gate.read_coverage_gate(tmp_path) == gate.DEFAULT_COVERAGE_GATE


def test_malformed_ini_is_skipped(tmp_path: Path) -> None:
    """An ini parse error falls back to the default gate."""
    (tmp_path / ".coveragerc").write_text("no section here", encoding="utf-8")
    assert gate.read_coverage_gate(tmp_path) == gate.DEFAULT_COVERAGE_GATE


def test_ini_without_the_option_is_skipped(tmp_path: Path) -> None:
    """An ini report section without fail_under is skipped."""
    (tmp_path / ".coveragerc").write_text(
        "[report]\nshow_missing = true\n",
        encoding="utf-8",
    )
    assert gate.read_coverage_gate(tmp_path) == gate.DEFAULT_COVERAGE_GATE


def test_as_gate_converts_numbers_and_strings() -> None:
    """Numeric and numeric-string values convert to a float gate."""
    assert gate._as_gate(95) == _GATE_95
    assert gate._as_gate(95.0) == _GATE_95
    assert gate._as_gate("95") == _GATE_95


def test_as_gate_rejects_non_numbers() -> None:
    """Booleans, None, words and other types are rejected."""
    assert gate._as_gate(True) is None  # noqa: FBT003
    assert gate._as_gate(None) is None
    assert gate._as_gate("not-a-number") is None
    assert gate._as_gate([95]) is None


# eof
