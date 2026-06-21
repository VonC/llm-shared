"""Tests for the new_draft non-interactive --from-draft mode.

Cover the --from-draft, --slug, --version, and layout flag parsing, the
draft-path and version resolution, the four relocation branches, the full
in-place and worktree runs, and the validation errors. The Git calls are
monkeypatched so every branch runs without a real repository.

Fix (split): extracted from `test_new_draft_workflow.py` so each test file
stays under the size limit. The interactive workflow tests stay there and the
CLI entry-point tests live in `test_new_draft_workflow_cli.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import new_draft_models as models
from tools import new_draft_workflow as workflow

_EXIT_OK = 0


def _write_version_txt(root: Path, *, first_line: str = "0.4.0 -- title") -> None:
    """Write a minimal version.txt with the given first line into `root`."""
    (root / "version.txt").write_text(f"{first_line}\n", encoding="utf-8")


def _write_source_draft(
    root: Path,
    *,
    name: str = "draft.topic.md",
    text: str = "# Draft topic\n",
) -> Path:
    """Write a source draft under `root/docs` and return its path."""
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    draft = docs / name
    draft.write_text(text, encoding="utf-8")
    return draft


def _no_collision(slug: str, *, cwd: Path) -> None:
    """Stub branch_collision that reports the slug as free."""
    del slug, cwd


def _local_collision(slug: str, *, cwd: Path) -> str:
    """Stub branch_collision that reports a local collision."""
    del slug, cwd
    return "local"


def _untracked(path: Path, *, cwd: Path) -> bool:
    """Stub path_is_tracked that reports the path as untracked."""
    del path, cwd
    return False


def _tracked(path: Path, *, cwd: Path) -> bool:
    """Stub path_is_tracked that reports the path as tracked."""
    del path, cwd
    return True


def test_parse_args_reads_from_draft_flags() -> None:
    """_parse_args reads the --from-draft, --slug, --version, and --worktree flags."""
    args = workflow._parse_args(
        [
            "--from-draft",
            "docs/d.md",
            "--slug",
            "topic",
            "--version",
            "1.2.3",
            "--worktree",
        ],
    )
    assert args.from_draft == Path("docs/d.md")
    assert args.slug == "topic"
    assert args.version == "1.2.3"
    assert args.use_worktree is True


def test_parse_args_in_place_sets_layout_false() -> None:
    """_parse_args records --in-place as a False worktree choice."""
    assert workflow._parse_args(["--in-place"]).use_worktree is False


def test_parse_args_layout_defaults_to_none() -> None:
    """_parse_args leaves the layout unset (None) when neither flag is given."""
    args = workflow._parse_args([])
    assert args.from_draft is None
    assert args.use_worktree is None


def test_resolve_draft_path_absolute_is_kept(tmp_path: Path) -> None:
    """_resolve_draft_path returns an absolute draft path unchanged."""
    absolute = (tmp_path / "docs" / "d.md").resolve()
    assert workflow._resolve_draft_path(absolute, tmp_path) == absolute


def test_resolve_draft_path_relative_joins_root(tmp_path: Path) -> None:
    """_resolve_draft_path joins a relative draft path onto the root."""
    assert (
        workflow._resolve_draft_path(Path("docs/d.md"), tmp_path)
        == tmp_path / "docs/d.md"
    )


def test_parse_version_arg_strips_leading_v() -> None:
    """_parse_version_arg accepts a leading v and surrounding whitespace."""
    assert workflow._parse_version_arg("v0.5.0") == models.SemanticVersion(0, 5, 0)
    assert workflow._parse_version_arg(" 0.5.0 ") == models.SemanticVersion(0, 5, 0)


def test_resolve_version_arg_uses_flag(tmp_path: Path) -> None:
    """_resolve_version_arg parses the flag value when one is given."""
    assert workflow._resolve_version_arg("0.5.0", tmp_path) == models.SemanticVersion(
        0,
        5,
        0,
    )


def test_resolve_version_arg_reads_version_txt(tmp_path: Path) -> None:
    """_resolve_version_arg falls back to version.txt when the flag is absent."""
    root = tmp_path.resolve()
    _write_version_txt(root, first_line="0.4.0 -- title")
    assert workflow._resolve_version_arg(None, root) == models.SemanticVersion(0, 4, 0)


def test_relocate_draft_in_place_tracked(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """In-place relocation of a tracked draft uses git_move."""
    moves: list[tuple[Path, Path, Path]] = []

    def fake_move(source: Path, target: Path, *, cwd: Path) -> None:
        moves.append((source, target, cwd))

    monkeypatch.setattr(workflow, "path_is_tracked", _tracked)
    monkeypatch.setattr(workflow, "git_move", fake_move)
    source = tmp_path / "docs" / "old.md"
    source.parent.mkdir(parents=True)
    source.write_text("body", encoding="utf-8")
    target = tmp_path / "docs" / "new.md"

    workflow._relocate_draft(source, target, source_cwd=tmp_path, target_cwd=tmp_path)

    assert moves == [(source, target, tmp_path)]


def test_relocate_draft_in_place_untracked(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """In-place relocation of an untracked draft renames it on the filesystem."""
    monkeypatch.setattr(workflow, "path_is_tracked", _untracked)
    source = tmp_path / "docs" / "old.md"
    source.parent.mkdir(parents=True)
    source.write_text("body", encoding="utf-8")
    target = tmp_path / "docs" / "new.md"

    workflow._relocate_draft(source, target, source_cwd=tmp_path, target_cwd=tmp_path)

    assert target.read_text(encoding="utf-8") == "body"
    assert not source.exists()


def test_relocate_draft_worktree_untracked_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Worktree relocation copies the text, stages it, and drops an untracked source."""
    staged: list[tuple[Path, Path]] = []

    def fake_stage(path: Path, *, cwd: Path) -> None:
        staged.append((path, cwd))

    monkeypatch.setattr(workflow, "stage_path", fake_stage)
    monkeypatch.setattr(workflow, "path_is_tracked", _untracked)
    source_cwd = tmp_path / "main"
    target_cwd = tmp_path / "wt"
    source = source_cwd / "docs" / "old.md"
    source.parent.mkdir(parents=True)
    source.write_text("draft body", encoding="utf-8")
    target = target_cwd / "docs" / "draft.v0.5.0.topic.md"

    workflow._relocate_draft(
        source,
        target,
        source_cwd=source_cwd,
        target_cwd=target_cwd,
    )

    assert target.read_text(encoding="utf-8") == "draft body"
    assert not source.exists()
    assert staged == [(target, target_cwd)]


def test_relocate_draft_worktree_tracked_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Worktree relocation also stages the deletion of a tracked source."""
    staged: list[tuple[Path, Path]] = []

    def fake_stage(path: Path, *, cwd: Path) -> None:
        staged.append((path, cwd))

    monkeypatch.setattr(workflow, "stage_path", fake_stage)
    monkeypatch.setattr(workflow, "path_is_tracked", _tracked)
    source_cwd = tmp_path / "main"
    target_cwd = tmp_path / "wt"
    source = source_cwd / "docs" / "old.md"
    source.parent.mkdir(parents=True)
    source.write_text("draft body", encoding="utf-8")
    target = target_cwd / "docs" / "draft.v0.5.0.topic.md"

    workflow._relocate_draft(
        source,
        target,
        source_cwd=source_cwd,
        target_cwd=target_cwd,
    )

    assert not source.exists()
    assert staged == [(target, target_cwd), (source, source_cwd)]


def test_run_from_draft_in_place(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A --from-draft --in-place run branches and renames the draft in place."""
    root = tmp_path.resolve()
    created: dict[str, object] = {}

    def fake_create(slug: str, *, cwd: Path) -> None:
        created["slug"] = slug
        created["cwd"] = cwd

    monkeypatch.setattr(workflow, "branch_collision", _no_collision)
    monkeypatch.setattr(workflow, "create_local_branch", fake_create)
    monkeypatch.setattr(workflow, "path_is_tracked", _untracked)
    source = _write_source_draft(root, text="# Draft topic\n")

    result = workflow.run(
        [
            "--root",
            str(root),
            "--from-draft",
            "docs/draft.topic.md",
            "--slug",
            "topic",
            "--version",
            "0.5.0",
            "--in-place",
        ],
    )

    assert result == _EXIT_OK
    assert created == {"slug": "topic", "cwd": root}
    target = root / "docs" / "draft.v0.5.0.topic.md"
    assert target.read_text(encoding="utf-8") == "# Draft topic\n"
    assert not source.exists()
    assert "Moved draft" in capsys.readouterr().out


def test_run_from_draft_worktree(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A --from-draft --worktree run writes the draft into the worktree docs."""
    root = tmp_path.resolve()
    staged: list[Path] = []

    def fake_add_worktree(worktree_path: Path, slug: str, *, cwd: Path) -> None:
        del slug, cwd
        worktree_path.mkdir(parents=True, exist_ok=True)

    def fake_stage(path: Path, *, cwd: Path) -> None:
        del cwd
        staged.append(path)

    monkeypatch.setattr(workflow, "branch_collision", _no_collision)
    monkeypatch.setattr(workflow, "add_worktree", fake_add_worktree)
    monkeypatch.setattr(workflow, "stage_path", fake_stage)
    monkeypatch.setattr(workflow, "path_is_tracked", _untracked)
    source = _write_source_draft(root, text="# Draft topic\n")

    result = workflow.run(
        [
            "--root",
            str(root),
            "--from-draft",
            "docs/draft.topic.md",
            "--slug",
            "topic",
            "--version",
            "0.5.0",
            "--worktree",
        ],
    )

    assert result == _EXIT_OK
    worktree = models.compute_worktree_path(root, "topic")
    target = worktree / "docs" / "draft.v0.5.0.topic.md"
    assert target.read_text(encoding="utf-8") == "# Draft topic\n"
    assert not source.exists()
    assert target in staged


def test_run_from_draft_defaults_version_from_version_txt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Without --version the run reads the current version from version.txt."""
    root = tmp_path.resolve()
    _write_version_txt(root, first_line="0.4.0 -- title")

    def fake_create(slug: str, *, cwd: Path) -> None:
        del slug, cwd

    monkeypatch.setattr(workflow, "branch_collision", _no_collision)
    monkeypatch.setattr(workflow, "create_local_branch", fake_create)
    monkeypatch.setattr(workflow, "path_is_tracked", _untracked)
    _write_source_draft(root, text="# Draft\n")

    result = workflow.run(
        [
            "--root",
            str(root),
            "--from-draft",
            "docs/draft.topic.md",
            "--slug",
            "topic",
            "--in-place",
        ],
    )

    assert result == _EXIT_OK
    assert (root / "docs" / "draft.v0.4.0.topic.md").exists()


def test_run_from_draft_requires_slug(tmp_path: Path) -> None:
    """--from-draft without --slug raises a NewDraftError."""
    root = tmp_path.resolve()
    with pytest.raises(models.NewDraftError, match="Provide a slug"):
        workflow.run(["--root", str(root), "--from-draft", "docs/d.md", "--in-place"])


def test_run_from_draft_rejects_collision(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--from-draft stops when the slug already names a branch."""
    root = tmp_path.resolve()
    monkeypatch.setattr(workflow, "branch_collision", _local_collision)

    with pytest.raises(models.NewDraftError, match="already exists"):
        workflow.run(
            [
                "--root",
                str(root),
                "--from-draft",
                "docs/d.md",
                "--slug",
                "topic",
                "--in-place",
            ],
        )


def test_run_from_draft_requires_layout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--from-draft without --worktree or --in-place raises a NewDraftError."""
    root = tmp_path.resolve()
    monkeypatch.setattr(workflow, "branch_collision", _no_collision)

    with pytest.raises(models.NewDraftError, match="Choose a layout"):
        workflow.run(
            ["--root", str(root), "--from-draft", "docs/d.md", "--slug", "topic"],
        )


def test_run_from_draft_missing_draft_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--from-draft stops when the draft path is not a file."""
    root = tmp_path.resolve()
    monkeypatch.setattr(workflow, "branch_collision", _no_collision)

    with pytest.raises(models.NewDraftError, match="Draft not found"):
        workflow.run(
            [
                "--root",
                str(root),
                "--from-draft",
                "docs/missing.md",
                "--slug",
                "topic",
                "--version",
                "0.5.0",
                "--in-place",
            ],
        )


# eof
