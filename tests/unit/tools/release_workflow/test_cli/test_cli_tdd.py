"""Dispatch isolates Git probes while preserving real context and failure policies."""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import cli
from tools.release_workflow.results import OperationResult
from tools.release_workflow.runtime_identity import RuntimeIdentity

if TYPE_CHECKING:
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.invocation import InvocationContext

_INVALID = 2


@pytest.mark.usefixtures("read_only_git")
def test_dispatch(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Native text arrives unchanged and diagnostics remain outside command data."""
    monkeypatch.setattr(cli, "stdin_is_console", lambda: False)
    payload = 'Bonjour %PATH% ^ ! & "quoted" 🐍'

    def handler(context: InvocationContext) -> OperationResult:
        assert context.payload == payload
        return OperationResult(data="result\n", diagnostics=("warning",))

    status = cli.main(
        ["probe", "--project-root", str(git_sandbox.home / "B"), "--text", payload],
        entry_kind="explicit-native", original_cwd=git_sandbox.home,
        runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"),
        environment=git_sandbox.environment, handlers={"probe": cli.Handler(handler, requires_input=True)},
    )
    assert status == 0
    captured = capsys.readouterr()
    assert captured.out == "result\n"
    assert captured.err.endswith("warning\n")
    assert "result" not in captured.err


@pytest.mark.parametrize("arguments", [[], ["missing"], ["probe", "--project-root", "A", "--project-root", "B"]])
def test_invalid_arguments(arguments: list[str], git_sandbox: GitSandbox, capsys: pytest.CaptureFixture[str]) -> None:
    """Unshipped domains and ambiguous arguments return input failure."""
    assert cli.main(arguments, entry_kind="explicit-native", original_cwd=git_sandbox.home,
                    runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared")) == _INVALID
    assert capsys.readouterr().err


@pytest.mark.usefixtures("read_only_git")
def test_missing_required_input(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Redirected stdin never prompts or invents consent."""
    monkeypatch.setattr(cli, "stdin_is_console", lambda: False)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("not implicitly consumed"))

    def handler(_context: InvocationContext) -> OperationResult:
        pytest.fail("handler must not run")

    assert cli.main(["probe", "--project-root", str(git_sandbox.home / "B")],
                    entry_kind="explicit-native", original_cwd=git_sandbox.home,
                    runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"), environment=git_sandbox.environment,
                    handlers={"probe": cli.Handler(handler, requires_input=True)}) == _INVALID
    assert "required input" in capsys.readouterr().err

@pytest.mark.parametrize("failure", [KeyboardInterrupt(), RuntimeError("handler failed")])
@pytest.mark.usefixtures("read_only_git")
def test_handler_failure(failure: BaseException, git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Handler exceptions and cancellation are failures with original details."""
    monkeypatch.setattr(cli, "stdin_is_console", lambda: False)

    def handler(_context: InvocationContext) -> OperationResult:
        raise failure

    assert cli.main(["probe", "--project-root", str(git_sandbox.home / "B")],
                    entry_kind="explicit-native", original_cwd=git_sandbox.home,
                    runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"), environment=git_sandbox.environment,
                    handlers={"probe": cli.Handler(handler)}) == 1
    expected = "interrupted" if isinstance(failure, KeyboardInterrupt) else "handler failed"
    assert expected in capsys.readouterr().err


@pytest.mark.parametrize("failure", [KeyboardInterrupt(), TypeError("preflight bug")])
def test_preflight_execution_failure(failure: BaseException, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Unexpected preflight failure differs from rejected input."""
    def failed() -> bool:
        raise failure

    monkeypatch.setattr(cli, "stdin_is_console", failed)
    assert cli.main(["probe"], entry_kind="explicit-native", original_cwd=tmp_path,
                    runtime=RuntimeIdentity(tmp_path, "venvs/prepared"),
                    handlers={"probe": cli.Handler(lambda _context: OperationResult())}) == 1
    expected = "interrupted" if isinstance(failure, KeyboardInterrupt) else "preflight bug"
    assert expected in capsys.readouterr().err


@pytest.mark.parametrize("explicit", [False, True])
def test_runtime_load(*, explicit: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Default source ownership and explicitly selected tooling roots are exact."""
    expected = tmp_path if explicit else Path(cli.__file__).resolve().parents[2]

    def load(root: Path) -> RuntimeIdentity:
        assert root == expected
        message = "test readiness boundary"
        raise ValueError(message)

    monkeypatch.setattr(cli.RuntimeIdentity, "load", load)
    assert cli.main(["probe"], entry_kind="explicit-native", original_cwd=tmp_path,
                    tooling_root=tmp_path if explicit else None,
                    handlers={"probe": cli.Handler(lambda _context: OperationResult())}) == _INVALID
    assert "test readiness boundary" in capsys.readouterr().err


def test_batch_text_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Even apparently safe free text must use a documented batch data channel."""
    assert cli.main(["probe", "--text", "hello"], entry_kind="explicit-batch", original_cwd=tmp_path,
                    handlers={"probe": cli.Handler(lambda _context: OperationResult())}) == _INVALID
    assert "UTF-8 file/stdin" in capsys.readouterr().err


# eof
