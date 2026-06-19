"""Tests for the new_draft interactive workflow and its helpers.

Cover slug re-prompting, version/worktree menus, the in-place and worktree
branch paths, the pyproject bump, the draft write, root resolution, argument
parsing, and the fatal-error handling. Also cover the non-interactive
--from-draft mode: flag parsing, draft-path and version resolution, the four
relocation branches, and the validation errors. The terminal seams (`ask_text`,
`select`) and the Git calls are monkeypatched so every branch runs without a TTY
or a real repository.
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

import pytest

from tools import new_draft_models as models
from tools import new_draft_workflow as workflow

_EXIT_OK = 0
_EXIT_CANCEL = 1
_EXIT_FATAL = 2


def _write_pyproject(root: Path, *, version: str = "0.3.0") -> None:
    """Write a minimal pyproject.toml with the given version into `root`."""
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "x"\nversion = "{version}"\n',
        encoding="utf-8",
    )


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
