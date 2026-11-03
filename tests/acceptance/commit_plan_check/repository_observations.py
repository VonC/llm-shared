"""Declared baseline/index inputs for commit-plan acceptance; no command mutations."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tests.review_repository_observations import ReviewRepositories

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from tools.git_command import GitCommandOptions


@dataclass
class PlanFacts:
    """Explicit versioned bytes read by the production commit-plan policy."""

    baseline: dict[str, bytes] = field(default_factory=dict[str, bytes])
    index: dict[str, bytes] = field(default_factory=dict[str, bytes])

    def changed_paths(self) -> tuple[str, ...]:
        """Report the declared index difference, including both sides of renames."""
        return tuple(sorted(name for name in self.baseline.keys() | self.index.keys()
                            if self.baseline.get(name) != self.index.get(name)))


REVIEW_REPOSITORIES = ReviewRepositories()
PLANS: dict[Path, PlanFacts] = {}


def declare_repository(root: Path, baseline: dict[str, bytes]) -> None:
    """Register immutable starting observations and an independent index mapping."""
    REVIEW_REPOSITORIES.register(root, baseline)
    PLANS[root.resolve()] = PlanFacts(dict(baseline), dict(baseline))


def declare_baseline(root: Path, *paths: str) -> None:
    """Supply baseline file contents directly, without creating Git objects."""
    facts = PLANS[root.resolve()]
    for name in paths:
        content = (root / name).read_bytes()
        facts.baseline[name] = content
        facts.index[name] = content
        REVIEW_REPOSITORIES.repositories[root.resolve()].tracked[name] = content


def declare_index(root: Path, *paths: str) -> None:
    """Supply the index observation for each explicit path, including deletion."""
    facts = PLANS[root.resolve()]
    for name in paths:
        path = root / name
        if path.is_file():
            facts.index[name] = path.read_bytes()
        else:
            facts.index.pop(name, None)


def read_index(arguments: Sequence[str], *, cwd: Path,
               options: GitCommandOptions | None = None) -> subprocess.CompletedProcess[str]:
    """Answer only production inventory/content reads; never execute or mutate."""
    del options
    command = tuple(arguments)
    facts = PLANS.get(cwd.resolve())
    if facts is None:
        message = "declared repository inventory is unavailable"
        raise OSError(message)

    output = _index_output(command, facts)
    return subprocess.CompletedProcess(list(arguments), 0, output, "")


def _index_output(command: tuple[str, ...], facts: PlanFacts) -> str:
    """Answer the finite content and inventory vocabulary."""
    match command:
        case ("diff", "--cached", "--name-only", "--no-renames", "-z"):
            return "".join(name + "\0" for name in facts.changed_paths())
        case ("write-tree",):
            return "a" * 40 + "\n"
        case ("ls-files", "--stage", "--", name):
            return name if name in facts.index else ""
        case ("ls-tree", "--name-only", "HEAD", "--", name):
            return name if name in facts.baseline else ""
        case ("show", reference):
            return _versioned_text(facts, reference)
        case _:
            message = f"undeclared commit-plan observation: {command!r}"
            raise AssertionError(message)


def _versioned_text(facts: PlanFacts, reference: str) -> str:
    """Read explicitly supplied index or baseline bytes."""
    revision, name = reference.split(":", 1)
    assert revision in {"", "HEAD"}
    return (facts.index if not revision else facts.baseline)[name].decode("utf-8")


# eof
