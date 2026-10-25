"""Prove artifact loading is read-only and preparation reuses existing policy."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.artifacts import (
    ArtifactError,
    prepare_artifacts,
    resolve_artifacts,
)
from tools.release_workflow.paths import ProjectIdentity

if TYPE_CHECKING:
    from os import stat_result

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox


@pytest.mark.parametrize("home", [".reviews", "scratch/release"])
def test_read_only_resolution_and_explicit_preparation(git_sandbox: GitSandbox, home: str) -> None:
    """Loading does not initialize the home or migrate legacy scratch files."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    if home != ".reviews":
        (root / ".review-artifacts.ini").write_text(f"[review-artifacts]\nhome={home}\n", encoding="utf-8")
    legacy = root / "a.legacy.txt"
    legacy.write_bytes(b"unchanged")
    declaration = resolve_artifacts(project, git_sandbox.context())
    assert declaration.home == root / home
    assert not declaration.home.exists()
    assert not hasattr(declaration, "prepare_home")
    prepared = prepare_artifacts(declaration, git_sandbox.context())
    assert prepared.home == declaration.home
    assert (prepared.home / ".gitignore").read_bytes() == b"*\n"
    assert legacy.read_bytes() == b"unchanged"
    assert prepare_artifacts(declaration, git_sandbox.context()).home == prepared.home


def test_invalid_and_tracked_artifact_homes_are_preflight_failures(git_sandbox: GitSandbox) -> None:
    """The controlled project's index determines tracking without preparation."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    source = root / ".review-artifacts.ini"
    source.write_text("invalid", encoding="utf-8")
    with pytest.raises(ArtifactError) as invalid:
        resolve_artifacts(project, git_sandbox.context())
    expected_status = 2
    assert invalid.value.exit_code == expected_status
    source.write_text("[review-artifacts]\nhome=sub\n", encoding="utf-8")
    (root / "sub/tracked").write_bytes(b"tracked")
    git_sandbox.git(["add", "sub/tracked"], cwd=root)
    with pytest.raises(ArtifactError, match="tracked"):
        resolve_artifacts(project, git_sandbox.context())
    assert not (root / "sub/.gitignore").exists()


def test_unc_home_is_rejected_before_any_network_probe(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid UNC declarations retain the helper diagnostic without touching SMB."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    source = root / ".review-artifacts.ini"
    content = b"[review-artifacts]\nhome=\\\\unreachable.invalid\\share\\home\n"
    source.write_bytes(content)
    stat = Path.stat

    def local_stat(path: Path, *, follow_symlinks: bool = True) -> stat_result:
        assert not path.drive.startswith("\\\\"), "UNC path reached filesystem probing"
        return stat(path, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(Path, "stat", local_stat)
    with pytest.raises(ArtifactError, match="artifact home must be repository-relative") as caught:
        resolve_artifacts(project, git_sandbox.context())

    expected_status = 2
    assert caught.value.exit_code == expected_status
    assert source.read_bytes() == content
    assert not (root / ".reviews").exists()


def test_preparation_failure_has_execution_status(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """Preparation retains the common helper's rollback and status 1 boundary."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    declaration = resolve_artifacts(project, git_sandbox.context())
    def denied(_path: Path, _content: bytes) -> int:
        msg = "write denied"
        raise PermissionError(msg)
    monkeypatch.setattr("pathlib.Path.write_bytes", denied)
    with pytest.raises(ArtifactError, match="write denied") as caught:
        prepare_artifacts(declaration, git_sandbox.context())
    assert caught.value.exit_code == 1
    assert not declaration.home.exists()


@pytest.mark.parametrize("destination", ["../A/private", "sub/nested/private", "alias/private"])
def test_foreign_and_nested_homes_are_rejected(git_sandbox: GitSandbox, destination: str) -> None:
    """Both direct nesting and a foreign junction fail before any preparation."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    nested = root / "sub/nested"
    nested.mkdir()
    (nested / ".git").write_bytes(b"gitdir: elsewhere")
    if destination.startswith("alias"):
        git_sandbox.junction("B/alias", git_sandbox.home / "A")
    (root / ".review-artifacts.ini").write_text(f"[review-artifacts]\nhome={destination}\n", encoding="utf-8")
    with pytest.raises(ArtifactError):
        resolve_artifacts(project, git_sandbox.context())
    assert not (nested / "private").exists()
    assert not (git_sandbox.home / "A/private").exists()


def test_nested_repository_alias_back_into_project_is_rejected(git_sandbox: GitSandbox) -> None:
    """Physical normalization must not erase a nested repository traversal."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    nested = root / "sub/nested"
    nested.mkdir()
    (nested / ".git").write_bytes(b"gitdir: elsewhere")
    git_sandbox.junction("B/sub/nested/back", root / "sub")
    (root / ".review-artifacts.ini").write_bytes(b"[review-artifacts]\nhome=sub/nested/back/private\n")

    with pytest.raises(ArtifactError, match="nested repository") as caught:
        resolve_artifacts(project, git_sandbox.context())

    expected_status = 2
    assert caught.value.exit_code == expected_status
    assert not (root / "sub/private").exists()


def test_repointed_configured_internal_alias_is_rejected(git_sandbox: GitSandbox) -> None:
    """Preparation retains and rechecks the configured alias, not only its target."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    alias = git_sandbox.junction("B/alias", root / "sub")
    (root / ".review-artifacts.ini").write_bytes(b"[review-artifacts]\nhome=alias/private\n")
    declaration = resolve_artifacts(project, git_sandbox.context())
    other = root / "other"
    other.mkdir()
    alias.rmdir()
    git_sandbox.junction("B/alias", other)

    with pytest.raises(ArtifactError, match="changed after authorization") as caught:
        prepare_artifacts(declaration, git_sandbox.context())

    assert caught.value.exit_code == 1
    assert not (root / "sub/private").exists()
    assert not (other / "private").exists()


def test_declaration_file_symlink_cannot_escape(git_sandbox: GitSandbox) -> None:
    """A real file symlink is checked before the common parser reads its bytes."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    source = git_sandbox.home / "A/config.ini"
    source.write_bytes(b"[review-artifacts]\nhome=private\n")
    try:
        (root / ".review-artifacts.ini").symlink_to(source)
    except OSError as exc:
        missing_symlink_privilege = 1314
        if exc.winerror != missing_symlink_privilege:
            raise
        pytest.skip("Windows file-symlink privilege unavailable; resolved-target boundary covered separately")
    with pytest.raises(ArtifactError, match=r"nested repository|escapes"):
        resolve_artifacts(project, git_sandbox.context())
    assert not (root / "private").exists()


def test_resolved_declaration_escape_is_rejected(git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """Inject the link-resolution result when native file symlinks are unavailable."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    source = root / ".review-artifacts.ini"
    source.write_bytes(b"[review-artifacts]\nhome=private\n")
    foreign = git_sandbox.home / "A/config.ini"
    resolve = Path.resolve
    def linked(path: Path, *, strict: bool = False) -> Path:
        return foreign if path == source else resolve(path, strict=strict)
    monkeypatch.setattr(Path, "resolve", linked)
    with pytest.raises(ArtifactError, match=r"nested repository|escapes"):
        resolve_artifacts(project, git_sandbox.context())
    assert not (root / "private").exists()


def test_preparation_rejects_new_tracking(git_sandbox: GitSandbox) -> None:
    """An index change between resolution and preparation is checked again."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    declaration = resolve_artifacts(project, git_sandbox.context())
    declaration.home.mkdir()
    (declaration.home / "tracked").write_bytes(b"keep")
    git_sandbox.git(["add", ".reviews/tracked"], cwd=root)
    with pytest.raises(ArtifactError, match="tracked") as caught:
        prepare_artifacts(declaration, git_sandbox.context())
    assert caught.value.exit_code == 1
    assert not (declaration.home / ".gitignore").exists()


def test_repointed_home_is_rejected_at_preparation(git_sandbox: GitSandbox) -> None:
    """A previously missing physical home cannot redirect preparation outside B."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    declaration = resolve_artifacts(project, git_sandbox.context())
    git_sandbox.junction("B/.reviews", git_sandbox.home / "A/sub")
    with pytest.raises(ArtifactError):
        prepare_artifacts(declaration, git_sandbox.context())
    assert not (git_sandbox.home / "A/sub/.gitignore").exists()


def test_existing_home_keeps_common_ignore_policy(git_sandbox: GitSandbox) -> None:
    """Existing homes are not silently repaired or rolled back on invalid bytes."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    declaration = resolve_artifacts(project, git_sandbox.context())
    declaration.home.mkdir()
    ignore = declaration.home / ".gitignore"
    ignore.write_bytes(b"*\r\n")
    with pytest.raises(ArtifactError, match="ignore coverage"):
        prepare_artifacts(declaration, git_sandbox.context())
    assert ignore.read_bytes() == b"*\r\n"


# eof
