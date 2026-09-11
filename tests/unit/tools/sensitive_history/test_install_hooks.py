"""Tests for composable installation of sensitive Git hooks.

Fix: the ``subprocess.run`` stand-in is fully typed (``object`` parameters
and a ``NoReturn`` return), so the strict pyright gate no longer flags
unknown parameter or argument types on the monkeypatched double.
Collision propagation injects Git path discovery because repository plumbing
is covered separately and is not part of that behavior.
CLI and generated-hook contracts use recorded Git results, so installer tests
do not create repositories or execute commits.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NoReturn

import pytest

import tools.sensitive_history.install_hooks as hook_installer
from tools.sensitive_history.install_hooks import (
    DISPATCHER_MARKER,
    HookInstallError,
    _adopt_existing_hook,
    _configure_shared_rules,
    _dispatcher,
    _entry,
    _git_path,
    _shell_quote,
    _write_executable,
    install_hooks,
    main,
)


def test_install_is_idempotent_and_preserves_an_existing_hook(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A dispatcher adopts existing work and gains one managed sensitive entry."""
    repo = tmp_path / "repo"
    repo.mkdir()
    hooks = repo / "hooks"
    hooks.mkdir()

    def fake_git_path(candidate: Path, name: str) -> Path:
        assert candidate == repo.resolve()
        assert name == "hooks"
        return hooks

    monkeypatch.setattr(hook_installer, "_git_path", fake_git_path)
    existing = hooks / "pre-commit"
    existing.write_text("#!/bin/sh\necho existing\n", encoding="utf-8")

    changes = install_hooks(repo, tmp_path / "llm-shared")

    assert "preserved existing pre-commit" in changes
    assert DISPATCHER_MARKER in existing.read_text(encoding="utf-8")
    assert (hooks / "pre-commit.d" / "50-existing").read_text(encoding="utf-8").endswith(
        "echo existing\n",
    )
    entry = (hooks / "pre-commit.d" / "90-sensitive").read_text(encoding="utf-8")
    assert "sensitive_pre_commit.py" in entry
    assert install_hooks(repo, tmp_path / "llm-shared") == ()


def test_shared_rules_config_is_absolute_and_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hook repositories retain an explicit machine-local common rules path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    shared = tmp_path / "common.rules"
    shared.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")
    configured: Path | None = None

    def config_run(
        args: list[str],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        nonlocal configured
        if "--get" in args:
            output = "" if configured is None else f"{configured}\n"
            return subprocess.CompletedProcess(args, int(configured is None), output, "")
        configured = Path(args[-1])
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", config_run)

    assert _configure_shared_rules(repo, shared)
    assert configured is not None
    assert configured.resolve() == shared.resolve()
    assert not _configure_shared_rules(repo, shared)
    with pytest.raises(HookInstallError, match="not found"):
        _configure_shared_rules(repo, tmp_path / "missing.rules")


def test_shared_rules_config_reports_git_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Git config failure stops installation before hooks become misleading."""
    repo = tmp_path / "repo"
    repo.mkdir()
    shared = tmp_path / "common.rules"
    shared.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")

    def failed_git(*_args: object, **_kwargs: object) -> NoReturn:
        message = "git unavailable"
        raise OSError(message)

    monkeypatch.setattr(subprocess, "run", failed_git)
    with pytest.raises(HookInstallError, match="cannot configure"):
        _configure_shared_rules(repo, shared)


def test_git_path_parses_relative_output_and_translates_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Git-path discovery resolves output and wraps command failures."""
    repo = tmp_path / "repo"
    repo.mkdir()
    failing = False

    def git_path_result(
        command: list[str],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if failing:
            raise subprocess.CalledProcessError(1, command)
        return subprocess.CompletedProcess(command, 0, ".git/hooks\n", "")

    monkeypatch.setattr(subprocess, "run", git_path_result)
    assert _git_path(repo, "hooks") == (repo / ".git" / "hooks").resolve()

    failing = True
    with pytest.raises(HookInstallError, match="cannot resolve Git 'hooks' path"):
        _git_path(repo, "hooks")


def test_dispatcher_and_entry_are_small_composable_shell_scripts(tmp_path: Path) -> None:
    """Generated files dispatch by hook name and quote installation paths."""
    quoted = _shell_quote(tmp_path / "it's shared")
    entry = _entry(tmp_path / "python.exe", tmp_path / "it's shared" / "hook.py")

    assert "pre-commit" not in _dispatcher()
    assert '"$hook" "$@" || exit $?' in _dispatcher()
    assert "'\"'\"'" in quoted
    assert "python.exe" in entry
    assert "hook.py" in entry


def test_write_executable_updates_only_changed_content(tmp_path: Path) -> None:
    """Repeated checks do not rewrite an already-correct hook."""
    path = tmp_path / "hook"
    assert _write_executable(path, "one\n")
    assert not _write_executable(path, "one\n")
    assert _write_executable(path, "two\n")
    assert path.read_text(encoding="utf-8") == "two\n"


def test_existing_hook_collision_fails_without_overwriting(tmp_path: Path) -> None:
    """An ambiguous preserved-hook target requires manual resolution."""
    hook = tmp_path / "pre-commit"
    chain = tmp_path / "pre-commit.d"
    chain.mkdir()
    hook.write_text("user hook", encoding="utf-8")
    (chain / "50-existing").write_text("older hook", encoding="utf-8")

    with pytest.raises(HookInstallError, match="already exists"):
        _adopt_existing_hook(hook, chain)
    hook.unlink()
    _adopt_existing_hook(hook, chain)


@pytest.fixture
def git_path_main_results(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[str, int, str, int, str, int, str]:
    """Run CLI behavior through recorded path and configuration boundaries."""
    repo = tmp_path / "repo"
    repo.mkdir()
    hooks = repo / ".git" / "hooks"
    hooks.mkdir(parents=True)
    shared = tmp_path / "shared"
    configured = False

    def fake_git_path(candidate: Path, name: str) -> Path:
        if not candidate.is_dir():
            message = f"not a Git repository: {candidate}"
            raise HookInstallError(message)
        assert name == "hooks"
        return hooks

    def configure_rules(_repo: Path, _rules: Path | None) -> bool:
        nonlocal configured
        changed = not configured
        configured = True
        return changed

    monkeypatch.setattr(hook_installer, "_git_path", fake_git_path)
    monkeypatch.setattr(hook_installer, "_configure_shared_rules", configure_rules)

    hooks_name = fake_git_path(repo, "hooks").name
    rules = tmp_path / "common.rules"
    rules.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")
    arguments = [
        str(repo),
        "--shared-root",
        str(shared),
        "--shared-rules",
        str(rules),
    ]
    first_status = main(arguments)
    first_output = capsys.readouterr().out
    second_status = main(arguments)
    second_output = capsys.readouterr().out
    absent_status = main([str(tmp_path / "absent")])
    absent_error = capsys.readouterr().err
    return (
        hooks_name,
        first_status,
        first_output,
        second_status,
        second_output,
        absent_status,
        absent_error,
    )


def test_git_path_and_main_report_success_and_failure(
    git_path_main_results: tuple[str, int, str, int, str, int, str],
) -> None:
    """The CLI reports installs, checks, and invalid repositories."""
    (
        hooks_name,
        first_status,
        first_output,
        second_status,
        second_output,
        absent_status,
        absent_error,
    ) = git_path_main_results

    assert hooks_name == "hooks"
    assert first_status == 0
    assert "installed" in first_output
    assert second_status == 0
    assert "already installed" in second_output
    assert absent_status == 1
    assert "ERROR" in absent_error


def test_install_reports_preserved_target_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public installer propagates safe-adoption failures."""
    repo = tmp_path / "repo"
    repo.mkdir()
    hooks = repo / "hooks"
    hooks.mkdir()

    def fake_git_path(candidate: Path, name: str) -> Path:
        assert candidate == repo.resolve()
        assert name == "hooks"
        return hooks

    monkeypatch.setattr(hook_installer, "_git_path", fake_git_path)
    (hooks / "pre-commit").write_text("new user hook", encoding="utf-8")
    chain = hooks / "pre-commit.d"
    chain.mkdir()
    (chain / "50-existing").write_text("old user hook", encoding="utf-8")

    with pytest.raises(HookInstallError, match="already exists"):
        install_hooks(repo, tmp_path / "shared")


def test_installed_hooks_route_blob_and_message_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Both generated dispatchers route to their exact lean adapters."""
    repo = tmp_path / "repo"
    hooks = repo / "hooks"
    hooks.mkdir(parents=True)

    def fake_git_path(_candidate: Path, name: str) -> Path:
        assert name == "hooks"
        return hooks

    def configured(_repo: Path, _rules: Path | None) -> bool:
        return True

    monkeypatch.setattr(hook_installer, "_git_path", fake_git_path)
    monkeypatch.setattr(hook_installer, "_configure_shared_rules", configured)
    install_hooks(repo, Path(__file__).parents[4], tmp_path / "shared.rules")

    pre_commit = (hooks / "pre-commit").read_text(encoding="utf-8")
    commit_message = (hooks / "commit-msg").read_text(encoding="utf-8")
    blob_entry = (hooks / "pre-commit.d" / "90-sensitive").read_text(
        encoding="utf-8",
    )
    message_entry = (hooks / "commit-msg.d" / "90-sensitive").read_text(
        encoding="utf-8",
    )

    assert DISPATCHER_MARKER in pre_commit
    assert DISPATCHER_MARKER in commit_message
    assert "sensitive_pre_commit.py" in blob_entry
    assert "sensitive_commit_msg.py" in message_entry
