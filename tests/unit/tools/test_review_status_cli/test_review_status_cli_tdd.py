"""Tests for review-status CLI boundaries and caller-preserving launcher.

The real Windows adapter process is module-scoped so its unavoidable startup
cost does not dominate the assertion call measured by the duration gate.
"""

from __future__ import annotations

import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import review_status, review_status_cli
from tools.review_status_models import (
    SCHEMA_VERSION,
    DamagedCandidateStatus,
    MigrationStatus,
    ReviewStatusOutcome,
    ReviewStatusResult,
)

_NON_TRUSTWORTHY_STATUS = 3
_OPERATIONAL_STATUS = 2


def _result(root: Path, outcome: ReviewStatusOutcome) -> ReviewStatusResult:
    """Return a minimal valid result for each process-status category."""
    exchanges = (
        (
            DamagedCandidateStatus(
                candidate_path="a.review-active.broken.md",
                diagnostic="damaged",
            ),
        )
        if outcome is ReviewStatusOutcome.UNTRUSTWORTHY
        else ()
    )
    return ReviewStatusResult(
        schema_version=SCHEMA_VERSION,
        repository_root=root.resolve().as_posix(),
        outcome=outcome,
        exchanges=exchanges,
        active_count=len(exchanges),
        has_errors=outcome is not ReviewStatusOutcome.TRUSTWORTHY,
        migration=(
            MigrationStatus.blocked(".reviews", ("collection failed",))
            if outcome is ReviewStatusOutcome.OPERATIONAL_FAILURE
            else MigrationStatus.unnecessary(".reviews")
        ),
    )


def test_main_discovers_upward_collects_once_and_renders_human(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Argument-free use retains the caller repository as collection root."""
    root = tmp_path / "répository"
    nested = root / "nested" / "caller"
    (root / ".git").mkdir(parents=True)
    nested.mkdir(parents=True)
    observed: list[Path] = []

    def collect(selected: Path, _clock: object) -> ReviewStatusResult:
        observed.append(selected)
        return _result(selected, ReviewStatusOutcome.TRUSTWORTHY)

    monkeypatch.chdir(nested)
    monkeypatch.setattr(review_status_cli, "collect_review_status", collect)

    status = review_status_cli.main([])

    streams = capsys.readouterr()
    assert status == 0
    assert observed == [root.resolve()]
    assert streams.out.startswith(f"Repository: {root.resolve().as_posix()}\n")
    assert streams.err == ""


def test_main_honors_explicit_root_and_compact_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Controlled callers can select a root without changing directory."""
    root = tmp_path / "selected"
    (root / ".git").mkdir(parents=True)
    observed: list[Path] = []

    def collect(selected: Path, _clock: object) -> ReviewStatusResult:
        observed.append(selected)
        return _result(selected, ReviewStatusOutcome.TRUSTWORTHY)

    monkeypatch.setattr(review_status_cli, "collect_review_status", collect)

    status = review_status_cli.main(["--root", str(root), "--format", "json"])

    streams = capsys.readouterr()
    assert status == 0
    assert observed == [root.resolve()]
    assert json.loads(streams.out)["repository_root"] == root.resolve().as_posix()
    assert streams.out.count("\n") == 1
    assert streams.err == ""


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        (ReviewStatusOutcome.TRUSTWORTHY, 0),
        (ReviewStatusOutcome.UNTRUSTWORTHY, 3),
    ],
)
def test_main_returns_typed_nonfatal_process_status(
    outcome: ReviewStatusOutcome,
    expected: int,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Trustworthy and damaged queries both render on stdout with typed status."""
    (tmp_path / ".git").mkdir()

    def collect(root: Path, _clock: object) -> ReviewStatusResult:
        return _result(root, outcome)

    monkeypatch.setattr(
        review_status_cli,
        "collect_review_status",
        collect,
    )

    assert review_status_cli.main(["--root", str(tmp_path)]) == expected
    streams = capsys.readouterr()
    assert f"Outcome: {outcome.value}" in streams.out
    assert streams.err == ""


def test_operational_result_renders_on_stderr_without_partial_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failed collection cannot be mistaken for a trustworthy payload."""
    (tmp_path / ".git").mkdir()

    def collect(root: Path, _clock: object) -> ReviewStatusResult:
        return _result(root, ReviewStatusOutcome.OPERATIONAL_FAILURE)

    monkeypatch.setattr(
        review_status_cli,
        "collect_review_status",
        collect,
    )

    status = review_status_cli.main(["--root", str(tmp_path), "--format", "json"])

    streams = capsys.readouterr()
    assert status == _OPERATIONAL_STATUS
    assert streams.out == ""
    payload = json.loads(streams.err)
    assert payload["outcome"] == "operational-failure"
    assert payload["migration"] == {
        "artifact_home": ".reviews",
        "diagnostics": ["collection failed"],
        "moved_count": 0,
        "state": "blocked",
    }


@pytest.mark.parametrize("arguments", [["--root", "missing"], ["--format", "yaml"]])
def test_invalid_invocation_reports_only_a_stable_stderr_diagnostic(
    arguments: list[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid roots and arguments return two without any guessed payload."""
    monkeypatch.chdir(tmp_path)

    status = review_status_cli.main(arguments)

    streams = capsys.readouterr()
    assert status == _OPERATIONAL_STATUS
    assert streams.out == ""
    assert streams.err.startswith("rvw_status: ")


def test_existing_explicit_directory_must_be_a_git_root(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An existing ordinary directory cannot masquerade as an explicit root."""
    status = review_status_cli.main(["--root", str(tmp_path)])

    streams = capsys.readouterr()
    assert status == _OPERATIONAL_STATUS
    assert streams.out == ""
    assert "not a Git repository root" in streams.err


def test_upward_discovery_fails_without_a_git_ancestor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Argument-free discovery never guesses a repository when none exists."""
    nested = tmp_path / "ordinary" / "nested"
    nested.mkdir(parents=True)

    def no_git_marker(_candidate: Path) -> bool:
        return False

    monkeypatch.chdir(nested)
    monkeypatch.setattr(review_status_cli, "_git_marker", no_git_marker)

    status = review_status_cli.main([])

    streams = capsys.readouterr()
    assert status == _OPERATIONAL_STATUS
    assert streams.out == ""
    assert "no Git repository found from caller directory" in streams.err


def test_wall_clock_is_timezone_aware() -> None:
    """The production clock supplies comparable local protocol timestamps."""
    observed = review_status_cli._wall_clock()  # noqa: SLF001

    assert observed.tzinfo is not None
    assert observed.utcoffset() is not None


def test_unexpected_collection_failure_is_an_operational_boundary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Unexpected service errors do not leak a traceback or partial output."""
    (tmp_path / ".git").mkdir()

    def fail(_root: Path, _clock: object) -> ReviewStatusResult:
        message = "boom"
        raise RuntimeError(message)

    monkeypatch.setattr(review_status_cli, "collect_review_status", fail)

    assert review_status_cli.main(["--root", str(tmp_path)]) == _OPERATIONAL_STATUS
    streams = capsys.readouterr()
    assert streams.out == ""
    assert streams.err == "rvw_status: unexpected failure: boom\n"


def test_module_guard_forwards_main_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Direct module execution exits with the same typed CLI result status."""
    (tmp_path / ".git").mkdir()

    def collect(root: Path, _clock: object) -> ReviewStatusResult:
        return _result(root, ReviewStatusOutcome.UNTRUSTWORTHY)

    monkeypatch.setattr(review_status, "collect_review_status", collect)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(review_status_cli.__file__), "--root", str(tmp_path), "--format", "json"],
    )

    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(review_status_cli.__file__), run_name="__main__")

    assert raised.value.code == _NON_TRUSTWORTHY_STATUS
    assert json.loads(capsys.readouterr().out)["outcome"] == "untrustworthy"


@pytest.fixture(scope="module")
def launcher_observation(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[subprocess.CompletedProcess[str], Path, Path, Path]:
    """Run the controlled Windows launcher once outside the measured call phase."""
    tmp_path = tmp_path_factory.mktemp("review-status-launcher")
    project_root = Path(review_status_cli.__file__).resolve().parent.parent
    installed = tmp_path / "installed"
    caller = tmp_path / "caller"
    launcher = installed / "rvw_status.bat"
    tools_dir = installed / "tools"
    older = installed / "venvs" / "python_3.12.1_llm-shared_old" / "Scripts"
    newer = installed / "venvs" / "python_3.12.2_llm-shared_new" / "Scripts"
    caller.mkdir()
    tools_dir.mkdir(parents=True)
    older.mkdir(parents=True)
    newer.mkdir(parents=True)
    shutil.copy2(project_root / "rvw_status.bat", launcher)
    shutil.copy2(sys.executable, older / "python.exe")
    shutil.copy2(sys.executable, newer / "python.exe")
    pyvenv = f"home = {sys.base_prefix}\n"
    (older.parent / "pyvenv.cfg").write_text(pyvenv, encoding="utf-8")
    (newer.parent / "pyvenv.cfg").write_text(pyvenv, encoding="utf-8")
    (tools_dir / "__init__.py").write_text("", encoding="utf-8")
    (tools_dir / "review_status_cli.py").write_text(
        "import json, os, sys\n"
        "print(json.dumps({'cwd': os.getcwd(), 'python': sys.executable, "
        "'pythonpath': os.environ.get('PYTHONPATH'), 'argv': sys.argv[1:]}))\n"
        "raise SystemExit(3)\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment.pop("PRJ_DIR", None)
    environment["PYTHONPATH"] = "existing-path"

    completed = subprocess.run(  # noqa: S603
        [str(launcher), "--format", "json"],
        cwd=caller,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return completed, caller, newer, installed


@pytest.mark.skipif(sys.platform != "win32", reason="Windows batch launcher")
def test_launcher_self_locates_newest_runtime_and_preserves_caller_context(
    launcher_observation: tuple[subprocess.CompletedProcess[str], Path, Path, Path],
) -> None:
    """The batch adapter selects its newest runtime and forwards context and status."""
    completed, caller, newer, installed = launcher_observation

    payload = json.loads(completed.stdout)
    assert completed.returncode == _NON_TRUSTWORTHY_STATUS
    assert Path(payload["cwd"]) == caller
    assert Path(payload["python"]).parent == newer
    assert Path(payload["pythonpath"].split(os.pathsep)[0]) == installed
    assert payload["argv"] == ["--format", "json"]
