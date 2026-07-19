"""Git plumbing for release planning and conflict previews."""

# Planner errors intentionally include actionable Git context at the raise site.
# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from tools.git_command import GitCommandOptions, run_cross_platform_git_command
from tools.prepare_release.prepare_release_plan_models import (
    CommitSummary,
    ConflictRecord,
    MergePreview,
    RebasePreview,
    ReleasePlanError,
)

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

_VERSION_RE = re.compile(r"git version (\d+)\.(\d+)\.(\d+)")
_MINIMUM_GIT_VERSION = (2, 50, 0)


class GitRepository:
    """Read repository topology and simulate merges without changing its state."""

    def __init__(self, root: Path) -> None:
        """Bind the helper to one repository root."""
        self.root = root.resolve()

    def run(
        self,
        args: Sequence[str],
        *,
        env: dict[str, str] | None = None,
    ) -> tuple[int, str, str]:
        """Run Git without raising and return status, stdout, and stderr."""
        result = run_cross_platform_git_command(
            list(args),
            cwd=self.root,
            options=GitCommandOptions(
                check=False,
                capture_output=True,
                encoding="utf-8",
                env=env,
            ),
        )
        return result.returncode, result.stdout, result.stderr

    def require(self, args: Sequence[str], *, action: str) -> str:
        """Run Git and return stdout, raising a concise planner error on failure."""
        status, stdout, stderr = self.run(args)
        if status != 0:
            detail = stderr.strip() or stdout.strip()
            suffix = f": {detail}" if detail else ""
            raise ReleasePlanError(f"Unable to {action}{suffix}")
        return stdout.strip()

    def assert_supported_version(self) -> str:
        """Return the Git version string after enforcing the planner minimum."""
        output = self.require(["--version"], action="read the Git version")
        match = _VERSION_RE.search(output)
        if match is None:
            raise ReleasePlanError(f"Unrecognized Git version output: {output}")
        version = tuple(int(part) for part in match.groups())
        if version < _MINIMUM_GIT_VERSION:
            minimum = ".".join(str(part) for part in _MINIMUM_GIT_VERSION)
            raise ReleasePlanError(
                f"Git {minimum}+ is required for isolated merge-tree previews; found {output}.",
            )
        return output.removeprefix("git version ")

    def verify_repository(self) -> None:
        """Raise unless root belongs to a Git working tree."""
        value = self.require(
            ["rev-parse", "--is-inside-work-tree"],
            action="verify the repository",
        )
        if value != "true":
            raise ReleasePlanError(f"Not a Git working tree: {self.root}")

    def resolve(self, ref: str) -> str:
        """Resolve one commit-ish to its full commit OID."""
        return self.require(
            ["rev-parse", "--verify", f"{ref}^{{commit}}"],
            action=f"resolve {ref}",
        )

    def current_branch(self) -> str:
        """Return the checked-out branch and reject detached HEAD."""
        branch = self.require(
            ["symbolic-ref", "--quiet", "--short", "HEAD"],
            action="identify the current branch",
        )
        if not branch:
            raise ReleasePlanError("prepare-release planning requires a checked-out branch.")
        return branch

    def local_branches(self) -> tuple[str, ...]:
        """Return all local branch names in stable order."""
        output = self.require(
            ["for-each-ref", "--sort=refname", "--format=%(refname:short)", "refs/heads"],
            action="list local branches",
        )
        return tuple(line for line in output.splitlines() if line)

    def branch_exists(self, branch: str) -> bool:
        """Return whether a local branch exists."""
        status, _, _ = self.run(["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"])
        return status == 0

    def config_value(self, key: str) -> str | None:
        """Return one repository config value, or None when unset."""
        status, stdout, _ = self.run(["config", "--get", key])
        value = stdout.strip()
        return value if status == 0 and value else None

    def remote_default_branch(self, remote: str = "origin") -> str | None:
        """Return a local branch name derived from a remote HEAD symbolic ref."""
        status, stdout, _ = self.run(
            ["symbolic-ref", "--quiet", "--short", f"refs/remotes/{remote}/HEAD"],
        )
        value = stdout.strip()
        prefix = f"{remote}/"
        if status != 0 or not value.startswith(prefix):
            return None
        branch = value.removeprefix(prefix)
        return branch if self.branch_exists(branch) else None

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """Return whether ancestor is reachable from descendant."""
        status, _, _ = self.run(["merge-base", "--is-ancestor", ancestor, descendant])
        return status == 0

    def merge_base(self, left: str, right: str, *, fork_point: bool = False) -> str | None:
        """Return a merge base, optionally using reflog-aware fork-point mode."""
        args = ["merge-base"]
        if fork_point:
            args.append("--fork-point")
        args.extend([left, right])
        status, stdout, _ = self.run(args)
        value = stdout.strip()
        return value if status == 0 and value else None

    def commit_count(self, revision_range: str) -> int:
        """Count commits in one revision range."""
        output = self.require(
            ["rev-list", "--count", revision_range],
            action=f"count commits in {revision_range}",
        )
        return int(output)

    def commits(self, revision_range: str) -> tuple[CommitSummary, ...]:
        """Return commits in oldest-first order for one range."""
        output = self.require(
            ["log", "--reverse", "--format=%H%x00%s", revision_range],
            action=f"list commits in {revision_range}",
        )
        commits: list[CommitSummary] = []
        for line in output.splitlines():
            oid, separator, subject = line.partition("\0")
            if separator:
                commits.append(CommitSummary(oid=oid, subject=subject))
        return tuple(commits)

    def commit_parents(self, commit: str) -> tuple[str, ...]:
        """Return the parent OIDs for one commit."""
        output = self.require(
            ["rev-list", "--parents", "-n", "1", commit],
            action=f"read parents of {commit}",
        )
        return tuple(output.split()[1:])

    def contains_merge(self, revision_range: str) -> bool:
        """Return whether a range contains at least one merge commit."""
        status, stdout, _ = self.run(["rev-list", "--min-parents=2", "-n", "1", revision_range])
        return status == 0 and bool(stdout.strip())

    def tags_containing(self, ref: str) -> tuple[str, ...]:
        """Return version-sorted tags containing a ref."""
        output = self.require(
            ["tag", "--contains", ref, "--sort=version:refname"],
            action=f"list tags containing {ref}",
        )
        return tuple(line for line in output.splitlines() if line)

    def latest_tag(self, ref: str) -> str | None:
        """Return the latest reachable tag, or None for an untagged history."""
        status, stdout, _ = self.run(["describe", "--tags", "--abbrev=0", ref])
        value = stdout.strip()
        return value if status == 0 and value else None

    def reflog(self, branch: str) -> tuple[tuple[str, str], ...]:
        """Return branch reflog entries from oldest to newest."""
        status, stdout, _ = self.run(
            ["reflog", "show", "--format=%H%x00%gs", branch],
        )
        if status != 0:
            return ()
        entries: list[tuple[str, str]] = []
        for line in stdout.splitlines():
            oid, separator, subject = line.partition("\0")
            if separator:
                entries.append((oid, subject))
        entries.reverse()
        return tuple(entries)

    def first_parent_history(self, branch: str) -> tuple[str, ...]:
        """Return a branch's first-parent commits from oldest to newest."""
        output = self.require(
            ["rev-list", "--first-parent", "--reverse", branch],
            action=f"inspect first-parent history of {branch}",
        )
        return tuple(line for line in output.splitlines() if line)

    @contextmanager
    def isolated_object_environment(self) -> Generator[dict[str, str]]:
        """Yield an environment that writes preview objects outside the repository."""
        object_dir = Path(
            self.require(
                ["rev-parse", "--path-format=absolute", "--git-path", "objects"],
                action="locate the Git object directory",
            ),
        )
        with tempfile.TemporaryDirectory(prefix="prepare-release-preview-") as temp_dir:
            preview_objects = Path(temp_dir) / "objects"
            preview_objects.mkdir()
            env = os.environ.copy()
            inherited = env.get("GIT_ALTERNATE_OBJECT_DIRECTORIES")
            alternates = [str(object_dir)]
            if inherited:
                alternates.append(inherited)
            env["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = os.pathsep.join(alternates)
            env["GIT_OBJECT_DIRECTORY"] = str(preview_objects)
            env.update(
                {
                    "GIT_AUTHOR_NAME": "prepare-release preview",
                    "GIT_AUTHOR_EMAIL": "preview@example.invalid",
                    "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
                    "GIT_COMMITTER_NAME": "prepare-release preview",
                    "GIT_COMMITTER_EMAIL": "preview@example.invalid",
                    "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
                },
            )
            yield env

    def preview_merge(
        self,
        destination: str,
        source: str,
        *,
        merge_base: str | None = None,
        env: dict[str, str] | None = None,
    ) -> MergePreview:
        """Simulate one ort merge and return its machine-readable conflicts."""
        args = ["merge-tree", "--write-tree", "--name-only", "--messages", "-z"]
        if merge_base is not None:
            args.append(f"--merge-base={merge_base}")
        args.extend([destination, source])
        status, stdout, stderr = self.run(args, env=env)
        if status not in {0, 1}:
            detail = stderr.strip() or stdout.strip()
            raise ReleasePlanError(f"git merge-tree could not run: {detail}")
        return _parse_merge_tree(stdout, clean=status == 0)

    def preview_rebase(self, base: str, branch: str, onto: str) -> RebasePreview:
        """Simulate each commit in `base..branch` onto `onto`, stopping at conflict."""
        commits = self.commits(f"{base}..{branch}")
        current_tip = self.resolve(onto)
        with self.isolated_object_environment() as env:
            for index, commit in enumerate(commits, start=1):
                parents = self.commit_parents(commit.oid)
                if len(parents) != 1:
                    raise ReleasePlanError(
                        f"Feature range contains merge commit {commit.oid}; select commits explicitly.",
                    )
                merge = self.preview_merge(
                    current_tip,
                    commit.oid,
                    merge_base=parents[0],
                    env=env,
                )
                if not merge.clean:
                    return RebasePreview(
                        clean=False,
                        checked_commits=index,
                        conflict_commit=commit.oid,
                        conflict_subject=commit.subject,
                        merge=merge,
                    )
                current_tree = self._tree_oid(current_tip, env=env)
                if merge.tree_oid != current_tree:
                    current_tip = self._virtual_commit(merge.tree_oid, current_tip, env=env)
        return RebasePreview(
            clean=True,
            checked_commits=len(commits),
            conflict_commit=None,
            conflict_subject=None,
            merge=None,
        )

    def _tree_oid(self, commit: str, *, env: dict[str, str]) -> str:
        status, stdout, stderr = self.run(["rev-parse", f"{commit}^{{tree}}"], env=env)
        if status != 0:
            raise ReleasePlanError(f"Unable to resolve preview tree: {stderr.strip()}")
        return stdout.strip()

    def _virtual_commit(self, tree: str, parent: str, *, env: dict[str, str]) -> str:
        status, stdout, stderr = self.run(
            ["commit-tree", tree, "-p", parent, "-m", "prepare-release conflict preview"],
            env=env,
        )
        if status != 0:
            raise ReleasePlanError(f"Unable to create temporary preview commit: {stderr.strip()}")
        return stdout.strip()


def _parse_merge_tree(output: str, *, clean: bool) -> MergePreview:
    """Parse the documented NUL-delimited merge-tree output format."""
    fields = output.split("\0")
    tree_oid = fields[0] if fields else ""
    if clean:
        return MergePreview(clean=True, tree_oid=tree_oid, conflicted_files=(), conflicts=())

    index = 1
    files: list[str] = []
    while index < len(fields) and fields[index]:
        files.append(fields[index])
        index += 1
    index += 1

    conflicts: list[ConflictRecord] = []
    while index < len(fields) and fields[index]:
        try:
            path_count = int(fields[index])
        except ValueError as exc:
            raise ReleasePlanError("Unexpected git merge-tree conflict record.") from exc
        index += 1
        paths = tuple(fields[index : index + path_count])
        index += path_count
        if index + 1 >= len(fields):
            raise ReleasePlanError("Incomplete git merge-tree conflict record.")
        conflict_type = fields[index]
        message = fields[index + 1]
        index += 2
        conflicts.append(
            ConflictRecord(
                conflict_type=conflict_type,
                paths=paths,
                message=message,
            ),
        )
    return MergePreview(
        clean=False,
        tree_oid=tree_oid,
        conflicted_files=tuple(files),
        conflicts=tuple(conflicts),
    )


# eof
