"""Tests for the new_draft script hub: delegation and __main__ execution.

Cover the hub's `main` delegation to the workflow and a full `__main__` run via
`runpy`, which exercises the import-path bootstrap and the bottom
`raise SystemExit(main())` guard. The terminal seams and Git call on the cached
workflow module are monkeypatched so the run completes without a TTY.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from tools import new_draft as new_draft_script
from tools import new_draft_models as models
from tools import new_draft_workflow as workflow

_EXIT_OK = 0


def test_main_delegates_to_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    """The hub main forwards argv to the workflow main and returns its result."""
    received: dict[str, object] = {}

    def fake_workflow_main(argv: object = None) -> int:
        received["argv"] = argv
        return _EXIT_OK

    monkeypatch.setattr(new_draft_script, "_workflow_main", fake_workflow_main)

    assert new_draft_script.main(["--root", "."]) == _EXIT_OK
    assert received["argv"] == ["--root", "."]


def test_script_runs_as_main_and_exits_zero(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Running the hub as __main__ scaffolds the effort and exits with code 0."""
    root = tmp_path.resolve()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "0.3.0"\n',
        encoding="utf-8",
    )
    script_path = Path(new_draft_script.__file__)
    expected_root = str(script_path.parent.parent.resolve())
    original_sys_path = list(sys.path)
    selections: list[object] = [models.SemanticVersion(0, 3, 1), False]

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return "entryslug"

    def fake_collision(slug: str, *, cwd: Path) -> str | None:
        del slug, cwd
        return None

    def fake_select(message: str, options: list[tuple[str, object]]) -> object:
        del message, options
        return selections.pop(0)

    def fake_create(slug: str, *, cwd: Path) -> None:
        del slug, cwd

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)
    monkeypatch.setattr(workflow, "branch_collision", fake_collision)
    monkeypatch.setattr(workflow, "select", fake_select)
    monkeypatch.setattr(workflow, "create_local_branch", fake_create)
    monkeypatch.setattr(sys, "argv", [str(script_path), "--root", str(root)])

    try:
        with pytest.raises(SystemExit) as excinfo:
            runpy.run_path(str(script_path), run_name="__main__")

        assert excinfo.value.code == _EXIT_OK
        assert expected_root in sys.path
        assert (root / "docs" / "draft.v0.3.1.entryslug.md").exists()
    finally:
        sys.path[:] = original_sys_path


# eof
