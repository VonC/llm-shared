"""Side-effect-free validation shared by reviewers and batch execution."""

from __future__ import annotations

import re
import shlex
from collections import Counter
from pathlib import PurePosixPath

from tools.git_batch_commit_models import (
    CommitBlock,
    CommitPlanGroup,
    CommitPlanSubjectRequirement,
    CommitPlanValidation,
)

_CONVENTIONAL_SUBJECT_RE = re.compile(
    r"^(?:build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"(?:\([a-z0-9][a-z0-9._/-]*\))?!?:\s+\S.*$",
)
_MIN_COMMAND_PARTS = 3


def _git_add_paths(command: str) -> list[str] | None:
    try:
        parts = shlex.split(command, posix=True)
    except ValueError:
        return None
    if len(parts) < _MIN_COMMAND_PARTS or parts[:2] != ["git", "add"]:
        return None
    arguments = parts[2:]
    if "--" in arguments:
        return arguments[arguments.index("--") + 1 :]
    return [item for item in arguments if not item.startswith("-")]


def _safe_relative_path(value: str) -> str | None:
    normalized = PurePosixPath(value.replace("\\", "/"))
    unsafe = normalized.is_absolute() or ".." in normalized.parts or not normalized.parts
    return None if unsafe else normalized.as_posix()


def _path_from_git_add(command: str) -> str | None:
    """Return the one repository-relative path from a supported git-add line."""
    paths = _git_add_paths(command)
    if paths is None or len(paths) != 1:
        return None
    return _safe_relative_path(paths[0])


def _validate_group(
    position: int,
    block: CommitBlock,
) -> tuple[CommitPlanGroup, list[str]]:
    diagnostics: list[str] = []
    paths: list[str] = []
    if _CONVENTIONAL_SUBJECT_RE.fullmatch(block.commit_title) is None:
        diagnostics.append(
            f"group {position} subject is not conventional: {block.commit_title}",
        )
    for command in block.git_adds:
        path = _path_from_git_add(command)
        if path is None:
            diagnostics.append(f"group {position} has unsupported git add: {command}")
        else:
            paths.append(path)
    return CommitPlanGroup(position, block.commit_title, tuple(paths)), diagnostics


def _membership_diagnostics(
    planned_paths: list[str],
    staged_paths: list[str] | tuple[str, ...],
) -> list[str]:
    duplicates = sorted(path for path, count in Counter(planned_paths).items() if count > 1)
    diagnostics = [f"planned path appears in multiple groups: {path}" for path in duplicates]
    planned = set(planned_paths)
    staged = {PurePosixPath(path.replace("\\", "/")).as_posix() for path in staged_paths}
    diagnostics.extend(f"planned path is not staged: {path}" for path in sorted(planned - staged))
    diagnostics.extend(f"staged path is missing from the plan: {path}" for path in sorted(staged - planned))
    return diagnostics


def _subject_requirement_diagnostics(
    groups: list[CommitPlanGroup],
    requirements: tuple[CommitPlanSubjectRequirement, ...],
) -> list[str]:
    """Require workflow-owned subjects on the groups containing their paths."""
    diagnostics: list[str] = []
    for requirement in requirements:
        matching = [group for group in groups if requirement.path in group.paths]
        if len(matching) != 1 or matching[0].subject == requirement.subject:
            continue
        group = matching[0]
        diagnostics.append(
            f"group {group.position} containing completed validation plan "
            f"{requirement.path} must use exact subject: {requirement.subject}",
        )
    return diagnostics


def validate_commit_plan(
    blocks: list[CommitBlock],
    staged_paths: list[str] | tuple[str, ...],
    subject_requirements: tuple[CommitPlanSubjectRequirement, ...] = (),
) -> CommitPlanValidation:
    """Validate groups, subjects, workflow markers, and staged membership."""
    diagnostics: list[str] = []
    groups: list[CommitPlanGroup] = []
    planned_paths: list[str] = []
    for position, block in enumerate(blocks, start=1):
        group, group_diagnostics = _validate_group(position, block)
        groups.append(group)
        planned_paths.extend(group.paths)
        diagnostics.extend(group_diagnostics)
    diagnostics.extend(_membership_diagnostics(planned_paths, staged_paths))
    diagnostics.extend(_subject_requirement_diagnostics(groups, subject_requirements))
    return CommitPlanValidation(tuple(groups), tuple(diagnostics))


__all__ = ["validate_commit_plan"]


# eof
