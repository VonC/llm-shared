"""Validate physical worktrees and managed destinations without tree scans.

Git metadata is distinct from managed project destinations, so linked
worktrees may keep their Git/common directories outside the physical root.
Destination checks visit only relevant ancestors and return a physical path;
the write boundary must repeat authorization immediately before mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.git_environment import GitPolicyError

if TYPE_CHECKING:
    from tools.release_workflow.git import GitExecutionContext

_METADATA_PATH_COUNT = 3


class ProjectPathError(ValueError):
    """A supplied root or managed path cannot be physically authorized."""


@dataclass(frozen=True)
class ProjectIdentity:
    """Physical worktree root and separate per-worktree/common Git metadata."""

    root: Path
    git_dir: Path
    common_dir: Path
    supplied_root: str


def _directory(supplied: str | Path | None, git: GitExecutionContext) -> Path:
    """Resolve relative input against the captured engine cwd, never ambient cwd."""
    if supplied is None or str(supplied) == "":
        msg = "An explicit project root is required"
        raise ProjectPathError(msg)
    path = Path(supplied)
    if not path.is_absolute():
        path = git.original_cwd / path
    if not path.is_dir():
        msg = f"Project root is not an existing directory: {supplied}"
        raise ProjectPathError(msg)
    return path.resolve(strict=True)


def _metadata(directory: Path, git: GitExecutionContext) -> tuple[Path, Path, Path]:
    """Check configuration before trusting any worktree discovery result."""
    git.inspect_config(cwd=directory)
    result = git.run(["rev-parse", "--path-format=absolute", "--show-toplevel", "--absolute-git-dir", "--git-common-dir"], cwd=directory)
    lines = result.stdout.splitlines()
    if len(lines) != _METADATA_PATH_COUNT or any(not Path(line).is_absolute() for line in lines):
        msg = "Git did not report three absolute project metadata paths"
        raise ProjectPathError(msg)
    root, git_dir, common = (Path(line).resolve(strict=True) for line in lines)
    return root, git_dir, common


def _validated_identity(supplied: str, directory: Path, metadata: tuple[Path, Path, Path]) -> ProjectIdentity:
    """Apply the same physical-root check to explicit and discovered roots."""
    root, git_dir, common = metadata
    if not directory.samefile(root):
        msg = f"Explicit project root is a subfolder, not the Git top-level: {supplied} (top-level {root})"
        raise ProjectPathError(msg)
    return ProjectIdentity(root, git_dir, common, supplied)


def validate_project(supplied: str | Path | None, git: GitExecutionContext) -> ProjectIdentity:
    """Require the explicit directory to be Git's physical top-level.

    Equivalent Windows spellings and links are compared by filesystem identity.
    Original user input is retained in both the identity and failure diagnostics.
    """
    try:
        directory = _directory(supplied, git)
        return _validated_identity(str(supplied), directory, _metadata(directory, git))
    except (OSError, RuntimeError, GitPolicyError, ProjectPathError) as exc:
        msg = f"Cannot validate project root {supplied}: {exc}"
        raise ProjectPathError(msg) from exc


def discover_project(start: str | Path, git: GitExecutionContext) -> ProjectIdentity:
    """Discover an alias's worktree then use the same physical-root validator.

    Keep the already inspected metadata for this operation, avoiding duplicate
    configuration and discovery subprocesses for the same worktree.
    """
    try:
        directory = _directory(start, git)
        metadata = _metadata(directory, git)
        root = _directory(metadata[0], git)
        return _validated_identity(str(root), root, metadata)
    except (OSError, RuntimeError, GitPolicyError, ProjectPathError) as exc:
        msg = f"Cannot discover project from {start}: {exc}"
        raise ProjectPathError(msg) from exc


def _foreign_boundary(directory: Path) -> bool:
    """Recognize nested worktrees/gitfiles and bare metadata without Git scans."""
    marker = directory / ".git"
    return marker.exists() or marker.is_symlink() or (
        (directory / "HEAD").is_file() and (directory / "objects").is_dir() and (directory / "refs").is_dir()
    )


def _check_repository_boundary(current: Path, root: Path) -> None:
    """Exclude our own Git metadata and foreign repositories by local probes."""
    metadata = root / ".git"
    if metadata.exists() and current.samefile(metadata):
        msg = f"Managed path crosses project Git metadata at {current}"
        raise ProjectPathError(msg)
    if current.is_dir() and _foreign_boundary(current):
        msg = f"Managed path crosses a nested repository at {current}"
        raise ProjectPathError(msg)


def _check_ancestors(target: Path, root: Path) -> None:
    """Visit existing ancestors once, stopping at a filesystem-identical root."""
    current = target
    while True:
        if current.exists():
            if current.samefile(root):
                return
            _check_repository_boundary(current, root)
            if current != target and not current.is_dir():
                msg = f"Managed path has a non-directory ancestor at {current}"
                raise ProjectPathError(msg)
        parent = current.parent
        if parent == current:
            msg = f"Managed path escapes physical project root {root}"
            raise ProjectPathError(msg)
        current = parent


def authorize_path(identity: ProjectIdentity, supplied: str | Path) -> Path:
    """Authorize existing/future destinations physically inside this worktree.

    Check the spelling's existing ancestors as well as the resolved destination
    so internal links cannot hide nested repositories. This makes no directory
    and never scans siblings or runs Git once per ancestor.
    """
    original = str(supplied)
    candidate = Path(supplied)
    if not candidate.is_absolute():
        candidate = identity.root / candidate
    try:
        _check_ancestors(candidate, identity.root)
        physical = candidate.resolve(strict=False)
        _check_ancestors(physical, identity.root)
    except (OSError, RuntimeError, ProjectPathError) as exc:
        msg = f"Cannot authorize managed path {original}: {exc}"
        raise ProjectPathError(msg) from exc
    return physical


# eof
