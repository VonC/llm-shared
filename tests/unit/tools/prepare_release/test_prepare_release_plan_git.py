"""Integration tests for isolated merge-tree and rebase conflict previews.

Fix: cover the remaining plumbing branches for the coverage gate: the
concise `require` failure, the Git version guard, the non-work-tree and
detached-state rejections, remote-HEAD default-branch mapping, merge-base
fork-point and absent-base results, missing reflogs, first-parent history,
inherited alternate object directories, merge-tree invocation failures, a
merge commit inside a rebase-preview range, unresolvable preview objects,
and malformed merge-tree conflict records.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from tools.prepare_release.prepare_release_plan_git import (
    GitRepository,
    _parse_merge_tree,
)
from tools.prepare_release.prepare_release_plan_models import ReleasePlanError

from .prepare_release_plan_test_support import commit_file, git, initialize_repository

if TYPE_CHECKING:
    from collections.abc import Sequence
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


def test_require_raises_a_concise_error_for_a_failing_command(tmp_path: Path) -> None:
    """A failing Git call surfaces its action and stderr, never a traceback."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path)

    with pytest.raises(ReleasePlanError, match="Unable to resolve does-not-exist"):
        repository.resolve("does-not-exist")


def test_version_guard_rejects_unrecognized_and_old_git(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The version guard rejects unparsable output and pre-2.50 versions."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path)

    def odd_version(_args: Sequence[str], *, action: str) -> str:
        del action
        return "odd output"

    monkeypatch.setattr(repository, "require", odd_version)
    with pytest.raises(ReleasePlanError, match="Unrecognized Git version output"):
        repository.assert_supported_version()

    def old_version(_args: Sequence[str], *, action: str) -> str:
        del action
        return "git version 2.30.0"

    monkeypatch.setattr(repository, "require", old_version)
    with pytest.raises(ReleasePlanError, match=r"Git 2\.50\.0\+ is required"):
        repository.assert_supported_version()


def test_verify_repository_rejects_a_non_work_tree(tmp_path: Path) -> None:
    """A root inside `.git` is a repository but not a working tree."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path / ".git")

    with pytest.raises(ReleasePlanError, match="Not a Git working tree"):
        repository.verify_repository()


def test_current_branch_rejects_an_empty_symbolic_ref(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty branch answer is rejected instead of planning on nothing."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path)

    def empty_branch(_args: Sequence[str], *, action: str) -> str:
        del action
        return ""

    monkeypatch.setattr(repository, "require", empty_branch)
    with pytest.raises(ReleasePlanError, match="requires a checked-out branch"):
        repository.current_branch()


def test_remote_default_branch_maps_origin_head_to_a_local_branch(
    tmp_path: Path,
) -> None:
    """A remote HEAD symref yields the local branch, or None when absent."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path)

    git(repo_path, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    assert repository.remote_default_branch() == "main"

    git(repo_path, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/gone")
    assert repository.remote_default_branch() is None


def test_merge_base_supports_fork_point_and_absent_bases(tmp_path: Path) -> None:
    """merge-base answers with and without fork-point, or None on failure."""
    repo_path = tmp_path / "repo"
    base = initialize_repository(repo_path)
    git(repo_path, "switch", "-c", "feature")
    commit_file(repo_path, "feature.txt", "feature\n", "feat: feature change")
    repository = GitRepository(repo_path)

    assert repository.merge_base("main", "feature") == base
    assert repository.merge_base("main", "feature", fork_point=True) == base
    assert repository.merge_base("main", "does-not-exist") is None
    assert repository.reflog("does-not-exist") == ()


def test_first_parent_history_is_oldest_first(tmp_path: Path) -> None:
    """First-parent history lists a branch's commits from oldest to newest."""
    repo_path = tmp_path / "repo"
    base = initialize_repository(repo_path)
    tip = commit_file(repo_path, "main.txt", "main\n", "feat: main work")
    repository = GitRepository(repo_path)

    assert repository.first_parent_history("main") == (base, tip)


def test_isolated_environment_appends_inherited_alternates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An inherited alternates path survives behind the repository objects."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path)
    monkeypatch.setenv("GIT_ALTERNATE_OBJECT_DIRECTORIES", "inherited-objects")

    with repository.isolated_object_environment() as env:
        alternates = env["GIT_ALTERNATE_OBJECT_DIRECTORIES"].split(os.pathsep)

    assert alternates[-1] == "inherited-objects"
    assert alternates[0].endswith("objects")


def test_preview_merge_reports_an_unrunnable_merge_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A merge-tree failure raises the planner error, not exit-code guessing.

    A real merge-tree exits 1 even for an unresolvable ref, so the usage
    failure (any status outside 0 and 1) is modeled with a stubbed run.
    """
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path)

    def broken_merge_tree(
        _args: Sequence[str],
        *,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str, str]:
        del env
        return 129, "", "usage: git merge-tree"

    monkeypatch.setattr(repository, "run", broken_merge_tree)
    with pytest.raises(ReleasePlanError, match="git merge-tree could not run"):
        repository.preview_merge("main", "main")


def test_preview_rebase_rejects_a_merge_commit_in_range(tmp_path: Path) -> None:
    """A merge commit inside the replay range stops the preview explicitly."""
    repo_path = tmp_path / "repo"
    base = initialize_repository(repo_path)
    git(repo_path, "switch", "-c", "feature")
    commit_file(repo_path, "feature.txt", "feature\n", "feat: feature change")
    git(repo_path, "switch", "-c", "side")
    commit_file(repo_path, "side.txt", "side\n", "feat: side change")
    git(repo_path, "switch", "feature")
    git(repo_path, "merge", "--no-ff", "side", "-m", "merge side")
    repository = GitRepository(repo_path)

    with pytest.raises(ReleasePlanError, match="select commits explicitly"):
        repository.preview_rebase(base, "feature", "main")


def test_preview_helpers_reject_unresolvable_objects(tmp_path: Path) -> None:
    """Tree resolution and virtual commits fail with planner errors."""
    repo_path = tmp_path / "repo"
    initialize_repository(repo_path)
    repository = GitRepository(repo_path)

    with repository.isolated_object_environment() as env:
        with pytest.raises(ReleasePlanError, match="Unable to resolve preview tree"):
            repository._tree_oid("does-not-exist", env=env)
        with pytest.raises(
            ReleasePlanError,
            match="Unable to create temporary preview commit",
        ):
            repository._virtual_commit("0" * 40, "does-not-exist", env=env)


def test_parse_merge_tree_rejects_malformed_conflict_records() -> None:
    """Undocumented merge-tree records raise instead of silently truncating."""
    bad_count = "tree\0file\0\0not-a-number\0"
    with pytest.raises(ReleasePlanError, match="Unexpected git merge-tree conflict"):
        _parse_merge_tree(bad_count, clean=False)

    truncated = "tree\0file\0\x001\0path\0CONFLICT (contents)"
    with pytest.raises(ReleasePlanError, match="Incomplete git merge-tree conflict"):
        _parse_merge_tree(truncated, clean=False)


# eof
