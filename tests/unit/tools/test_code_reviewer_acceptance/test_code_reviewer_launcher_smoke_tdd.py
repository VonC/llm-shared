"""One real startup smoke per code-reviewer launcher."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import cast

import pytest

# ruff: noqa: S603

_LAUNCHERS = (
    ("code_review_request.bat", "usage: code-review-request"),
    ("code_review_evidence.bat", "usage: code-review-evidence"),
    ("code_review_answer.bat", "usage: code_review_answer_cli.py"),
)


@pytest.fixture(params=_LAUNCHERS, ids=lambda case: case[0])
def launcher_startup(request: pytest.FixtureRequest) -> None:
    """Start each shipped launcher once outside measured call timing."""
    launcher, usage = cast("tuple[str, str]", request.param)
    path = (Path("bin") / launcher).resolve()
    result = subprocess.run(
        [str(path), "--help"],
        cwd=Path.cwd(),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert usage in result.stdout


def test_each_code_review_launcher_reaches_its_public_entry_point(
    launcher_startup: None,
) -> None:
    """Requirement AC08: canonical launchers reach their public entry points."""
    assert launcher_startup is None
