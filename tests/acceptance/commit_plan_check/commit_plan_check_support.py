"""Shared real-repository builders for the commit-plan-check acceptance modules.

The acceptance scenarios all need the same Git setup, adapter invocation and
state snapshot. They used to live beside the scenarios in one module, which
made that module the longest-running file of the suite and therefore the
critical path of the parallel walk, because ``--dist loadscope`` keeps every
test of one module on a single worker.

Fix: extract the builders so the scenarios can live in sibling modules that
run on separate workers. No builder changed behavior; only their names became
public, since they now cross a module boundary.
"""

# ruff: noqa: S603, S607

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from tools import commit_plan_check

NON_READY_STATUS = 3
OPERATIONAL_STATUS = 2
TREE_A = "a" * 40
TREE_B = "b" * 40


@dataclass(frozen=True)
class RepositoryState:
    """Observable repository state protected by the checker contract."""

    head: str
    index_tree: str
    staged_paths: tuple[str, ...]
    worktree_diff: bytes
    plan_bytes: bytes | None
    ignored_root: tuple[str, ...]


def git(root: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    """Run one required Git setup or snapshot command."""
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
    )


def commit(root: Path, message: str) -> None:
    """Create one deterministic local fixture commit."""
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Commit Plan Acceptance",
            "-c",
            "user.email=acceptance@example.invalid",
            "commit",
            "-q",
            "-m",
            message,
        ],
        check=True,
        capture_output=True,
    )


def initialize_repository(root: Path) -> None:
    """Create a repository with one stable HEAD and ignored root evidence."""
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "baseline.txt").write_text("baseline\n", encoding="utf-8")
    git(root, "add", "--", ".gitignore", "baseline.txt")
    commit(root, "test: create baseline")


def valid_plan(
    *paths: str,
    subject: str = "feat(check): validate staged paths",
) -> str:
    """Build one parser-valid group for the supplied exact membership."""
    commands = "\n".join(f"git add -- {path}" for path in paths)
    return f"""{commands}

{subject}

Why:

The staged paths need one exact read-only plan.

The checker can now report mechanical readiness.

What:

- validate every staged path
"""


def stage_sample(root: Path) -> None:
    """Create and stage the common sample path."""
    (root / "sample.txt").write_text("sample\n", encoding="utf-8")
    git(root, "add", "--", "sample.txt")


def module_environment() -> dict[str, str]:
    """Expose the project module while keeping the fixture as caller root."""
    environment = os.environ.copy()
    project_root = str(Path(commit_plan_check.__file__).resolve().parent.parent)
    previous = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        f"{project_root}{os.pathsep}{previous}" if previous else project_root
    )
    return environment


def adapter_arguments(root: Path, adapter: str, output_format: str) -> list[str]:
    """Return one module or root-launcher command over the same service."""
    common = ["--root", str(root), "--format", output_format]
    if adapter == "module":
        return [sys.executable, "-m", "tools.commit_plan_check", *common]
    project_root = Path(commit_plan_check.__file__).resolve().parent.parent
    return [str(project_root / "commit-plan-check.bat"), *common]


def run_adapter(
    root: Path,
    adapter: str,
    output_format: str,
) -> subprocess.CompletedProcess[str]:
    """Run one public adapter with bounded process completion."""
    return subprocess.run(
        adapter_arguments(root, adapter, output_format),
        cwd=root,
        env=module_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def snapshot(root: Path) -> RepositoryState:
    """Capture every repository surface named by the no-mutation contract."""
    plan = root / "a.commit"
    ignored = git(
        root,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
        "--",
        "a.*",
    ).stdout
    return RepositoryState(
        head=git(root, "rev-parse", "HEAD").stdout.decode().strip(),
        index_tree=git(root, "write-tree").stdout.decode().strip(),
        staged_paths=tuple(
            part.decode()
            for part in git(
                root,
                "diff",
                "--cached",
                "--name-only",
                "--no-renames",
                "-z",
            ).stdout.split(b"\0")
            if part
        ),
        worktree_diff=git(root, "diff", "--binary").stdout,
        plan_bytes=plan.read_bytes() if plan.exists() else None,
        ignored_root=tuple(part.decode() for part in ignored.split(b"\0") if part),
    )


def human_fragments(payload: object) -> tuple[str, ...]:
    """Project structured evidence into the fragments rendered for humans."""
    structured = cast("dict[str, object]", payload)
    groups = cast("list[dict[str, object]]", structured["groups"])
    fragments = [
        f"state: {structured['state']}",
        f"ready: {str(structured['ready']).lower()}",
    ]
    for group in groups:
        fragments.append(cast("str", group["subject"]))
        fragments.extend(cast("list[str]", group["paths"]))
    fragments.extend(cast("list[str]", structured["diagnostics"]))
    return tuple(fragments)


# eof
