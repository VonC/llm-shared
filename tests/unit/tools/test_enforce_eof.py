"""Tests for the EOF enforcement tool shared root-resolution behavior.

Fix: Verify the tool reuses the shared `find_project_root` symbol from the
`tools` package instead of keeping a local copy.

Fix: Verify the tool builds its scan roots from the shared root helper result.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tools import enforce_eof
from tools import find_project_root as shared_find_project_root

if TYPE_CHECKING:
    import pytest


def test_enforce_eof_reuses_shared_find_project_root_symbol() -> None:
    """The EOF tool should reuse the shared project-root helper."""
    assert enforce_eof.find_project_root is shared_find_project_root


def test_enforce_eof_main_uses_shared_root_helper(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The EOF tool should derive its scan directories from the shared helper."""
    captured_roots: list[Path] = []

    def fake_find_project_root(start_path: Path) -> Path:
        assert start_path == Path(enforce_eof.__file__).parent
        return tmp_path

    def fake_iter_python_files(roots: list[Path]) -> tuple[Path, ...]:
        captured_roots.extend(roots)
        return ()

    monkeypatch.setattr(enforce_eof, "find_project_root", fake_find_project_root)
    monkeypatch.setattr(enforce_eof, "_iter_python_files", fake_iter_python_files)

    enforce_eof.main()

    assert captured_roots == [tmp_path / "src", tmp_path / "tools"]


# eof
