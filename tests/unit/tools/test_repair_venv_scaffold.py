"""Tests for the non-destructive project venv scaffold repair."""

from __future__ import annotations

import logging
import venv
from typing import TYPE_CHECKING

import pytest

from tools import repair_venv_scaffold

if TYPE_CHECKING:
    from pathlib import Path


def test_repair_restores_activation_without_replacing_python(tmp_path: Path) -> None:
    """A missing activation script is restored around the existing interpreter."""
    env_dir = tmp_path / "env"
    venv.EnvBuilder(with_pip=False).create(env_dir)
    config, python, activation = repair_venv_scaffold._required_paths(env_dir)
    python_before = python.read_bytes()
    activation.unlink()

    repaired = repair_venv_scaffold.repair_scaffold(env_dir)

    assert repaired == (activation,)
    assert config.is_file()
    assert activation.is_file()
    assert python.read_bytes() == python_before


def test_repair_creates_a_missing_scaffold(tmp_path: Path) -> None:
    """A missing venv receives its config, interpreter, and activation script."""
    env_dir = tmp_path / "env"

    repaired = repair_venv_scaffold.repair_scaffold(env_dir)

    required = repair_venv_scaffold._required_paths(env_dir)
    assert repaired == required
    assert all(path.is_file() for path in required)
    assert repair_venv_scaffold.repair_scaffold(env_dir) == ()


def test_repair_reports_missing_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A broken stdlib script setup cannot look like a successful repair."""
    monkeypatch.setattr(venv.EnvBuilder, "setup_scripts", lambda *_args: None)

    with pytest.raises(
        repair_venv_scaffold.VenvScaffoldError,
        match="activate",
    ):
        repair_venv_scaffold.repair_scaffold(tmp_path / "env")


def test_main_reports_success_and_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The batch-facing entry point returns stable success and failure codes."""
    env_dir = tmp_path / "env"
    repaired_path = env_dir / "activate.bat"
    monkeypatch.setattr(
        repair_venv_scaffold,
        "repair_scaffold",
        lambda _path: (repaired_path,),
    )

    with caplog.at_level(logging.INFO):
        assert repair_venv_scaffold.main([str(env_dir)]) == 0
    assert "activate.bat" in caplog.text

    def fail(_path: Path) -> tuple[Path, ...]:
        message = "broken"
        raise repair_venv_scaffold.VenvScaffoldError(message)

    monkeypatch.setattr(repair_venv_scaffold, "repair_scaffold", fail)
    assert repair_venv_scaffold.main([str(env_dir)]) == 1
    assert "Venv scaffold repair failed" in caplog.text


def test_main_requires_one_venv_path() -> None:
    """The batch-facing entry point rejects ambiguous arguments."""
    with pytest.raises(SystemExit, match="usage"):
        repair_venv_scaffold.main([])
