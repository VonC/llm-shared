"""Integration tests for isolated merge-tree and rebase conflict previews."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_git import GitRepository

from .prepare_release_plan_test_support import commit_file, git, initialize_repository

if TYPE_CHECKING:
    from pathlib import Path

_EXPECTED_REPLAYED_COMMITS = 2


def test_preview_merge_reports_conflicted_file_without_changing_objects(tmp_path: Path) -> None:
    """merge-tree reports a content conflict and writes only temporary objects."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    git(repo_path, "switch", "-c", "feature")
    commit_file(repo_path, "shared.txt", "feature\n", "feat: feature change")
    git(repo_path, "switch", "main")
    commit_file(repo_path, "shared.txt", "main\n", "fix: main change")
    repository = GitRepository(repo_path)
    objects_before = git(repo_path, "count-objects", "-v")

    with repository.isolated_object_environment() as env:
        preview = repository.preview_merge("main", "feature", env=env)

    assert preview.clean is False
    assert preview.conflicted_files == ("shared.txt",)
    assert any(record.conflict_type.startswith("CONFLICT") for record in preview.conflicts)
    assert git(repo_path, "count-objects", "-v") == objects_before


def test_preview_rebase_stops_at_first_conflicting_commit(tmp_path: Path) -> None:
    """A rebase preview identifies the exact commit that would stop replay."""
    repo_path = tmp_path / "repo"
    base = initialize_repository(repo_path)
    git(repo_path, "switch", "-c", "develop")
    develop_tip = commit_file(repo_path, "parent.txt", "develop\n", "feat: parent work")
    git(repo_path, "switch", "-c", "feature")
    feature_tip = commit_file(repo_path, "shared.txt", "feature\n", "feat: feature change")
    git(repo_path, "switch", "main")
    commit_file(repo_path, "shared.txt", "main\n", "fix: main change")
    repository = GitRepository(repo_path)

    preview = repository.preview_rebase(develop_tip, feature_tip, "main")

    assert repository.resolve(base) == base
    assert preview.clean is False
    assert preview.checked_commits == 1
    assert preview.conflict_commit == feature_tip
    assert preview.conflict_subject == "feat: feature change"
    assert preview.merge is not None
    assert preview.merge.conflicted_files == ("shared.txt",)


def test_preview_rebase_advances_virtual_tip_for_clean_commits(tmp_path: Path) -> None:
    """Sequential clean commits are replayed through an isolated synthetic tip."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    git(repo_path, "switch", "-c", "develop")
    develop_tip = commit_file(repo_path, "parent.txt", "develop\n", "feat: parent work")
    git(repo_path, "switch", "-c", "feature")
    commit_file(repo_path, "one.txt", "one\n", "feat: first")
    feature_tip = commit_file(repo_path, "two.txt", "two\n", "feat: second")
    git(repo_path, "switch", "main")
    commit_file(repo_path, "main.txt", "main\n", "fix: main work")
    repository = GitRepository(repo_path)

    preview = repository.preview_rebase(develop_tip, feature_tip, "main")

    assert preview.clean is True
    assert preview.checked_commits == _EXPECTED_REPLAYED_COMMITS
    assert preview.conflict_commit is None
    assert preview.merge is None


# eof
