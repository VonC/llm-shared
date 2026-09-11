"""Integration tests for isolated merge-tree and rebase conflict previews.

Fix: cover the remaining plumbing branches for the coverage gate: the
concise `require` failure, the Git version guard, the non-work-tree and
detached-state rejections, remote-HEAD default-branch mapping, merge-base
fork-point and absent-base results, missing reflogs, first-parent history,
inherited alternate object directories, merge-tree invocation failures, a
merge commit inside a rebase-preview range, unresolvable preview objects,
and malformed merge-tree conflict records.

Fix: drive merge-tree parsing and sequential rebase behavior through recorded
Git plumbing results and method seams. This keeps the exact conflict, replay,
merge-rejection, and failure contracts without repeated repository setup.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import os
import subprocess
from contextlib import AbstractContextManager, nullcontext
from typing import TYPE_CHECKING

import pytest

from tools.prepare_release import prepare_release_plan_git as git_adapter
from tools.prepare_release.prepare_release_plan_git import (
    GitRepository,
    _parse_merge_tree,
)
from tools.prepare_release.prepare_release_plan_models import (
    CommitSummary,
    MergePreview,
    ReleasePlanError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


_EXPECTED_REPLAYED_COMMITS = 2
_EXPECTED_COMMIT_COUNT = 2


def test_repository_parses_recorded_git_command_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise the complete non-streaming Git adapter without subprocesses."""
    oid = "a" * 40
    parent = "b" * 40

    def recorded_git(
        command: Sequence[str],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        key = tuple(command)
        outputs: dict[tuple[str, ...], tuple[int, str, str]] = {
            ("--version",): (0, "git version 2.50.1\n", ""),
            ("symbolic-ref", "--quiet", "--short", "HEAD"): (0, "feature\n", ""),
            (
                "for-each-ref",
                "--sort=refname",
                "--format=%(refname:short)",
                "refs/heads",
            ): (0, "feature\nmain\n", ""),
            ("config", "--get", "release.integrationBranch"): (0, "develop\n", ""),
            (
                "symbolic-ref",
                "--quiet",
                "--short",
                "refs/remotes/origin/HEAD",
            ): (1, "", "missing"),
            ("merge-base", "--is-ancestor", "main", "feature"): (0, "", ""),
            ("rev-list", "--count", "main..feature"): (0, "2\n", ""),
            ("log", "--reverse", "--format=%H%x00%s", "main..feature"): (
                0,
                f"{oid}\0feat: one\nmalformed\n",
                "",
            ),
            ("rev-list", "--parents", "-n", "1", oid): (
                0,
                f"{oid} {parent}\n",
                "",
            ),
            ("rev-list", "--min-parents=2", "-n", "1", "main..feature"): (
                0,
                f"{oid}\n",
                "",
            ),
            ("tag", "--contains", "feature", "--sort=version:refname"): (
                0,
                "v1.0.0\nv1.1.0\n",
                "",
            ),
            ("describe", "--tags", "--abbrev=0", "main"): (0, "v1.1.0\n", ""),
            ("reflog", "show", "--format=%H%x00%gs", "feature"): (
                0,
                f"{oid}\0newest\n{parent}\0oldest\n",
                "",
            ),
            ("rev-parse", f"{oid}^{{tree}}"): (0, "tree-oid\n", ""),
            (
                "commit-tree",
                "tree-oid",
                "-p",
                oid,
                "-m",
                "prepare-release conflict preview",
            ): (0, "virtual-oid\n", ""),
            (
                "merge-tree",
                "--write-tree",
                "--name-only",
                "--messages",
                "-z",
                "--merge-base=base",
                "main",
                "feature",
            ): (0, "tree-oid\0", ""),
        }
        try:
            status, stdout, stderr = outputs[key]
        except KeyError as error:
            raise AssertionError(key) from error
        return subprocess.CompletedProcess(command, status, stdout, stderr)

    monkeypatch.setattr(git_adapter, "run_cross_platform_git_command", recorded_git)
    repository = GitRepository(tmp_path)

    preview = repository.preview_merge("main", "feature", merge_base="base")
    actual = (
        repository.assert_supported_version(),
        repository.current_branch(),
        repository.local_branches(),
        repository.config_value("release.integrationBranch"),
        repository.remote_default_branch(),
        repository.is_ancestor("main", "feature"),
        repository.commit_count("main..feature"),
        repository.commits("main..feature"),
        repository.commit_parents(oid),
        repository.contains_merge("main..feature"),
        repository.tags_containing("feature"),
        repository.latest_tag("main"),
        repository.reflog("feature"),
        repository._tree_oid(oid, env={}),
        repository._virtual_commit("tree-oid", oid, env={}),
        preview.clean,
    )
    expected = (
        "2.50.1",
        "feature",
        ("feature", "main"),
        "develop",
        None,
        True,
        _EXPECTED_COMMIT_COUNT,
        (CommitSummary(oid, "feat: one"),),
        (parent,),
        True,
        ("v1.0.0", "v1.1.0"),
        "v1.1.0",
        ((parent, "oldest"), (oid, "newest")),
        "tree-oid",
        "virtual-oid",
        True,
    )
    assert actual == expected


def test_preview_merge_reports_conflicted_file_without_changing_objects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """merge-tree reports a content conflict and writes only temporary objects."""
    repository = GitRepository(tmp_path)
    expected_env = {"GIT_OBJECT_DIRECTORY": "temporary"}
    output = (
        "tree\0shared.txt\0\0"
        "1\0shared.txt\0CONFLICT (contents)\0content conflict\0"
    )
    calls: list[tuple[tuple[str, ...], dict[str, str] | None]] = []

    def merge_tree_run(
        args: Sequence[str],
        *,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str, str]:
        calls.append((tuple(args), env))
        return 1, output, ""

    monkeypatch.setattr(repository, "run", merge_tree_run)
    preview = repository.preview_merge("main", "feature", env=expected_env)

    assert preview.clean is False
    assert preview.conflicted_files == ("shared.txt",)
    assert any(record.conflict_type.startswith("CONFLICT") for record in preview.conflicts)
    assert calls == (
        [
            (
                (
                    "merge-tree",
                    "--write-tree",
                    "--name-only",
                    "--messages",
                    "-z",
                    "main",
                    "feature",
                ),
                expected_env,
            ),
        ]
    )


def test_preview_rebase_stops_at_first_conflicting_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A rebase preview identifies the exact commit that would stop replay."""
    repository = GitRepository(tmp_path)
    feature_tip = "f" * 40
    conflict = MergePreview(
        clean=False,
        tree_oid="tree",
        conflicted_files=("shared.txt",),
        conflicts=(),
    )
    def one_commit(_revision_range: str) -> tuple[CommitSummary, ...]:
        return (CommitSummary(feature_tip, "feat: feature change"),)

    def main_tip(_ref: str) -> str:
        return "m" * 40

    def one_parent(_oid: str) -> tuple[str, ...]:
        return ("b" * 40,)

    def isolated_environment() -> AbstractContextManager[dict[str, str]]:
        return nullcontext({})

    def conflicting_preview(
        _destination: str,
        _source: str,
        **_kwargs: object,
    ) -> MergePreview:
        return conflict

    monkeypatch.setattr(
        repository,
        "commits",
        one_commit,
    )
    monkeypatch.setattr(repository, "resolve", main_tip)
    monkeypatch.setattr(repository, "commit_parents", one_parent)
    monkeypatch.setattr(repository, "isolated_object_environment", isolated_environment)
    monkeypatch.setattr(repository, "preview_merge", conflicting_preview)

    preview = repository.preview_rebase("develop", feature_tip, "main")

    assert preview.clean is False
    assert preview.checked_commits == 1
    assert preview.conflict_commit == feature_tip
    assert preview.conflict_subject == "feat: feature change"
    assert preview.merge is not None
    assert preview.merge.conflicted_files == ("shared.txt",)


def test_preview_rebase_advances_virtual_tip_for_clean_commits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sequential clean commits are replayed through an isolated synthetic tip."""
    repository = GitRepository(tmp_path)
    commits = (
        CommitSummary("1" * 40, "feat: first"),
        CommitSummary("2" * 40, "feat: second"),
    )
    tips: list[tuple[str, str]] = []
    def selected_commits(_revision_range: str) -> tuple[CommitSummary, ...]:
        return commits

    def main_tip(_ref: str) -> str:
        return "m" * 40

    def one_parent(_oid: str) -> tuple[str, ...]:
        return ("b" * 40,)

    def isolated_environment() -> AbstractContextManager[dict[str, str]]:
        return nullcontext({})

    def clean_preview(
        _tip: str,
        oid: str,
        **_kwargs: object,
    ) -> MergePreview:
        return MergePreview(
            clean=True,
            tree_oid=f"tree-{oid[0]}",
            conflicted_files=(),
            conflicts=(),
        )

    def current_tree(tip: str, **_kwargs: object) -> str:
        return f"old-{tip[0]}"

    monkeypatch.setattr(repository, "commits", selected_commits)
    monkeypatch.setattr(repository, "resolve", main_tip)
    monkeypatch.setattr(repository, "commit_parents", one_parent)
    monkeypatch.setattr(repository, "isolated_object_environment", isolated_environment)
    monkeypatch.setattr(
        repository,
        "preview_merge",
        clean_preview,
    )
    monkeypatch.setattr(repository, "_tree_oid", current_tree)

    def virtual_commit(tree: str, parent: str, *, env: dict[str, str]) -> str:
        del env
        tips.append((tree, parent))
        return f"virtual-{len(tips)}"

    monkeypatch.setattr(repository, "_virtual_commit", virtual_commit)
    preview = repository.preview_rebase("develop", "feature", "main")

    assert preview.clean is True
    assert preview.checked_commits == _EXPECTED_REPLAYED_COMMITS
    assert preview.conflict_commit is None
    assert preview.merge is None
    assert tips == [("tree-1", "m" * 40), ("tree-2", "virtual-1")]


def test_require_raises_a_concise_error_for_a_failing_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing Git call surfaces its action and stderr, never a traceback."""
    repository = GitRepository(tmp_path)

    def failed_run(
        _args: Sequence[str],
        *,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str, str]:
        del env
        return 128, "", "unknown revision"

    monkeypatch.setattr(
        repository,
        "run",
        failed_run,
    )

    with pytest.raises(ReleasePlanError, match="Unable to resolve does-not-exist"):
        repository.resolve("does-not-exist")


def test_version_guard_rejects_unrecognized_and_old_git(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The version guard rejects unparsable output and pre-2.50 versions."""
    repository = GitRepository(tmp_path)

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


def test_verify_repository_rejects_a_non_work_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A root inside `.git` is a repository but not a working tree."""
    repository = GitRepository(tmp_path / ".git")

    def not_work_tree(_args: Sequence[str], **_kwargs: object) -> str:
        return "false"

    monkeypatch.setattr(repository, "require", not_work_tree)

    with pytest.raises(ReleasePlanError, match="Not a Git working tree"):
        repository.verify_repository()


def test_current_branch_rejects_an_empty_symbolic_ref(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty branch answer is rejected instead of planning on nothing."""
    repository = GitRepository(tmp_path)

    def empty_branch(_args: Sequence[str], *, action: str) -> str:
        del action
        return ""

    monkeypatch.setattr(repository, "require", empty_branch)
    with pytest.raises(ReleasePlanError, match="requires a checked-out branch"):
        repository.current_branch()


def test_remote_default_branch_maps_origin_head_to_a_local_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A remote HEAD symref yields the local branch, or None when absent."""
    repository = GitRepository(tmp_path)
    remote_branch = "main"

    def remote_run(
        args: Sequence[str],
        *,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str, str]:
        del env
        if args[0] == "symbolic-ref":
            return 0, f"origin/{remote_branch}\n", ""
        exists = args[-1] == "refs/heads/main"
        return (0 if exists else 1), "", ""

    monkeypatch.setattr(repository, "run", remote_run)
    assert repository.remote_default_branch() == "main"

    remote_branch = "gone"
    assert repository.remote_default_branch() is None


def test_merge_base_supports_fork_point_and_absent_bases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """merge-base answers with and without fork-point, or None on failure."""
    base = "a" * 40
    repository = GitRepository(tmp_path)

    def merge_base_run(
        args: Sequence[str],
        *,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str, str]:
        del env
        if args[0] == "merge-base" and args[-1] == "feature":
            return 0, f"{base}\n", ""
        return 1, "", "unknown revision"

    monkeypatch.setattr(repository, "run", merge_base_run)

    assert repository.merge_base("main", "feature") == base
    assert repository.merge_base("main", "feature", fork_point=True) == base
    assert repository.merge_base("main", "does-not-exist") is None
    assert repository.reflog("does-not-exist") == ()


def test_first_parent_history_is_oldest_first(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """First-parent history lists a branch's commits from oldest to newest."""
    base = "a" * 40
    tip = "b" * 40
    repository = GitRepository(tmp_path)

    def history_result(_args: Sequence[str], **_kwargs: object) -> str:
        return f"{base}\n{tip}\n"

    monkeypatch.setattr(
        repository,
        "require",
        history_result,
    )
    history = repository.first_parent_history("main")

    assert history == (base, tip)


def test_isolated_environment_appends_inherited_alternates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An inherited alternates path survives behind the repository objects."""
    repository = GitRepository(tmp_path)
    object_dir = tmp_path / "objects"

    def object_directory(_args: Sequence[str], **_kwargs: object) -> str:
        return str(object_dir)

    monkeypatch.setattr(
        repository,
        "require",
        object_directory,
    )
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
    repository = GitRepository(tmp_path)

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


def test_preview_rebase_rejects_a_merge_commit_in_range(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A merge commit inside the replay range stops the preview explicitly."""
    repository = GitRepository(tmp_path)
    commit = CommitSummary("c" * 40, "merge side")
    def selected_commit(_revision_range: str) -> tuple[CommitSummary, ...]:
        return (commit,)

    def main_tip(_ref: str) -> str:
        return "m" * 40

    def merge_parents(_oid: str) -> tuple[str, ...]:
        return "a", "b"

    def isolated_environment() -> AbstractContextManager[dict[str, str]]:
        return nullcontext({})

    monkeypatch.setattr(repository, "commits", selected_commit)
    monkeypatch.setattr(repository, "resolve", main_tip)
    monkeypatch.setattr(repository, "commit_parents", merge_parents)
    monkeypatch.setattr(repository, "isolated_object_environment", isolated_environment)

    with pytest.raises(ReleasePlanError, match="select commits explicitly"):
        repository.preview_rebase("base", "feature", "main")


def test_preview_helpers_reject_unresolvable_objects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tree resolution and virtual commits fail with planner errors."""
    repository = GitRepository(tmp_path)

    def unresolvable(
        _args: Sequence[str],
        **_kwargs: object,
    ) -> tuple[int, str, str]:
        return 128, "", "unknown object"

    monkeypatch.setattr(
        repository,
        "run",
        unresolvable,
    )

    with pytest.raises(ReleasePlanError, match="Unable to resolve preview tree"):
        repository._tree_oid("does-not-exist", env={})
    with pytest.raises(ReleasePlanError, match="Unable to create temporary preview commit"):
        repository._virtual_commit("0" * 40, "does-not-exist", env={})


def test_parse_merge_tree_rejects_malformed_conflict_records() -> None:
    """Undocumented merge-tree records raise instead of silently truncating."""
    bad_count = "tree\0file\0\0not-a-number\0"
    with pytest.raises(ReleasePlanError, match="Unexpected git merge-tree conflict"):
        _parse_merge_tree(bad_count, clean=False)

    truncated = "tree\0file\0\x001\0path\0CONFLICT (contents)"
    with pytest.raises(ReleasePlanError, match="Incomplete git merge-tree conflict"):
        _parse_merge_tree(truncated, clean=False)


# eof
