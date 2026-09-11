"""Resolve mandatory code-review validation commands and their sources."""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

ValidationSource = Literal["project", "plan", "request"]
DEFAULT_PROJECT_VALIDATION_COMMANDS = ("ghog day",)
_SOURCE_ORDER: tuple[ValidationSource, ...] = ("project", "plan", "request")

PROJECT_VALIDATION_FILE = ".review-validation"


def load_project_validation_commands(project_root: Path) -> tuple[str, ...]:
    """Read the project's declared mandatory commands, or the built-in default.

    The default assumes a Python project: `ghog day` walks a check step and a
    pytest step. A repository without a Python suite cannot satisfy it and, since
    the resolver has no removal operation, could never reach a complete
    validation floor whatever it did. That made commit-readiness unreachable for
    every non-Python repository rather than for one, which is a policy nobody
    wrote down.

    So the floor is declarable. The file is VERSIONED, unlike the `a.review-mode`
    marker, because it states what a repository must prove rather than how one
    machine runs: the reviewer, the transcript and every contributor read the
    same declaration.

    Declaring does not weaken the no-removal rule. Whatever a project names here
    is mandatory for it, additions still cannot subtract, and the resolved set
    still labels these commands `project` so a reader can see where the
    obligation came from. What changes is that the obligation can describe the
    repository it applies to.

    Format is one command per line; `#` comments and blank lines are ignored. An
    empty declaration is refused rather than read as "no floor": a project that
    means to keep the built-in default omits the file.

    Args:
        project_root: Repository root holding the optional declaration.

    Returns:
        The declared commands, or the built-in default when none is declared.
    """
    declaration = project_root / PROJECT_VALIDATION_FILE
    if not declaration.exists():
        return DEFAULT_PROJECT_VALIDATION_COMMANDS
    if not declaration.is_file():
        message = f"invalid {PROJECT_VALIDATION_FILE}: declaration is not a file"
        raise ReviewExchangeError(message)
    try:
        content = declaration.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        message = f"invalid {PROJECT_VALIDATION_FILE}: {error}"
        raise ReviewExchangeError(message) from error
    commands = tuple(
        stripped
        for line in content.splitlines()
        if (stripped := line.strip()) and not stripped.startswith("#")
    )
    if not commands:
        message = (
            f"invalid {PROJECT_VALIDATION_FILE}: declares no command; "
            "omit the file to keep the built-in default"
        )
        raise ReviewExchangeError(message)
    return commands


@dataclass(frozen=True)
class ResolvedValidationCommand:
    """One normalized command with every source that requires it."""

    command: str
    sources: tuple[ValidationSource, ...]

    def __post_init__(self) -> None:
        """Reject empty commands and invalid or duplicate source labels."""
        if not self.command.strip():
            raise ReviewExchangeError("validation command must be non-empty")
        if not self.sources or len(set(self.sources)) != len(self.sources):
            raise ReviewExchangeError("validation command sources must be non-empty and unique")
        if any(source not in _SOURCE_ORDER for source in self.sources):
            raise ReviewExchangeError("validation command source is unsupported")

    def to_payload(self) -> dict[str, object]:
        """Return the canonical request-payload representation."""
        return {"command": self.command, "sources": list(self.sources)}


@dataclass(frozen=True)
class ResolvedValidationSet:
    """Immutable, deterministically ordered mandatory validation commands."""

    commands: tuple[ResolvedValidationCommand, ...]

    def __post_init__(self) -> None:
        """Reject empty sets and duplicate command lines."""
        if not self.commands:
            raise ReviewExchangeError("resolved validation set must be non-empty")
        command_lines = tuple(entry.command for entry in self.commands)
        if len(set(command_lines)) != len(command_lines):
            raise ReviewExchangeError("resolved validation commands must be unique")

    @property
    def command_lines(self) -> tuple[str, ...]:
        """Return the command lines in deterministic execution order."""
        return tuple(entry.command for entry in self.commands)

    def to_payload(self) -> dict[str, object]:
        """Return the canonical request-payload representation."""
        return {"commands": [entry.to_payload() for entry in self.commands]}


def resolve_code_review_validation(
    project_defaults: Sequence[str],
    plan_additions: Sequence[str] = (),
    request_additions: Sequence[str] = (),
) -> ResolvedValidationSet:
    """Combine required defaults and additions without a removal operation."""
    if not project_defaults:
        raise ReviewExchangeError("project validation defaults must be non-empty")
    sources_by_command: dict[str, list[ValidationSource]] = {}
    for source, commands in zip(
        _SOURCE_ORDER,
        (project_defaults, plan_additions, request_additions),
        strict=True,
    ):
        for raw_command in commands:
            command = raw_command.strip()
            if not command:
                raise ReviewExchangeError("validation command must be non-empty")
            labels = sources_by_command.setdefault(command, [])
            if source not in labels:
                labels.append(source)
    return ResolvedValidationSet(
        tuple(
            ResolvedValidationCommand(command, tuple(sources))
            for command, sources in sources_by_command.items()
        ),
    )


# eof
