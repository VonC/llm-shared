"""Separate read-only artifact declarations from explicit mutation preparation.

The existing review helper remains the only parser, ignore-policy validator and
preparation rollback owner. No release adapter migrates legacy scratch files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.release_workflow.git_environment import GitPolicyError
from tools.release_workflow.managed_files import (
    ManagedTarget,
    ManagedWriteError,
    authorize_write,
)
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.git import GitExecutionContext
    from tools.release_workflow.paths import ProjectIdentity


class ArtifactError(ValueError):
    """Artifact diagnostics carry preflight (2) or execution (1) status."""

    def __init__(self, message: str, *, exit_code: int) -> None:
        """Keep the status for the invocation renderer without printing here."""
        self.exit_code = exit_code
        super().__init__(message)


@dataclass(frozen=True)
class ArtifactDeclaration:
    """Read-only paths retaining configured spelling for preparation rechecks.

    No eager home preparation or scratch migration method is exposed.
    """

    project: ProjectIdentity
    source: ManagedTarget
    destination: ManagedTarget
    declared: bool

    @property
    def home(self) -> Path:
        """Return the validated physical home, which need not exist yet."""
        return self.destination.path


@dataclass(frozen=True)
class PreparedArtifacts:
    """Explicitly prepared home capability supplied only to mutating services."""

    project: ProjectIdentity
    destination: ManagedTarget

    @property
    def home(self) -> Path:
        """Return the physical location retained by this capability."""
        return self.destination.path


def _tracked(git: GitExecutionContext, root: Path, relative: str) -> bool:
    """Use the operation's controlled executable, environment and literal paths."""
    return bool(git.run(["ls-files", "-z", "--", relative], cwd=root).stdout)


def _require_untracked(git: GitExecutionContext, root: Path, relative: str) -> None:
    """Reject newly tracked content again immediately before preparation."""
    if _tracked(git, root, relative):
        msg = "Artifact home names a tracked directory"
        raise ManagedWriteError(msg)


def resolve_artifacts(project: ProjectIdentity, git: GitExecutionContext) -> ArtifactDeclaration:
    """Load once, retain lexical authorization and leave all artifacts untouched."""
    destinations: list[ManagedTarget] = []

    def validate_home(path: Path) -> None:
        destinations.append(authorize_write(project, path))

    try:
        source = authorize_write(project, ".review-artifacts.ini")
        configuration = ReviewArtifactConfiguration.load(
            project.root, tracked_directory=lambda root, relative: _tracked(git, root, relative), validate_home=validate_home,
        )
        destination, = destinations
        destination.revalidate()
        return ArtifactDeclaration(project, source, destination, configuration.declared)
    except (ReviewExchangeError, ManagedWriteError, GitPolicyError, OSError) as exc:
        raise ArtifactError(str(exc), exit_code=2) from exc


def prepare_artifacts(declaration: ArtifactDeclaration, git: GitExecutionContext) -> PreparedArtifacts:
    """Prepare after domain preflight, rechecking ancestors and current tracking.

    Resolution froze the physical destination; it is never silently redirected
    by a changed declaration. Parsing and preparation semantics stay in the
    existing helper. Domains must revalidate mutable state after taking the lock.
    """
    try:
        declaration.source.revalidate()
        home = declaration.destination.revalidate()
        ignore = authorize_write(declaration.project, home / ".gitignore")
        relative = home.relative_to(declaration.project.root).as_posix()
        _require_untracked(git, declaration.project.root, relative)
        configuration = ReviewArtifactConfiguration(declaration.project.root, home, relative, declaration.declared)
        declaration.destination.revalidate()
        ignore.revalidate()
        configuration.prepare_home()
        declaration.destination.revalidate()
        ignore.revalidate()
        return PreparedArtifacts(declaration.project, declaration.destination)
    except (ReviewExchangeError, ManagedWriteError, GitPolicyError, OSError) as exc:
        raise ArtifactError(str(exc), exit_code=1) from exc


# eof
