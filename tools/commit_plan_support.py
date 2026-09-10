"""Shared read-only repository support for commit-plan workflows.

Step 1 centralizes exact staged-path inventory so validation and future checking
use the same Git arguments, NUL decoding, ordering, and rename-side membership.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tools.git_batch_commit_models import CommitPlanSubjectRequirement
from tools.git_command import GitCommandOptions, run_cross_platform_git_command
from tools.prompt_workflow_plan import parse_validation_steps

if TYPE_CHECKING:
    from pathlib import Path

_STAGED_PATH_ARGUMENTS = (
    "diff",
    "--cached",
    "--name-only",
    "--no-renames",
    "-z",
)
_VALIDATION_PLAN_RE = re.compile(
    r"^plan\.v\d+(?:\.\d+)+\.(?P<slug>.+)\.validation\.md$",
)


def staged_paths(root: Path) -> tuple[str, ...]:
    """Return ordered staged paths, counting both sides of a rename."""
    result = run_cross_platform_git_command(
        _STAGED_PATH_ARGUMENTS,
        cwd=root,
        options=GitCommandOptions(capture_output=True, encoding="utf-8"),
    )
    return tuple(path for path in result.stdout.split("\0") if path)


def _tracked_text(root: Path, path: str, *, index: bool) -> str | None:
    """Read one path from the index or HEAD, returning None when absent."""
    listing = ("ls-files", "--stage", "--", path) if index else (
        "ls-tree",
        "--name-only",
        "HEAD",
        "--",
        path,
    )
    listed = run_cross_platform_git_command(
        listing,
        cwd=root,
        options=GitCommandOptions(capture_output=True, encoding="utf-8"),
    )
    if not listed.stdout:
        return None
    object_name = f":{path}" if index else f"HEAD:{path}"
    content = run_cross_platform_git_command(
        ("show", object_name),
        cwd=root,
        options=GitCommandOptions(capture_output=True, encoding="utf-8"),
    )
    return content.stdout


def completed_validation_subject_requirements(
    root: Path,
    paths: tuple[str, ...],
) -> tuple[CommitPlanSubjectRequirement, ...]:
    """Return exact pw subjects for validation steps newly completed in the index."""
    requirements: list[CommitPlanSubjectRequirement] = []
    for path in paths:
        match = _VALIDATION_PLAN_RE.fullmatch(PurePosixPath(path).name)
        if match is None:
            continue
        staged_text = _tracked_text(root, path, index=True)
        if staged_text is None:
            continue
        head_text = _tracked_text(root, path, index=False) or ""
        head_steps = {step.number: step.verified for step in parse_validation_steps(head_text)}
        for step in parse_validation_steps(staged_text):
            if not step.verified or head_steps.get(step.number, False):
                continue
            requirements.append(
                CommitPlanSubjectRequirement(
                    path=PurePosixPath(path.replace("\\", "/")).as_posix(),
                    subject=(
                        f"docs({match.group('slug')}): "
                        f"record step {step.number} validation"
                    ),
                ),
            )
    return tuple(requirements)


__all__ = ["completed_validation_subject_requirements", "staged_paths"]


# eof
