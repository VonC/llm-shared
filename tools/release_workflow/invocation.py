"""Freeze one validated invocation without inherited project-location authority.

Explicitly named selectors are read once as data. All project services use the
captured cwd and selected physical root; construction performs no managed writes.
Step 1 of v0.14.0 version-sources: the parsed operation tokens travel from the
request to the context unchanged; the batch-character rule covers them too.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.artifacts import ArtifactDeclaration, resolve_artifacts
from tools.release_workflow.configuration import Configuration, load_configuration
from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.paths import (
    ProjectIdentity,
    discover_project,
    validate_project,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.release_workflow.runtime_identity import RuntimeIdentity

ENTRY_KINDS = frozenset({"explicit-native", "explicit-batch", "alias-batch"})
_LEGACY = frozenset({
    "PRJ_DIR", "PRJ_DIR_UNIX", "PRJ_DIR_NAME", "VERSION_TXT_FILE", "POM_FILE",
    "PACKAGE_JSON_FILE", "HEADER_CHANGELOG_FILE", "DEV_WORKFLOW_DIR",
})


@dataclass(frozen=True)
class InvocationRequest:
    """Parsed input choices before selector resolution and project validation."""

    project_root: str | None = None
    project_root_env: str | None = None
    input_file: str | None = None
    input_file_env: str | None = None
    text: str | None = None
    input_stdin: bool = False
    non_interactive: bool = False
    operation: tuple[str, ...] = ()


@dataclass(frozen=True)
class InvocationContext:
    """Fixed identities, original caller data, computed paths and input policy.

    `operation` holds the trailing tokens the handler's validator accepted.
    """

    project: ProjectIdentity
    runtime: RuntimeIdentity
    git: GitExecutionContext
    configuration: Configuration
    artifacts: ArtifactDeclaration
    entry_kind: str
    original_argv: tuple[str, ...]
    original_cwd: Path
    non_interactive: bool
    input_file: Path | None
    input_source: str
    payload: str | None
    diagnostics: tuple[str, ...]
    operation: tuple[str, ...] = ()

    @property
    def project_name(self) -> str:
        """Name only the selected physical worktree."""
        return self.project.root.name

    @property
    def root_windows(self) -> str:
        """Return the native Windows root spelling."""
        return str(self.project.root)

    @property
    def root_posix(self) -> str:
        """Return the same root with forward slashes."""
        return self.project.root.as_posix()

    @property
    def version_file(self) -> Path:
        """Locate the project's version data."""
        return self.project.root / "version.txt"

    @property
    def pom_file(self) -> Path:
        """Locate the project's Maven declaration."""
        return self.project.root / "pom.xml"

    @property
    def package_file(self) -> Path:
        """Locate the project's package declaration."""
        return self.project.root / "package.json"

    @property
    def changelog_header(self) -> Path:
        """Locate the project's changelog header."""
        return self.project.root / "changelog-header.md"

    @property
    def dev_workflow(self) -> Path:
        """Locate the project's development workflow directory."""
        return self.project.root / "tools" / "dev_workflow"


def validate_arguments(entry_kind: str, arguments: tuple[str, ...]) -> None:
    """Reject surviving unsafe batch characters; native text remains data."""
    if entry_kind not in ENTRY_KINDS:
        msg = f"Invalid entry kind: {entry_kind!r}"
        raise ValueError(msg)
    if entry_kind.endswith("-batch") and any(char in token for token in arguments for char in '%^!"'):
        msg = "Unsupported batch argument characters; use explicit path selectors and UTF-8 file/stdin input"
        raise ValueError(msg)


def _environment_value(environment: Mapping[str, str], name: str) -> str | None:
    """Retain Windows case-insensitive lookup after freezing an environment copy."""
    normalized = name.upper()
    return next((value for key, value in environment.items() if key.upper() == normalized), None)


def _selected(direct: str | None, selector: str | None, environment: Mapping[str, str], label: str) -> tuple[str | None, str]:
    """Resolve only an explicitly named variable, retaining error provenance."""
    if direct is not None and selector is not None:
        msg = f"Conflicting {label} inputs: direct={direct!r}, selector {selector!r}={_environment_value(environment, selector)!r}"
        raise ValueError(msg)
    if selector is None:
        return direct, f"{label}={direct!r}"
    value = _environment_value(environment, selector)
    source = f"{label} selector {selector!r}={value!r}"
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", selector) is None or not value:
        msg = f"Invalid or missing {source}"
        raise ValueError(msg)
    return value, source


def _legacy_warning(environment: Mapping[str, str], original_cwd: Path, project: ProjectIdentity) -> tuple[str, ...]:
    """Compare inherited location only to explain why it has no authority."""
    inherited = _environment_value(environment, "PRJ_DIR")
    if not inherited:
        return ()
    legacy = Path(inherited)
    if not legacy.is_absolute():
        legacy = original_cwd / legacy
    if legacy.resolve() != project.root:
        return (f"Ignored stale PRJ_DIR={inherited}; validated project root is {project.root}",)
    return ()


def _input_path(locator: str | None, source: str, root: Path) -> Path | None:
    """Resolve read-only input locators relative to the validated project root."""
    if locator is None:
        return None
    if not locator:
        msg = f"Empty {source}"
        raise ValueError(msg)
    path = Path(locator)
    return path if path.is_absolute() else root / path


def create_context(request: InvocationRequest, *, runtime: RuntimeIdentity, entry_kind: str,  # noqa: PLR0913 - fixed bootstrap facts
                   original_argv: tuple[str, ...], original_cwd: Path,
                   environment: Mapping[str, str], stdin_console: bool) -> InvocationContext:
    """Compose preflight services once with no fallback to ambient project state."""
    validate_arguments(entry_kind, original_argv)
    supplied, source = _selected(request.project_root, request.project_root_env, environment, "project root")
    locator, input_source = _selected(request.input_file, request.input_file_env, environment, "input file")
    if sum((locator is not None, request.text is not None, request.input_stdin)) > 1:
        msg = f"Conflicting payload inputs: {input_source}, text or stdin"
        raise ValueError(msg)
    if supplied is None and entry_kind != "alias-batch":
        msg = "An explicit project root is required (--project-root or --project-root-env)"
        raise ValueError(msg)
    non_interactive = request.non_interactive or not stdin_console
    child_environment = {key: value for key, value in environment.items() if key.upper() not in _LEGACY}
    git = GitExecutionContext.create(child_environment, original_cwd=original_cwd, non_interactive=non_interactive)
    try:
        project = discover_project(original_cwd, git) if supplied is None else validate_project(supplied, git)
    except ValueError as exc:
        msg = f"{source}: {exc}"
        raise ValueError(msg) from exc
    diagnostics = (*git.diagnostics, *_legacy_warning(environment, original_cwd, project))
    input_file = _input_path(locator, input_source, project.root)
    return InvocationContext(
        project, runtime, git, load_configuration(project), resolve_artifacts(project, git),
        entry_kind, original_argv, original_cwd, non_interactive, input_file,
        input_source, request.text, tuple(diagnostics), request.operation,
    )


# eof
