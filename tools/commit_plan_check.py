"""Read-only commit-plan readiness service and command-line adapter.

Step 2 exposes immutable human and JSON evidence over the existing parser,
shared staged inventory, and public validator without entering commit execution.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import NoReturn

from tools import find_project_root
from tools.commit_plan_support import (
    completed_validation_subject_requirements,
    staged_paths,
)
from tools.git_batch_commit_models import (
    CommitMessageError,
    CommitPlanGroup,
    CommitPlanValidation,
)
from tools.git_batch_commit_parsing import parse_clipboard_content
from tools.git_batch_commit_validation import validate_commit_plan

_OPERATIONAL_STATUS = 2
_NON_READY_STATUS = 3


class CommitPlanCheckState(StrEnum):
    """Stable states reported by the root commit-plan checker."""

    VALID = "valid"
    MISSING_PLAN = "missing-plan"
    EMPTY_PLAN = "empty-plan"
    EMPTY_STAGED_SET = "empty-staged-set"
    INVALID_PLAN = "invalid-plan"
    OPERATIONAL_FAILURE = "operational-failure"


@dataclass(frozen=True)
class CommitPlanCheckResult:
    """Immutable evidence produced by one commit-plan check."""

    state: CommitPlanCheckState
    groups: tuple[CommitPlanGroup, ...] = ()
    diagnostics: tuple[str, ...] = ()
    staged_paths: tuple[str, ...] = ()

    @property
    def ready(self) -> bool:
        """Return whether the result authorizes readiness to be considered."""
        return self.state is CommitPlanCheckState.VALID and not self.diagnostics

    def structured_payload(self) -> dict[str, object]:
        """Project this result into the stable structured evidence schema."""
        return {
            "schema_version": 1,
            "state": self.state.value,
            "ready": self.ready,
            "staged_paths": list(self.staged_paths),
            "groups": [
                {
                    "position": group.position,
                    "subject": group.subject,
                    "paths": list(group.paths),
                }
                for group in self.groups
            ],
            "diagnostics": list(self.diagnostics),
        }


def _read_plan(plan_path: Path) -> str:
    """Read the one canonical root plan exactly once."""
    return plan_path.read_text(encoding="utf-8")


def _operational_result(action: str, err: Exception) -> CommitPlanCheckResult:
    """Return one stable operational diagnostic for a failed boundary."""
    return CommitPlanCheckResult(
        state=CommitPlanCheckState.OPERATIONAL_FAILURE,
        diagnostics=(f"cannot {action} commit plan: {err}",),
    )


def _result_from_validation(
    validation: CommitPlanValidation,
    inventory: tuple[str, ...],
) -> CommitPlanCheckResult:
    """Wrap unchanged validator evidence with checker input-state meaning."""
    if not inventory:
        state = CommitPlanCheckState.EMPTY_STAGED_SET
    elif validation.valid:
        state = CommitPlanCheckState.VALID
    else:
        state = CommitPlanCheckState.INVALID_PLAN
    return CommitPlanCheckResult(
        state=state,
        groups=validation.groups,
        diagnostics=validation.diagnostics,
        staged_paths=inventory,
    )


def check_commit_plan(root: Path) -> CommitPlanCheckResult:  # noqa: PLR0911
    """Check ``<root>/a.commit`` against exact staged membership without writes."""
    plan_path = root / "a.commit"
    if not plan_path.is_file():
        return CommitPlanCheckResult(
            state=CommitPlanCheckState.MISSING_PLAN,
            diagnostics=("root a.commit is missing",),
        )

    try:
        content = _read_plan(plan_path)
    except (OSError, UnicodeError) as err:
        return _operational_result("read", err)
    if not content.strip():
        return CommitPlanCheckResult(
            state=CommitPlanCheckState.EMPTY_PLAN,
            diagnostics=("a.commit is empty",),
        )

    try:
        blocks = parse_clipboard_content(content, interactive=False)
    except CommitMessageError as err:
        return CommitPlanCheckResult(
            state=CommitPlanCheckState.INVALID_PLAN,
            diagnostics=(f"cannot parse a.commit: {err}",),
        )
    except Exception as err:  # noqa: BLE001  # pragma: no cover
        return _operational_result("parse", err)
    if not blocks:
        return CommitPlanCheckResult(
            state=CommitPlanCheckState.EMPTY_PLAN,
            diagnostics=("a.commit contains no commit groups",),
        )

    try:
        inventory = staged_paths(root)
    except Exception as err:  # noqa: BLE001 - Git failures vary by platform.
        return _operational_result("inventory", err)
    try:
        requirements = completed_validation_subject_requirements(root, inventory)
        validation = validate_commit_plan(blocks, inventory, requirements)
    except Exception as err:  # noqa: BLE001  # pragma: no cover
        return _operational_result("validate", err)
    return _result_from_validation(validation, inventory)


def render_human(result: CommitPlanCheckResult) -> str:
    """Render deterministic line-oriented evidence for human quotation."""
    lines = [
        f"state: {result.state.value}",
        f"ready: {str(result.ready).lower()}",
    ]
    for group in result.groups:
        lines.append(f"group {group.position}: {group.subject}")
        lines.extend(f"group {group.position} path: {path}" for path in group.paths)
    lines.extend(f"staged path: {path}" for path in result.staged_paths)
    lines.extend(f"diagnostic: {diagnostic}" for diagnostic in result.diagnostics)
    return "\n".join(lines)


def render_json(result: CommitPlanCheckResult) -> str:
    """Render deterministic compact JSON from the shared typed result."""
    return json.dumps(result.structured_payload(), ensure_ascii=False, separators=(",", ":"))


class _InvocationError(Exception):
    """Raised when CLI arguments do not satisfy the command contract."""


class _ArgumentParser(argparse.ArgumentParser):
    """Convert argparse usage errors into the command's status-two contract."""

    def error(self, message: str) -> NoReturn:
        raise _InvocationError(message)


def _parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(description="Check read-only root a.commit readiness.")
    parser.add_argument("--root", type=Path, help="explicit Git repository root")
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="evidence rendering format",
    )
    return parser


def _resolve_root(explicit_root: Path | None) -> Path:
    """Resolve and validate either an explicit root or upward discovery."""
    if explicit_root is None:
        return find_project_root(Path.cwd())
    root = explicit_root.resolve()
    if not (root / ".git").is_dir():
        msg = f"not a Git repository root: {root}"
        raise FileNotFoundError(msg)
    return root


def main(argv: list[str] | None = None) -> int:
    """Run one read-only check and map it to stdout, stderr, and stable status."""
    try:
        args = _parser().parse_args(argv)
        root = _resolve_root(args.root)
        result = check_commit_plan(root)
    except _InvocationError as err:
        sys.stderr.write(f"commit-plan-check: {err}\n")
        return 2
    except (OSError, ValueError) as err:
        sys.stderr.write(f"commit-plan-check: {err}\n")
        return 2
    except Exception as err:  # noqa: BLE001  # pragma: no cover
        sys.stderr.write(f"commit-plan-check: unexpected failure: {err}\n")
        return 2

    if result.state is CommitPlanCheckState.OPERATIONAL_FAILURE:
        diagnostic = result.diagnostics[0] if result.diagnostics else result.state.value
        sys.stderr.write(f"commit-plan-check: {diagnostic}\n")
        return 2

    renderer = render_json if args.format == "json" else render_human
    sys.stdout.write(f"{renderer(result)}\n")
    if not result.ready:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CommitPlanCheckResult",
    "CommitPlanCheckState",
    "check_commit_plan",
    "main",
    "render_human",
    "render_json",
]


# eof
