"""Tests for composable installation of sensitive Git hooks."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

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


def _repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(  # noqa: S603
        ["git", "init", "-b", "main"],  # noqa: S607
        cwd=path,
        check=True,
        capture_output=True,
    )
    return path


def test_install_is_idempotent_and_preserves_an_existing_hook(tmp_path: Path) -> None:
    """A dispatcher adopts existing work and gains one managed sensitive entry."""
    repo = _repo(tmp_path / "repo")
    hooks = _git_path(repo, "hooks")
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


def test_shared_rules_config_is_absolute_and_idempotent(tmp_path: Path) -> None:
    """Hook repositories retain an explicit machine-local common rules path."""
    repo = _repo(tmp_path / "repo")
    shared = tmp_path / "common.rules"
    shared.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")

    assert _configure_shared_rules(repo, shared)
    configured = subprocess.run(  # noqa: S603
        ["git", "config", "--path", "--get", "sensitive.sharedRulesFile"],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    assert Path(configured).resolve() == shared.resolve()
    assert not _configure_shared_rules(repo, shared)
    with pytest.raises(HookInstallError, match="not found"):
        _configure_shared_rules(repo, tmp_path / "missing.rules")


def test_shared_rules_config_reports_git_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Git config failure stops installation before hooks become misleading."""
    repo = _repo(tmp_path / "repo")
    shared = tmp_path / "common.rules"
    shared.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")

    def failed_git(*_args, **_kwargs):  # noqa: ANN002, ANN003, ANN202
        message = "git unavailable"
        raise OSError(message)

    monkeypatch.setattr(subprocess, "run", failed_git)
    with pytest.raises(HookInstallError, match="cannot configure"):
        _configure_shared_rules(repo, shared)


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


def test_git_path_and_main_report_success_and_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI reports installs, checks, and invalid repositories."""
    repo = _repo(tmp_path / "repo")
    shared = tmp_path / "shared"

    assert _git_path(repo, "hooks").name == "hooks"
    rules = tmp_path / "common.rules"
    rules.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")
    arguments = [
        str(repo),
        "--shared-root",
        str(shared),
        "--shared-rules",
        str(rules),
    ]
    assert main(arguments) == 0
    assert "installed" in capsys.readouterr().out
    assert main(arguments) == 0
    assert "already installed" in capsys.readouterr().out
    assert main([str(tmp_path / "absent")]) == 1
    assert "ERROR" in capsys.readouterr().err


def test_install_reports_preserved_target_collision(tmp_path: Path) -> None:
    """The public installer propagates safe-adoption failures."""
    repo = _repo(tmp_path / "repo")
    hooks = _git_path(repo, "hooks")
    (hooks / "pre-commit").write_text("new user hook", encoding="utf-8")
    chain = hooks / "pre-commit.d"
    chain.mkdir()
    (chain / "50-existing").write_text("old user hook", encoding="utf-8")

    with pytest.raises(HookInstallError, match="already exists"):
        install_hooks(repo, tmp_path / "shared")


def test_installed_hooks_block_blob_and_message_then_allow_clean_commit(
    tmp_path: Path,
) -> None:
    """Real Git commits exercise both generated dispatchers and lean adapters."""
    repo = _repo(tmp_path / "repo")
    subprocess.run(  # noqa: S603
        ["git", "config", "user.name", "Hook Tests"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    subprocess.run(  # noqa: S603
        ["git", "config", "user.email", "hooks@example.invalid"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    shared_rules = tmp_path / "a.sensitive.replacements.local.txt"
    shared_rules.write_text(
        "literal:BlockedHookTerm==>redacted\n",
        encoding="utf-8",
    )
    (repo / "a.sensitive.replacements.local.txt").write_text("", encoding="utf-8")
    install_hooks(repo, Path(__file__).parents[4], shared_rules)

    candidate = repo / "candidate.txt"
    candidate.write_text("contains BlockedHookTerm\n", encoding="utf-8")
    subprocess.run(  # noqa: S603
        ["git", "add", "candidate.txt"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    blob_result = subprocess.run(  # noqa: S603
        ["git", "commit", "-m", "safe message"],  # noqa: S607
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert blob_result.returncode != 0
    assert "candidate.txt:1" in blob_result.stderr
    assert "BlockedHookTerm" not in blob_result.stderr

    candidate.write_text("safe content\n", encoding="utf-8")
    subprocess.run(  # noqa: S603
        ["git", "add", "candidate.txt"],  # noqa: S607
        cwd=repo,
        check=True,
    )
    message_result = subprocess.run(  # noqa: S603
        ["git", "commit", "-m", "BlockedHookTerm message"],  # noqa: S607
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert message_result.returncode != 0
    assert "commit message line 1" in message_result.stderr
    assert "BlockedHookTerm" not in message_result.stderr

    clean_result = subprocess.run(  # noqa: S603
        ["git", "commit", "-m", "safe message"],  # noqa: S607
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert clean_result.returncode == 0, clean_result.stderr
