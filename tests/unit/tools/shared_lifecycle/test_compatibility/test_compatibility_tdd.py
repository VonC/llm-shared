"""Keep scenario generation and verdicts real while replacing child transport."""

from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from tools.lifecycle_compatibility import runner, scenarios

if TYPE_CHECKING:
    from collections.abc import Callable

_CLEANUP_TIMEOUT = 5


def _not_alive(_pid: int) -> bool:
    """Represent a worker already reaped by its controller."""
    return False


def _alive(_pid: int) -> bool:
    """Represent a surviving worker for failure-cleanup tests."""
    return True


def _kill(_pid: int, *, group: bool = True) -> None:
    """Observe the cleanup seam without sending a real signal."""
    assert group is False


def _unrelated(**_kwargs: object) -> tuple[str, str]:
    """Return output that cannot prove the required declaration diagnostic."""
    return "unrelated", ""


def _passed(*_args: object) -> dict[str, object]:
    """Represent already-verified evidence when testing CLI aggregation."""
    return {"passed": True}

@pytest.fixture
def transport(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    """Observe actual commands without starting a process in the carrying suite."""
    calls: list[dict[str, object]] = []

    class Child:
        """Supply a completed controller and its real evidence file shapes."""

        pid = 456
        returncode = 4

        def __init__(self, command: list[str], **kwargs: object) -> None:
            calls.append({"command": command, **kwargs})
            root = Path(str(kwargs["cwd"]))
            (root / "worker.gw0.pid").write_text("101", encoding="utf-8")
            (root / "worker.gw1.pid").write_text("102", encoding="utf-8")
            (root / "announced").write_text("gw0", encoding="utf-8")

        def communicate(self, timeout: float | None = None) -> tuple[str, str]:
            assert timeout is not None
            return "process_allowed requires a non-empty reason string", ""

    monkeypatch.setattr(runner.subprocess, "Popen", Child)
    monkeypatch.setattr(runner, "alive", _not_alive)
    return calls


def test_smoke_preserves_isolation_and_interprets_real_evidence(
    tmp_path: Path, transport: list[dict[str, object]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Inherited selection cannot bind a generated project to the carrying suite."""
    monkeypatch.setenv("PYTEST_ADDOPTS", "--bad")
    monkeypatch.setenv("LLM_SHARED_PYTEST_BINDING", "stale")
    result = runner.run_smoke(tmp_path)
    assert result["passed"] is True
    assert result["returncode"] == pytest.ExitCode.USAGE_ERROR
    assert result["workers_reaped"] is True
    _assert_launch_isolation(transport[0])
    assert (tmp_path / "project" / "pytest.ini").exists()
    assert json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))["passed"]


def _assert_launch_isolation(call: dict[str, object]) -> None:
    """Inspect the fixed plugin selection and cleared selection environment."""
    command = cast("list[str]", call["command"])
    assert "xdist.plugin" in command
    assert "llm_shared_process_audit" in command
    environment = cast("dict[str, str]", call["env"])
    assert "PYTEST_ADDOPTS" not in environment
    assert "LLM_SHARED_PYTEST_BINDING" not in environment
    assert environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"


@pytest.mark.parametrize("scenario", scenarios.NAMES)
def test_scenario_construction_keeps_peer_observation_before_bad_worker(
    tmp_path: Path, scenario: str,
) -> None:
    """Generated projects contain a bounded peer handshake and test-start proof."""
    scenarios.write_project(tmp_path, scenario)
    source = (tmp_path / "conftest.py").read_text(encoding="utf-8")
    compile(source, "conftest.py", "exec")
    assert "pytest_xdist_node_collection_finished" in source
    assert "monotonic() + 15" in source
    assert scenario in source
    assert "started" in (tmp_path / "test_peer.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("change", ["started", "missing_peer", "missing_worker", "diagnostic", "exitcode", "alive"])
def test_negative_evidence_cannot_pass(
    tmp_path: Path, transport: list[dict[str, object]], monkeypatch: pytest.MonkeyPatch, change: str,
) -> None:
    """Each required observation independently participates in the verdict."""
    original = runner.subprocess.Popen
    def altered(*args: object, **kwargs: object) -> object:
        child = cast("Callable[..., object]", original)(*args, **kwargs)
        root = Path(str(kwargs["cwd"]))
        if change == "started":
            (root / "started").touch()
        elif change == "missing_peer":
            (root / "announced").unlink()
        elif change == "missing_worker":
            (root / "worker.gw1.pid").unlink()
        elif change == "diagnostic":
            monkeypatch.setattr(child, "communicate", _unrelated)
        elif change == "exitcode":
            monkeypatch.setattr(child, "returncode", 0)
        elif change == "alive":
            monkeypatch.setattr(runner, "alive", _alive)
            monkeypatch.setattr(runner, "kill_tree", _kill)
        return child
    monkeypatch.setattr(runner.subprocess, "Popen", altered)
    assert runner.run_smoke(tmp_path)["passed"] is False
    assert len(transport) == 1


def test_timeout_kills_and_reaps_controller(
    tmp_path: Path, transport: list[dict[str, object]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A hung controller is bounded and its pipe is drained after tree cleanup."""
    killed: list[int] = []
    original = runner.subprocess.Popen
    def hanging(*args: object, **kwargs: object) -> object:
        child = cast("Callable[..., object]", original)(*args, **kwargs)
        attempts = iter([True, False])
        def communicate(timeout: float) -> tuple[str, str]:
            if next(attempts):
                command = "pytest"
                raise subprocess.TimeoutExpired(command, timeout)
            return "", ""
        monkeypatch.setattr(child, "communicate", communicate)
        return child
    monkeypatch.setattr(runner.subprocess, "Popen", hanging)
    monkeypatch.setattr(runner, "kill_tree", killed.append)
    result = runner.run_smoke(tmp_path)
    assert result["timed_out"] is True
    assert result["passed"] is False
    assert killed == [456]
    assert len(transport) == 1


def test_cli_records_real_versions_and_reports_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The CLI aggregates all scenarios and returns a failing executable verdict."""
    runs: list[str] = []
    def smoke(root: Path, scenario: str) -> dict[str, object]:
        runs.append(scenario)
        assert root.parent == tmp_path
        return {"passed": scenario != "exit"}
    monkeypatch.setattr(runner, "run_smoke", smoke)
    assert runner.main([str(tmp_path)]) == 1
    assert runs == list(scenarios.NAMES)
    evidence = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert evidence["python"]
    assert evidence["pytest"]
    assert evidence["xdist"]
    monkeypatch.setattr(runner, "run_smoke", _passed)
    assert runner.main([str(tmp_path)]) == 0


def test_fresh_evidence_is_required(tmp_path: Path) -> None:
    """An earlier announcement or start marker must never contaminate a probe."""
    (tmp_path / "project").mkdir()
    with pytest.raises(ValueError, match="fresh project"):
        runner.run_smoke(tmp_path)


@pytest.mark.parametrize("running", [True, False])
def test_windows_process_probe_matches_pid_column(
    monkeypatch: pytest.MonkeyPatch, *, running: bool,
) -> None:
    """CSV image names and localized no-match output cannot masquerade as PIDs."""
    monkeypatch.setattr(runner.sys, "platform", "win32")
    commands: list[list[str]] = []
    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        assert kwargs["timeout"] == _CLEANUP_TIMEOUT
        output = '"python.exe","123","Console"' if running else "INFO: no matches"
        return subprocess.CompletedProcess(command, 0, stdout=output)
    monkeypatch.setattr(runner.subprocess, "run", run)
    assert runner.alive(123) is running
    runner.kill_tree(123)
    assert commands[0][0] == "tasklist"
    assert commands[1] == ["taskkill", "/T", "/F", "/PID", "123"]


@pytest.mark.parametrize("missing", [False, True])
@pytest.mark.parametrize("group", [False, True])
def test_posix_probe_and_cleanup(
    monkeypatch: pytest.MonkeyPatch, *, missing: bool, group: bool,
) -> None:
    """POSIX cleanup handles both a controller group and an orphaned worker."""
    monkeypatch.setattr(runner.sys, "platform", "linux")
    signals: list[tuple[int, int]] = []
    def send(pid: int, signum: int) -> None:
        signals.append((pid, signum))
        if missing:
            raise ProcessLookupError
    monkeypatch.setattr(runner.os, "kill", send)
    monkeypatch.setattr(runner.os, "killpg", send, raising=False)
    monkeypatch.setattr(runner.signal, "SIGKILL", 9, raising=False)
    assert runner.alive(123) is not missing
    runner.kill_tree(123, group=group)
    assert signals == [(123, 0), (123, 9)]


def test_module_entrypoint_uses_same_harness(
    tmp_path: Path, transport: list[dict[str, object]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Executing the module returns its aggregate verdict through SystemExit."""
    monkeypatch.setattr(runner.sys, "argv", ["runner", str(tmp_path)])
    monkeypatch.setattr(runner.sys, "platform", "win32")
    # runpy creates a second module; replace its transport-independent process
    # probes through the shared subprocess seam rather than granting permission.
    def no_processes(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="")
    monkeypatch.setattr(runner.subprocess, "run", no_processes)
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(runner.__file__, run_name="__main__")
    assert caught.value.code == 1
    assert len(transport) == len(scenarios.NAMES)


# eof
