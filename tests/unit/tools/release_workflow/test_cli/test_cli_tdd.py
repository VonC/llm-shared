"""Dispatch isolates Git probes while preserving real context and failure policies.

Step 1 of v0.14.0 version-sources: trailing operation tokens parse around the
options, reach a handler's argument validator and the invocation context, and
are rejected with status 2 by a handler without a validator. A validator
failure stops before any identity load or Git context creation. Step 9 ships
exactly `version` and `versions`.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import cli
from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.results import OperationResult
from tools.release_workflow.runtime_identity import RuntimeIdentity

if TYPE_CHECKING:
    from typing import NoReturn

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.invocation import InvocationContext

_INVALID = 2
_TOKENS = ("set", "0.14.0")


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


@pytest.mark.parametrize("layout", ["after", "before", "between", "first"])
@pytest.mark.usefixtures("read_only_git")
def test_operation_tokens_reach_validator_and_context(layout: str, git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch,
                                                      capsys: pytest.CaptureFixture[str]) -> None:
    """Options before, between and after the tokens parse the same way."""
    monkeypatch.setattr(cli, "stdin_is_console", lambda: False)
    root = ["--project-root", str(git_sandbox.home / "B")]
    argv = {"after": ["versions", *_TOKENS, *root], "before": ["versions", *root, *_TOKENS],
            "between": ["versions", "set", *root, "0.14.0"], "first": [*root, "versions", *_TOKENS]}[layout]
    validated: list[tuple[str, ...]] = []

    def handler(context: InvocationContext) -> OperationResult:
        return OperationResult(data=" ".join(context.operation) + "\n")

    status = cli.main(argv, entry_kind="explicit-native", original_cwd=git_sandbox.home,
                      runtime=RuntimeIdentity(git_sandbox.home, "venvs/prepared"), environment=git_sandbox.environment,
                      handlers={"versions": cli.Handler(handler, validate_arguments=validated.append)})
    assert status == 0, capsys.readouterr().err
    assert validated == [_TOKENS]
    assert capsys.readouterr().out == "set 0.14.0\n"


def test_handler_without_validator_rejects_tokens(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """An operation that declares no validator takes no trailing token."""
    assert cli.main(["probe", "extra"], entry_kind="explicit-native", original_cwd=tmp_path,
                    runtime=RuntimeIdentity(tmp_path, "venvs/prepared"),
                    handlers={"probe": cli.Handler(lambda _context: OperationResult())}) == _INVALID
    assert "Release operation 'probe' takes no arguments: extra" in capsys.readouterr().err


def test_validator_failure_precedes_identity_and_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                     capsys: pytest.CaptureFixture[str]) -> None:
    """A rejected token returns 2 before any identity load or Git process."""
    calls: list[str] = []

    def git_created(*_arguments: object, **_options: object) -> NoReturn:
        calls.append("git")
        raise AssertionError

    def identity_loaded(_root: Path) -> NoReturn:
        calls.append("identity")
        raise AssertionError

    def reject(tokens: tuple[str, ...]) -> None:
        message = f"Unsupported version token: {tokens[-1]}"
        raise ValueError(message)

    monkeypatch.setattr(GitExecutionContext, "create", git_created)
    monkeypatch.setattr(cli.RuntimeIdentity, "load", identity_loaded)
    assert cli.main(["versions", "set", "v0.14.0"], entry_kind="explicit-native", original_cwd=tmp_path,
                    handlers={"versions": cli.Handler(lambda _context: OperationResult(), validate_arguments=reject)}) == _INVALID
    assert calls == []
    assert "Unsupported version token: v0.14.0" in capsys.readouterr().err


def test_unavailable_operation_message_is_unchanged(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Tokens after an unshipped command keep the unavailable-operation message."""
    assert cli.main(["missing", "set", "0.14.0"], entry_kind="explicit-native", original_cwd=tmp_path,
                    runtime=RuntimeIdentity(tmp_path, "venvs/prepared"), handlers={}) == _INVALID
    assert "Release operation 'missing' is unavailable in this tooling checkout" in capsys.readouterr().err


def test_only_the_version_commands_ship() -> None:
    """Step 9 ships `version` and `versions`; no other operation is registered."""
    assert set(cli.SHIPPED_HANDLERS) == {"version", "versions"}


# eof
