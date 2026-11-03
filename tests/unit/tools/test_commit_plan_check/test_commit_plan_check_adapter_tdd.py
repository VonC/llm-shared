"""Direct caller-root discovery and module entry-point exit contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.script_entry import run_main
from tools import commit_plan_check

# ruff: noqa: S603, S607

NON_READY_STATUS = 3


def _valid_plan() -> str:
    """Return one parser-valid commit plan for the staged sample file."""
    return """git add -- sample.txt

feat(check): validate sample

Why:

The sample needs an exact commit plan.

The repository can now expose ready evidence.

What:

- Validate the staged sample.
"""


def test_cli_checks_the_caller_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Default root discovery reaches production policy from a foreign cwd."""
    from tests.acceptance.commit_plan_check.repository_observations import (  # noqa: PLC0415
        declare_index,
        declare_repository,
        read_index,
    )
    from tools import commit_plan_support  # noqa: PLC0415

    declare_repository(tmp_path, {})
    (tmp_path / "sample.txt").write_text("sample\n", encoding="utf-8")
    (tmp_path / "a.commit").write_text(_valid_plan(), encoding="utf-8")
    declare_index(tmp_path, "sample.txt")
    monkeypatch.setattr(commit_plan_support, "run_cross_platform_git_command", read_index)
    monkeypatch.delenv("PRJ_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    assert commit_plan_check.main(["--format", "json"]) == 0
    output = capsys.readouterr()
    assert output.err == ""
    assert json.loads(output.out)["state"] == "valid"


def test_module_main_guard_exits_with_the_cli_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The in-process module guard passes through expected non-readiness."""
    (tmp_path / ".git").mkdir()
    script = Path(commit_plan_check.__file__)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(script), "--root", str(tmp_path), "--format", "json"],
    )

    with pytest.raises(SystemExit) as raised:
        run_main(str(script))

    assert raised.value.code == NON_READY_STATUS
    assert json.loads(capsys.readouterr().out)["state"] == "missing-plan"


# eof
