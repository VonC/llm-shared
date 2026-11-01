"""Direct CLI scenarios over declared repository contents and index inputs."""

from __future__ import annotations

import io
import shutil
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from typing import TYPE_CHECKING, TextIO, cast

from tests.acceptance.commit_plan_check.repository_observations import (
    PLANS,
    declare_index,
    declare_repository,
)
from tools import commit_plan_check

if TYPE_CHECKING:
    from pathlib import Path

NON_READY_STATUS = 3
OPERATIONAL_STATUS = 2
TREE_A = "a" * 40
TREE_B = "b" * 40


@dataclass(frozen=True)
class RepositoryState:
    """Observable repository state protected by the checker contract."""

    baseline: tuple[tuple[str, bytes], ...]
    index: tuple[tuple[str, bytes], ...]
    staged_paths: tuple[str, ...]
    files: tuple[tuple[str, bytes], ...]
    plan_bytes: bytes | None


def build_repository_seed(root: Path) -> None:
    """Write the two baseline files without initializing a Git database."""
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "baseline.txt").write_text("baseline\n", encoding="utf-8")


def initialize_repository(root: Path, seed: Path) -> None:
    """Copy fixture data and declare an independent baseline and index."""
    shutil.copytree(seed, root, dirs_exist_ok=True)
    declare_repository(root, {name: (root / name).read_bytes()
                              for name in (".gitignore", "baseline.txt")})


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
    declare_index(root, "sample.txt")


def run_adapter(
    root: Path,
    output_format: str,
    *,
    stdout: TextIO | None = None,
) -> subprocess.CompletedProcess[str]:
    """Invoke the real CLI parser and service with captured or caller-owned IO."""
    captured, errors = io.StringIO(), io.StringIO()
    arguments = ["--root", str(root), "--format", output_format]
    with redirect_stdout(stdout if stdout is not None else captured), redirect_stderr(errors):
        status = commit_plan_check.main(arguments)
    return subprocess.CompletedProcess(arguments, status, captured.getvalue(), errors.getvalue())


def snapshot(root: Path) -> RepositoryState:
    """Capture every repository surface named by the no-mutation contract."""
    plan = root / "a.commit"
    facts = PLANS[root.resolve()]
    return RepositoryState(
        baseline=tuple(sorted(facts.baseline.items())),
        index=tuple(sorted(facts.index.items())),
        staged_paths=facts.changed_paths(),
        files=tuple(sorted((path.relative_to(root).as_posix(), path.read_bytes())
                           for path in root.rglob("*") if path.is_file())),
        plan_bytes=plan.read_bytes() if plan.exists() else None,
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
