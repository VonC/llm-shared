"""Tests for EOF enforcement helper branches and script execution.

Fix: Cover file iteration, file rewriting, error handling, and `__main__`
execution in `tools.enforce_eof`.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import tools
from tools import enforce_eof

if TYPE_CHECKING:
    import pytest

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


def test_iter_python_files_yields_only_python_files_from_existing_roots(
    tmp_path: Path,
) -> None:
    """Python-file iteration should skip missing roots, non-Python files, and cache dirs."""
    tools_root = tmp_path / "tools"
    nested_root = tools_root / "nested"
    cache_root = tools_root / "__pycache__"
    nested_root.mkdir(parents=True)
    cache_root.mkdir(parents=True)
    python_file = nested_root / "example.py"
    python_file.write_text("print('ok')\n", encoding="utf-8")
    (nested_root / "notes.txt").write_text("ignore", encoding="utf-8")
    (cache_root / "cached.py").write_text("print('ignore')\n", encoding="utf-8")

    result = list(enforce_eof._iter_python_files([tmp_path / "missing", tools_root]))

    assert result == [python_file]


def test_process_file_rewrites_duplicate_eof_markers(tmp_path: Path) -> None:
    """File processing should strip duplicate EOF markers before rewriting one clean tail."""
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hi')\n\n# eof\n\n# eof\n", encoding="utf-8")

    assert enforce_eof._process_file(file_path) is True
    assert file_path.read_text(encoding="utf-8") == "print('hi')\n\n\n# eof\n"


def test_process_file_returns_false_when_content_is_already_normalized(
    tmp_path: Path,
) -> None:
    """File processing should report no change when the EOF tail is already correct."""
    file_path = tmp_path / "example.py"
    file_path.write_text("print('hi')\n\n\n# eof\n", encoding="utf-8")

    assert enforce_eof._process_file(file_path) is False


def test_process_file_logs_oserror_for_missing_files(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """File-processing failures should be logged and reported as no-op results."""
    missing_file = tmp_path / "missing.py"
    caplog.set_level("ERROR")

    assert enforce_eof._process_file(missing_file) is False
    assert "Error processing file" in caplog.text


def test_main_logs_updated_files_and_summary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Main execution should count scanned files and log updated relative paths."""
    scanned_files = [tmp_path / "tools" / "one.py", tmp_path / "src" / "two.py"]

    def fake_iter_python_files(roots: list[Path]) -> list[Path]:
        assert roots == [tmp_path / "src", tmp_path / "tools"]
        return scanned_files

    def fake_process_file(file_path: Path) -> bool:
        return file_path.name == "one.py"

    def fake_find_project_root(_start_path: Path) -> Path:
        return tmp_path

    monkeypatch.setattr(enforce_eof, "find_project_root", fake_find_project_root)
    monkeypatch.setattr(enforce_eof, "_iter_python_files", fake_iter_python_files)
    monkeypatch.setattr(enforce_eof, "_process_file", fake_process_file)
    caplog.set_level("INFO")

    enforce_eof.main()

    assert (
        "Updated: tools\\one.py" in caplog.text
        or "Updated: tools/one.py" in caplog.text
    )
    assert "Total Python files scanned: 2" in caplog.text
    assert "Files updated: 1" in caplog.text


def test_main_logs_when_project_root_lookup_fails(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Main execution should log a root-resolution error without re-raising."""

    def fake_find_project_root(_start_path: Path) -> Path:
        msg = "missing root"
        raise FileNotFoundError(msg)

    monkeypatch.setattr(
        enforce_eof,
        "find_project_root",
        fake_find_project_root,
    )
    caplog.set_level("ERROR")

    enforce_eof.main()

    assert "Error finding project root" in caplog.text


def test_main_logs_when_file_system_errors_occur(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Main execution should log unexpected file-system errors without re-raising."""

    def fake_find_project_root(_start_path: Path) -> Path:
        msg = "disk error"
        raise OSError(msg)

    monkeypatch.setattr(
        enforce_eof,
        "find_project_root",
        fake_find_project_root,
    )
    caplog.set_level("ERROR")

    enforce_eof.main()

    assert "An unexpected file system error occurred" in caplog.text


def test_enforce_eof_script_runs_as_main(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Running the script as `__main__` should insert project paths and call `main()`."""
    expected_root = Path(enforce_eof.__file__).parent.parent.resolve()
    expected_src = (expected_root / "src").resolve()
    script_path = Path(enforce_eof.__file__)
    (tmp_path / "src").mkdir()
    (tmp_path / "tools").mkdir()
    original_sys_path = list(sys.path)

    def fake_find_project_root(_start_path: Path) -> Path:
        return tmp_path

    monkeypatch.setattr(tools, "find_project_root", fake_find_project_root)

    try:
        runpy.run_path(str(script_path), run_name="__main__")
        assert str(expected_root) in sys.path
        assert str(expected_src) in sys.path
    finally:
        sys.path[:] = original_sys_path


# eof
