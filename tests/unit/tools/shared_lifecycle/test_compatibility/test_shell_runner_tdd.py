"""Keep real shell generation/verdicts while replacing processes and threads.

Virtual scratch exercises snapshots and transfers; only the standalone harness
starts cmd. Exhaustive finite cases cover this orchestration, without new PBT.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, TypeVar

import pytest

from tools.lifecycle_compatibility import runner, shell_runner, shell_scenarios
from tools.pytest_plugin_shell import OWNED_KEYS

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from typing import Self

_Item = TypeVar("_Item")
_Result = TypeVar("_Result")
_SHELL_CASES = 10
_SHELL_RESULTS = 11
_TRANSFERS = 4
_TIMEOUT = 30


class InlinePool:
    """Preserve mapped operations without starting threads in audited tests."""

    def __init__(self, *, max_workers: int) -> None:
        """Accept the production concurrency bound without allocating workers."""
        self.workers = max_workers

    def __enter__(self) -> Self:
        """Return the local mapped-operation boundary."""
        return self

    def __exit__(self, *_args: object) -> None:
        """Own no external resources that need cleanup."""

    def map(self, function: Callable[[_Item], _Result], items: Iterable[_Item]) -> Iterator[_Result]:
        """Run every supplied operation at its ordinary measured call site."""
        return map(function, items)


def snapshot(case: shell_scenarios.ShellCase) -> dict[str, str | None]:
    """Declare the observed success state, preserving both original suffixes."""
    return {"PROBE_EXIT": str(case.code), "LLM_SHARED_PYTEST_PLUGINS": "lifecycle,process",
            "LLM_SHARED_PYTEST_ROOT": str(case.cwd.resolve()), "LLM_SHARED_PYTEST_POLICY_DIR": "policy",
            "PYTHONPATH": "loader;" + case.extra.get("PYTHONPATH", ""),
            "PYTEST_ADDOPTS": "-p loader " + case.extra.get("PYTEST_ADDOPTS", "")}


@pytest.mark.parametrize("index", range(_SHELL_CASES))
def test_each_caller_case_preserves_contract(tmp_path: Path, index: int) -> None:
    """Both expansion modes, all refusal cases and concurrent callers are named."""
    cases = shell_scenarios.cases(tmp_path, Path(tmp_path.anchor))
    assert len({case.name for case in cases}) == _SHELL_CASES
    case = cases[index]
    before: dict[str, str | None] = dict.fromkeys((*OWNED_KEYS, "PROBE_EXIT"))
    after = {**before, "PROBE_EXIT": str(case.code)} if case.code else snapshot(case)
    assert shell_scenarios.verdict(case, case.code, before, after)
    assert case.delayed in ("off", "on")
    assert (case.cwd == Path(tmp_path.anchor)) == case.name.startswith("drive-root")


@pytest.mark.parametrize("change", ["exit", "PROBE_EXIT", *OWNED_KEYS])
def test_bad_success_evidence_fails_closed(tmp_path: Path, change: str) -> None:
    """Each owned observation and both exit observations affect the verdict."""
    case = shell_scenarios.cases(tmp_path, tmp_path)[0]
    after = snapshot(case)
    if change != "exit":
        after[change] = None
    assert not shell_scenarios.verdict(case, 1 if change == "exit" else 0, {}, after)


def test_partial_refusal_is_rejected(tmp_path: Path) -> None:
    """A refusal that changes even one owned value is not atomic."""
    case = shell_scenarios.cases(tmp_path, tmp_path)[1]
    assert not shell_scenarios.verdict(case, case.code, {}, {"PROBE_EXIT": "4", "PYTHONPATH": "changed"})


@pytest.mark.parametrize("value", [[], {}, dict.fromkeys((*OWNED_KEYS, "PROBE_EXIT"), 1)])
def test_incomplete_or_malformed_snapshot_is_rejected(tmp_path: Path, value: object) -> None:
    """JSON shape and value types must match the generated dumper's contract."""
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="shell snapshot"):
        shell_scenarios.read_snapshot(path)


@pytest.mark.parametrize("state", ["success", "missing", "timeout", "exit"])
def test_shell_transport_is_bounded_and_assesses_snapshots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, state: str) -> None:
    """Commands keep cwd/expansion; timeouts kill/reap and cannot earn a pass."""
    case = shell_scenarios.cases(tmp_path, tmp_path)[0]
    killed: list[int] = []
    class Child:
        """Supply only child observations at the existing Popen transport seam."""

        pid = 71
        returncode = 1 if state == "exit" else 0

        def __init__(self, command: list[str], **kwargs: object) -> None:
            self.calls = 0
            assert command == ["cmd", "/d", "/v:off", "/c", str(tmp_path / "caller.bat")]
            assert kwargs["cwd"] == case.cwd
            if state != "missing":
                home = tmp_path / case.name
                (home / "snapshot.before.json").write_text(json.dumps(dict.fromkeys((*OWNED_KEYS, "PROBE_EXIT"))), encoding="utf-8")
                (home / "snapshot.after.json").write_text(json.dumps(snapshot(case)), encoding="utf-8")

        def communicate(self, timeout: int) -> tuple[bytes, None]:
            self.calls += 1
            if state == "timeout" and self.calls == 1:
                assert timeout == _TIMEOUT
                command = "cmd"
                raise subprocess.TimeoutExpired(command, timeout)
            return b"caller observations", None
    monkeypatch.setattr(shell_runner.subprocess, "Popen", Child)
    monkeypatch.setattr(runner, "kill_tree", killed.append)
    result = shell_runner.run_case(tmp_path, case)
    assert result["passed"] is (state == "success")
    assert result["timed_out"] is (state == "timeout")
    assert killed == ([71] if state == "timeout" else [])
    assert (tmp_path / case.name / "controller.log").read_bytes() == b"caller observations"


def test_caller_environment_discards_inherited_bindings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only explicit case inputs enter the prepared caller environment."""
    for key in (*OWNED_KEYS, "LLM_SHARED_PYTEST_STALE", "PYTEST_PLUGINS", "PROBE_EXIT"):
        monkeypatch.setenv(key, "stale")
    environment = shell_runner.caller_environment(tmp_path, {"PYTEST_ADDOPTS": shell_scenarios.PUNCTUATION})
    assert environment["PYTEST_ADDOPTS"] == shell_scenarios.PUNCTUATION
    assert not (set(OWNED_KEYS) - {"PYTEST_ADDOPTS"}) & environment.keys()
    assert not {"LLM_SHARED_PYTEST_STALE", "PYTEST_PLUGINS", "PROBE_EXIT"} & environment.keys()
    assert environment["PATH"].startswith(str(Path(shell_runner.sys.executable).parent))


@pytest.mark.parametrize("corrupt", [False, True])
def test_concurrent_transfers_require_distinct_complete_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, corrupt: bool) -> None:
    """Transfer publication uses real virtual files; incomplete results fail."""
    monkeypatch.setattr(shell_runner, "ThreadPoolExecutor", InlinePool)
    if corrupt:
        def publish(*_args: object, **_kwargs: object) -> Path:
            path = tmp_path / "duplicate.env"
            path.write_text("partial", encoding="cp850")
            return path
        monkeypatch.setattr(shell_runner, "publish_result", publish)
    result = shell_runner.transfer_case(tmp_path, 850)
    assert result["passed"] is not corrupt
    assert result["count"] == _TRANSFERS
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("windows", [False, True])
def test_all_mode_keeps_eleven_shell_cases_or_reports_absence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, windows: bool) -> None:
    """Other platforms never claim passed; Windows wires every real operation."""
    monkeypatch.setattr(shell_runner.sys, "platform", "win32" if windows else "linux")
    monkeypatch.setattr(shell_runner, "ThreadPoolExecutor", InlinePool)
    monkeypatch.setattr(shell_runner.ctypes, "windll", SimpleNamespace(kernel32=SimpleNamespace(GetOEMCP=lambda: 850)), raising=False)
    calls: list[str] = []
    def run_case(_evidence: Path, case: shell_scenarios.ShellCase) -> dict[str, object]:
        calls.append(case.name)
        return {"scenario": case.name, "passed": True}
    monkeypatch.setattr(shell_runner, "run_case", run_case)
    evidence = tmp_path / "windows-shell"
    results = shell_runner.run_all(evidence)
    if windows:
        assert len(results) == _SHELL_RESULTS
        assert len(calls) == _SHELL_CASES
        assert all(result["passed"] for result in results)
        assert "chcp 850 >nul" in (evidence / "caller.bat").read_text(encoding="ascii")
        compile((evidence / "dump.py").read_text(encoding="utf-8"), "dump.py", "exec")
    else:
        assert results == [{"scenario": "windows-shell", "passed": None, "status": "not run", "reason": "requires Windows cmd.exe"}]
        assert not evidence.exists()
        assert calls == []


# eof
