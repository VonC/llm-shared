"""Tests for the new_draft CLI entry point and argument plumbing.

Cover project-root resolution, the --root argument parsing, the `_today`
helper, the fatal-error handling, and `main()` forwarding to `run`. The Git
discovery seam is monkeypatched so every branch runs without a real repository.

Fix (split): extracted from `test_new_draft_workflow.py` so each test file
stays under the size limit. The interactive workflow tests stay there and the
non-interactive --from-draft tests live in
`test_new_draft_workflow_from_draft.py`.
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

import pytest

from tools import new_draft_models as models
from tools import new_draft_workflow as workflow

_EXIT_OK = 0
_EXIT_FATAL = 2


def test_resolve_root_uses_explicit_root(tmp_path: Path) -> None:
    """_resolve_root resolves an explicit --root path."""
    namespace = argparse.Namespace(root=tmp_path)
    assert workflow._resolve_root(namespace) == tmp_path.resolve()


def test_resolve_root_discovers_when_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """_resolve_root falls back to discovery when --root is absent."""
    namespace = argparse.Namespace(root=None)

    def fake_find(start: Path) -> Path:
        del start
        return tmp_path

    monkeypatch.setattr(workflow, "find_project_root", fake_find)

    assert workflow._resolve_root(namespace) == tmp_path


def test_parse_args_defaults_root_to_none() -> None:
    """_parse_args leaves --root unset by default."""
    assert workflow._parse_args([]).root is None


def test_parse_args_reads_root() -> None:
    """_parse_args reads the --root path argument."""
    assert workflow._parse_args(["--root", "some/dir"]).root == Path("some/dir")


def test_today_returns_a_date() -> None:
    """_today returns a date instance."""
    assert isinstance(workflow._today(), datetime.date)


def test_log_fatal_exits_with_fatal_code(capsys: pytest.CaptureFixture[str]) -> None:
    """_log_fatal logs the error and exits with the fatal code."""
    with pytest.raises(SystemExit) as excinfo:
        workflow._log_fatal(models.NewDraftError("boom"))

    assert excinfo.value.code == _EXIT_FATAL
    assert "ERROR: boom" in capsys.readouterr().out


def test_main_returns_run_result(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main forwards argv to run and returns its result."""

    def fake_run(argv: object) -> int:
        del argv
        return _EXIT_OK

    monkeypatch.setattr(workflow, "run", fake_run)

    assert workflow.main(["--root", "."]) == _EXIT_OK


def test_main_converts_errors_to_fatal_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main turns an expected NewDraftError into the fatal exit code."""

    def fake_run(argv: object) -> int:
        del argv
        msg = "nope"
        raise models.NewDraftError(msg)

    monkeypatch.setattr(workflow, "run", fake_run)

    with pytest.raises(SystemExit) as excinfo:
        workflow.main([])

    assert excinfo.value.code == _EXIT_FATAL


# eof
