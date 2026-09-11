"""Executable adapter parity tests for the read-only commit-plan checker.

Step 2 keeps module and batch entry points on the caller's repository while
sharing one CLI implementation and exit-status contract. Real process setup is
module-scoped so Groundhog measures the assertions rather than startup I/O.
"""

from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

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


def _real_repository(root: Path) -> None:
    """Create a real repository with one staged file and matching plan."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / "sample.txt").write_text("sample\n", encoding="utf-8")
    (root / "a.commit").write_text(_valid_plan(), encoding="utf-8")
    subprocess.run(["git", "add", "--", "sample.txt"], cwd=root, check=True)


def _module_environment(project_root: Path) -> dict[str, str]:
    """Expose llm-shared imports without overriding caller-root discovery."""
    environment = os.environ.copy()
    environment.pop("PRJ_DIR", None)
    previous = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        f"{project_root}{os.pathsep}{previous}" if previous else str(project_root)
    )
    return environment


@pytest.fixture(scope="module")
def adapter_results(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    """Run both real adapters once outside the measured assertion call."""
    repository = tmp_path_factory.mktemp("commit-plan-check-adapters")
    _real_repository(repository)
    project_root = Path(commit_plan_check.__file__).resolve().parent.parent
    environment = _module_environment(project_root)

    module = subprocess.run(
        [sys.executable, "-m", "tools.commit_plan_check", "--format", "json"],
        cwd=repository,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    launcher = subprocess.run(
        [str(project_root / "commit-plan-check.bat"), "--format", "json"],
        cwd=repository,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return module, launcher


@pytest.mark.skipif(sys.platform != "win32", reason="Windows batch launcher")
def test_module_and_root_launcher_check_the_same_caller_repository(
    adapter_results: tuple[
        subprocess.CompletedProcess[str],
        subprocess.CompletedProcess[str],
    ],
) -> None:
    """Both adapters return identical evidence and status from a foreign cwd."""
    module, launcher = adapter_results

    assert module.returncode == launcher.returncode == 0
    assert module.stderr == launcher.stderr == ""
    assert json.loads(module.stdout) == json.loads(launcher.stdout)
    assert json.loads(launcher.stdout)["state"] == "valid"


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
        runpy.run_path(str(script), run_name="__main__")

    assert raised.value.code == NON_READY_STATUS
    assert json.loads(capsys.readouterr().out)["state"] == "missing-plan"


# eof
