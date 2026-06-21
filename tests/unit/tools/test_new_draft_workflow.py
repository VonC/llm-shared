"""Tests for the new_draft interactive workflow menu path.

Cover slug re-prompting, the version and worktree menus, and the in-place and
worktree branch runs driven by the interactive prompts. The terminal seams
(`ask_text`, `select`) and the Git calls are monkeypatched so every branch runs
without a TTY or a real repository.

Fix (split): the CLI entry-point tests moved to
`test_new_draft_workflow_cli.py` and the non-interactive --from-draft tests to
`test_new_draft_workflow_from_draft.py`, so each test file stays under the size
limit while this file keeps the interactive workflow coverage.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import new_draft_models as models
from tools import new_draft_workflow as workflow

_EXIT_OK = 0
_EXIT_CANCEL = 1


def _write_pyproject(root: Path, *, version: str = "0.3.0") -> None:
    """Write a minimal pyproject.toml with the given version into `root`."""
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "x"\nversion = "{version}"\n',
        encoding="utf-8",
    )


def test_run_creates_branch_and_draft_in_place(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A full in-place run bumps pyproject and writes the draft on the new branch."""
    root = tmp_path.resolve()
    _write_pyproject(root)
    created: dict[str, object] = {}

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return "myslug"

    def fake_collision(slug: str, *, cwd: Path) -> str | None:
        del slug, cwd
        return None

    selections: list[object] = [models.SemanticVersion(0, 3, 1), False]

    def fake_select(message: str, options: list[tuple[str, object]]) -> object:
        del message, options
        return selections.pop(0)

    def fake_create(slug: str, *, cwd: Path) -> None:
        created["slug"] = slug
        created["cwd"] = cwd

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)
    monkeypatch.setattr(workflow, "branch_collision", fake_collision)
    monkeypatch.setattr(workflow, "select", fake_select)
    monkeypatch.setattr(workflow, "create_local_branch", fake_create)

    result = workflow.run(["--root", str(root)])

    assert result == _EXIT_OK
    assert created == {"slug": "myslug", "cwd": root}
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.3.0"' in pyproject  # pyproject is read, never rewritten
    draft = root / "docs" / "draft.v0.3.1.myslug.md"
    assert draft.exists()
    assert "# Draft v0.3.1 for myslug" in draft.read_text(encoding="utf-8")
    assert "Created branch 'myslug'" in capsys.readouterr().out


def test_run_creates_worktree_branch_and_draft(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A worktree run scaffolds branch, pyproject bump, and draft inside the worktree."""
    root = tmp_path.resolve()
    _write_pyproject(root)
    holder: dict[str, Path] = {}

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return "wtslug"

    def fake_collision(slug: str, *, cwd: Path) -> str | None:
        del slug, cwd
        return None

    selections: list[object] = [models.SemanticVersion(0, 4, 0), True]

    def fake_select(message: str, options: list[tuple[str, object]]) -> object:
        del message, options
        return selections.pop(0)

    def fake_add_worktree(worktree_path: Path, slug: str, *, cwd: Path) -> None:
        del slug, cwd
        worktree_path.mkdir(parents=True, exist_ok=True)
        holder["path"] = worktree_path

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)
    monkeypatch.setattr(workflow, "branch_collision", fake_collision)
    monkeypatch.setattr(workflow, "select", fake_select)
    monkeypatch.setattr(workflow, "add_worktree", fake_add_worktree)

    result = workflow.run(["--root", str(root)])

    assert result == _EXIT_OK
    expected = models.compute_worktree_path(root, "wtslug")
    assert holder["path"] == expected
    assert (expected / "docs" / "draft.v0.4.0.wtslug.md").exists()
    # The root pyproject is only read for the current version, never rewritten.
    assert 'version = "0.3.0"' in (root / "pyproject.toml").read_text(encoding="utf-8")


def test_run_cancels_when_no_slug(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Run returns the cancel code when the slug prompt is cancelled."""
    root = tmp_path.resolve()
    _write_pyproject(root)

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return None

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)

    result = workflow.run(["--root", str(root)])

    assert result == _EXIT_CANCEL
    assert "no slug" in capsys.readouterr().out


def test_run_cancels_when_no_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Run returns the cancel code when the version menu is cancelled."""
    root = tmp_path.resolve()
    _write_pyproject(root)

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return "myslug"

    def fake_collision(slug: str, *, cwd: Path) -> str | None:
        del slug, cwd
        return None

    def fake_select(message: str, options: list[tuple[str, object]]) -> object:
        del message, options
        return None

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)
    monkeypatch.setattr(workflow, "branch_collision", fake_collision)
    monkeypatch.setattr(workflow, "select", fake_select)

    result = workflow.run(["--root", str(root)])

    assert result == _EXIT_CANCEL
    assert "no version" in capsys.readouterr().out


def test_run_cancels_when_no_worktree_choice(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Run returns the cancel code when the worktree menu is cancelled."""
    root = tmp_path.resolve()
    _write_pyproject(root)
    selections: list[object] = [models.SemanticVersion(0, 3, 1), None]

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return "myslug"

    def fake_collision(slug: str, *, cwd: Path) -> str | None:
        del slug, cwd
        return None

    def fake_select(message: str, options: list[tuple[str, object]]) -> object:
        del message, options
        return selections.pop(0)

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)
    monkeypatch.setattr(workflow, "branch_collision", fake_collision)
    monkeypatch.setattr(workflow, "select", fake_select)

    result = workflow.run(["--root", str(root)])

    assert result == _EXIT_CANCEL
    assert "no worktree" in capsys.readouterr().out


def test_prompt_valid_slug_retries_until_free(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """_prompt_valid_slug re-prompts past an invalid slug and a taken branch."""
    raws: list[str] = ["with space", "taken", "good"]
    collisions: list[str | None] = ["local", None]

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return raws.pop(0)

    def fake_collision(slug: str, *, cwd: Path) -> str | None:
        del slug, cwd
        return collisions.pop(0)

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)
    monkeypatch.setattr(workflow, "branch_collision", fake_collision)

    assert workflow._prompt_valid_slug(tmp_path) == "good"


def test_prompt_valid_slug_cancel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """_prompt_valid_slug returns None when the text prompt is cancelled."""

    def fake_ask_text(message: str, *, default: str = "") -> str | None:
        del message, default
        return None

    monkeypatch.setattr(workflow, "ask_text", fake_ask_text)

    assert workflow._prompt_valid_slug(tmp_path) is None


def test_prompt_version_offers_three_bumps(monkeypatch: pytest.MonkeyPatch) -> None:
    """_prompt_version offers patch/minor/major labels and returns the choice."""
    recorded_labels: list[str] = []

    def fake_select(
        message: str,
        options: list[tuple[str, models.SemanticVersion]],
    ) -> models.SemanticVersion:
        del message
        recorded_labels.extend(label for label, _ in options)
        return options[1][1]

    monkeypatch.setattr(workflow, "select", fake_select)

    chosen = workflow._prompt_version(models.SemanticVersion(1, 2, 3))

    assert chosen == models.SemanticVersion(1, 3, 0)
    assert recorded_labels == ["patch -> 1.2.4", "minor -> 1.3.0", "major -> 2.0.0"]


@pytest.mark.parametrize("choice", [True, False, None])
def test_prompt_worktree_returns_choice(
    monkeypatch: pytest.MonkeyPatch,
    choice: object,
) -> None:
    """_prompt_worktree returns the selected yes/no/cancel value verbatim."""

    def fake_select(message: str, options: list[tuple[str, object]]) -> object:
        del message, options
        return choice

    monkeypatch.setattr(workflow, "select", fake_select)

    assert workflow._prompt_worktree(Path("repo/worktree")) is choice


# eof
