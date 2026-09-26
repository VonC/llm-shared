#!/usr/bin/env python3
"""Plan prepare-release topology and preview conflicts without changing refs.

Fix: every working file of a release run (the `a.prepare-release.active` flag,
the preview object directories, any backup or scratch copy) lives in the
project's review artifact home, never at the project root (see
`rules/artifact_files.md`). `--artifact-home` prints that prepared home for
`--root` and exits, so the `prepare-release` instruction resolves the one
deterministic folder it touches and removes the flag in, through the same
launcher it already calls, whatever `.review-artifacts.ini` declares.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from tools.artifact_home import artifact_home
from tools.prepare_release.prepare_release_plan_models import (
    ReleasePlan,
    ReleasePlanError,
)
from tools.prepare_release.prepare_release_plan_workflow import build_release_plan

if TYPE_CHECKING:
    from collections.abc import Sequence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prepare-release-plan",
        description=(
            "Detect the prepare-release branch role, exact operation, and likely Git conflicts."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--main", default="main", help="Release branch name.")
    parser.add_argument("--integration", help="Integration branch override.")
    parser.add_argument(
        "--umbrella",
        type=Path,
        help="Collection draft whose slug names this topic's integration branch.",
    )
    parser.add_argument("--branch", help="Ref to plan instead of checked-out HEAD.")
    parser.add_argument("--feature-base", help="Confirmed feature boundary commit.")
    parser.add_argument("--feature-parent", help="Confirmed feature parent branch.")
    parser.add_argument(
        "--feature-target",
        choices=("auto", "main", "integration"),
        default="auto",
        help="Land feature mode on main, or on the resolved integration branch first.",
    )
    parser.add_argument(
        "--no-conflict-preview",
        action="store_true",
        help="Detect topology without invoking git merge-tree.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--artifact-home",
        action="store_true",
        help="Print the prepared review artifact home of --root, where run files live, and exit.",
    )
    return parser


def print_artifact_home(root: Path) -> int:
    """Prepare and print the review artifact home that holds release run files.

    Args:
        root: The project root.

    Returns:
        0 with the home path printed, 2 with an ERROR line when it is invalid.
    """
    try:
        home = artifact_home(root.resolve())
    except (OSError, ValueError) as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return 2
    sys.stdout.write(f"{home}\n")
    return 0


def render_plan(plan: ReleasePlan) -> str:
    """Render one human-readable plan."""
    lines = [
        *_header_lines(plan),
        *_boundary_lines(plan),
        *_commit_lines(plan),
        *_operation_lines(plan),
        *_conflict_lines(plan),
        *(f"Note: {note}" for note in plan.notes),
    ]
    return "\n".join(lines)


def _header_lines(plan: ReleasePlan) -> list[str]:
    """Render stable plan identity fields."""
    return [
        f"Release mode: {plan.mode}",
        f"Start branch: {plan.branch} ({plan.branch_oid[:12]})",
        f"Action: {plan.action}",
        f"Scope: {plan.scope} ({len(plan.commits)} commits)",
    ]


def _boundary_lines(plan: ReleasePlan) -> list[str]:
    """Render feature boundary evidence and alternatives."""
    lines: list[str] = []
    if plan.feature_base:
        lines.append(f"Feature base: {plan.feature_base}")
    if plan.boundary_evidence:
        lines.append(f"Boundary evidence: {plan.boundary_evidence}")
    if not plan.boundary_candidates:
        return lines
    lines.append("Boundary candidates:")
    for candidate in plan.boundary_candidates:
        parents = ", ".join(candidate.parent_refs) or "unknown parent"
        lines.append(
            f"  {candidate.base} ({candidate.commit_count} commits; {parents}; "
            f"{candidate.evidence})",
        )
    return lines


def _commit_lines(plan: ReleasePlan) -> list[str]:
    """Render the exact selected commits."""
    if not plan.commits:
        return []
    return ["Selected commits:", *(f"  {commit.oid[:12]} {commit.subject}" for commit in plan.commits)]


def _operation_lines(plan: ReleasePlan) -> list[str]:
    """Render the proposed Git and validation operations."""
    if not plan.operations:
        return []
    return ["Proposed operations:", *(f"  {operation}" for operation in plan.operations)]


def _conflict_lines(plan: ReleasePlan) -> list[str]:
    """Render merge-tree results for a merge or sequential rebase preview."""
    preview = plan.merge_preview
    label = "Merge conflict preview"
    if plan.rebase_preview is not None:
        rebase = plan.rebase_preview
        if rebase.clean:
            return [
                f"Rebase conflict preview: clean through {rebase.checked_commits} commits",
            ]
        preview = rebase.merge
        label = (
            f"Rebase conflict preview at {rebase.conflict_commit[:12]} "
            f"{rebase.conflict_subject}"
            if rebase.conflict_commit and rebase.conflict_subject
            else "Rebase conflict preview"
        )
    if preview is None:
        return []
    if preview.clean:
        return [f"{label}: clean"]
    lines = [f"{label}: conflicts likely"]
    lines.extend(f"  file: {path}" for path in preview.conflicted_files)
    for conflict in preview.conflicts:
        paths = ", ".join(conflict.paths)
        lines.extend(
            [
                f"  {conflict.conflict_type}: {paths}",
                f"    {conflict.message}",
            ],
        )
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    """Run the release planner CLI."""
    args = _parser().parse_args(argv)
    if args.artifact_home:
        return print_artifact_home(args.root)
    try:
        plan = build_release_plan(
            args.root,
            main_branch=args.main,
            integration_branch=args.integration,
            umbrella=args.umbrella,
            branch=args.branch,
            feature_base=args.feature_base,
            feature_parent=args.feature_parent,
            feature_target=args.feature_target,
            preview_conflicts=not args.no_conflict_preview,
        )
    except ReleasePlanError as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return 2
    output = json.dumps(plan.to_dict(), indent=2) if args.json else render_plan(plan)
    sys.stdout.write(f"{output}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
