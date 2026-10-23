"""Real isolated processes prove producer authority and import failure isolation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

import pytest

if TYPE_CHECKING:
    import subprocess


@pytest.mark.parametrize(("scenario", "status"), [
    ("success", 0), ("failed_setup", 7), ("no_environment", 0),
    ("missing_python", 2), ("foreign_python", 0),
])
def test_setup_entry(processes: dict[str, object], scenario: str, status: int) -> None:
    """Batch entry propagates saved status and only publishes measured success."""
    result = cast("subprocess.CompletedProcess[str]", processes[scenario])
    assert result.returncode == status, result.stdout + result.stderr
    assert processes["preserved"]
    assert processes["nonlocal_preserved"]
    assert processes["record"] == "1\nvenvs/prepared\n"
    if scenario in ("no_environment", "foreign_python"):
        assert "Warning: release runtime identity not updated" in result.stderr


@pytest.mark.parametrize(("scenario", "status"), [
    ("clean_success", 0), ("clean_setup_failure", 7), ("clean_producer_failure", 2),
])
def test_setup_status_cleanup(processes: dict[str, object], scenario: str, status: int) -> None:
    """The actual senv block preserves failures and never leaks its temporaries."""
    result = cast("subprocess.CompletedProcess[str]", processes[scenario])
    assert result.returncode == status, result.stdout + result.stderr
    assert "STATUS_CLEAN" in result.stdout
    assert ("SETUP_CONTINUED" in result.stdout) == (status == 0)


@pytest.mark.parametrize(("scenario", "status", "imported"), [
    ("ready", 0, True), ("missing_engine", 2, True), ("missing_record", 2, False),
    ("escaped_record", 2, False),
])
def test_isolated_bootstrap(processes: dict[str, object], scenario: str, status: int, *, imported: bool) -> None:
    """Failure before readiness leaves tools unimported and consumer untouched."""
    result = cast("subprocess.CompletedProcess[str]", processes[scenario])
    assert result.returncode == 0, result.stderr
    observed = json.loads(result.stdout)
    assert observed == {"status": status, "tools": imported, "isolated": 1, "utf8": 1, "bytecode": True}
    if status:
        assert "Run this checkout's setup" in result.stderr
    assert processes["cache_files"] == []
    assert processes["consumer_unchanged"]


def test_eager_import_closure(eager_closure: subprocess.CompletedProcess[str]) -> None:
    """The real tools initializer and its closure need no third-party packages."""
    assert eager_closure.returncode == 0, eager_closure.stderr
    imports = json.loads(eager_closure.stdout)
    assert "tools.review_exchange_publication" in imports
    assert "tools.release_workflow" in imports

# eof
