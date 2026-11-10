"""Exercise prepared/collision contracts with typed, isolated cache storage."""

from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from tools import pytest_plugin_environment
from tools.lifecycle_compatibility import (
    behavior_runner,
    behavior_scenarios,
    environment,
    runner,
    shell_runner,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

_CASE_TIMEOUT = 30
_ALL_SCENARIOS = 26


@pytest.mark.parametrize("case", behavior_scenarios.cases(), ids=lambda case: case.name)
def test_executable_scenarios_keep_real_contracts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: behavior_scenarios.Case) -> None:
    """Generated code, fixed loading, diagnostics and summary counts remain real."""
    calls: list[list[str]] = []
    def cache_root(_environment: Mapping[str, str]) -> Path:
        return tmp_path / "loader-cache"
    monkeypatch.setattr(pytest_plugin_environment, "default_cache_root", cache_root)
    compile(case.source, case.name, "exec")
    compile(case.conftest, "conftest.py", "exec")
    class Child:
        """Supply only the external pytest observation for this scenario."""

        returncode = case.code

        def __init__(self, command: list[str], **kwargs: object) -> None:
            calls.append(command)
            assert kwargs["cwd"] == tmp_path / "project"

        def communicate(self, timeout: int) -> tuple[str, None]:
            assert timeout == _CASE_TIMEOUT
            return "\n".join([*case.contains, *(text for text, count in case.summaries for _ in range(count))]), None
    monkeypatch.setattr(behavior_runner.subprocess, "Popen", Child)
    def packages(destination: Path) -> None:
        destination.mkdir()
    monkeypatch.setattr(behavior_runner, "mandatory_packages", packages)
    assert behavior_runner.run_case(tmp_path, case)["passed"] is True
    assert len(calls) == 1
    assert ("-S" in calls[0]) is case.optional_absent
    if case.optional_absent:
        assert 'find_spec("xdist") is None' in (tmp_path / "project/test_behavior.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("timeout", [False, True])
def test_harness_failures_and_timeouts_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, timeout: bool) -> None:
    """A timed-out child is killed/reaped and cannot supply success evidence."""
    killed: list[int] = []
    class Child:
        """Supply a failed child, optionally requiring bounded cleanup."""

        pid = 71
        returncode = 1

        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self.calls = 0

        def communicate(self, timeout: int) -> tuple[str, None]:
            self.calls += 1
            if self.calls == 1 and timeout == _CASE_TIMEOUT and should_timeout:
                command = "pytest"
                raise subprocess.TimeoutExpired(command, timeout)
            return "", None
    should_timeout = timeout
    monkeypatch.setattr(behavior_runner.subprocess, "Popen", Child)
    monkeypatch.setattr(runner, "kill_tree", killed.append)
    result = behavior_runner.run_case(tmp_path, behavior_scenarios.cases()[0])
    assert result["passed"] is False
    assert result["timed_out"] is timeout
    assert killed == ([71] if timeout else [])


@pytest.mark.parametrize("missing", [False, True])
def test_optional_environment_contains_only_mandatory_packages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, missing: bool) -> None:
    """No optional plugin packages are copied into the site-free import path."""
    copies: list[str] = []
    def find_spec(name: str) -> SimpleNamespace | None:
        if missing:
            return None
        return SimpleNamespace(origin=str(tmp_path / (name + ".py")) if name == "py" else str(tmp_path / name / "__init__.py"))
    def copytree(_source: Path, destination: Path, **_kwargs: object) -> None:
        copies.append(destination.name)
    def copyfile(_source: Path, destination: Path) -> None:
        copies.append(destination.stem)
    monkeypatch.setattr(behavior_runner.importlib.util, "find_spec", find_spec)
    monkeypatch.setattr(behavior_runner.shutil, "copytree", copytree)
    monkeypatch.setattr(behavior_runner.shutil, "copyfile", copyfile)
    if missing:
        with pytest.raises(ValueError, match="Mandatory pytest package"):
            behavior_runner.mandatory_packages(tmp_path / "vendor")
    else:
        behavior_runner.mandatory_packages(tmp_path / "vendor")
        assert {"pytest", "_pytest", "py", "pluggy", "packaging", "iniconfig", "pygments", "colorama"} == set(copies)
        assert "xdist" not in copies


def test_runner_all_mode_validates_versions_and_aggregates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Full mode preserves barrier probes and adds every policy case."""
    probes: list[Path] = []
    def verify(root: Path, *_args: object) -> None:
        assert root == runner.Path(runner.__file__).resolve().parents[2]
        assert _args == (runner.Path(runner.sys.executable), runner.sys.version_info[:2])
        probes.append(root)
    def smoke(_root: Path, name: str) -> dict[str, object]:
        return {"scenario": name, "passed": True}
    def case_result(_root: Path, case: behavior_scenarios.Case) -> dict[str, object]:
        return {"scenario": case.name, "passed": True}
    monkeypatch.setattr(environment, "verify", verify)
    monkeypatch.setattr(runner, "run_smoke", smoke)
    monkeypatch.setattr(behavior_runner, "run_case", case_result)
    def shells(root: Path) -> list[dict[str, object]]:
        assert root == tmp_path / "windows-shell"
        return [{"scenario": "windows-shell", "passed": None, "status": "not run"}]
    monkeypatch.setattr(shell_runner, "run_all", shells)
    assert runner.main([str(tmp_path), "--all"]) == 0
    assert len(probes) == 1
    results = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))["scenarios"]
    assert len(results) == _ALL_SCENARIOS
    assert results == [{"scenario": name, "passed": True} for name in (
        *runner.scenarios.NAMES, *(case.name for case in behavior_scenarios.cases()),
    )] + [{"scenario": "windows-shell", "passed": None, "status": "not run"}]


# eof
