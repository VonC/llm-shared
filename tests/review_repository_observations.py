"""Finite, read-only repository observations for review acceptance scenarios.

Tests declare tracked bytes and ignore coverage directly. This port supports
only the queries used by review policy; it cannot initialize, stage, commit,
interpret shell text or fall back to an executable.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pytest


@dataclass
class ReviewFacts:
    """Repository observations owned by one independent acceptance scenario."""

    root: Path
    tracked: dict[str, bytes] = field(default_factory=dict[str, bytes])
    ignored: bool = True
    branch: str = "resume-acceptance"

    def covers(self, relative: str) -> bool:
        """Declare ignore coverage for transient inputs and review artifacts."""
        path = Path(relative)
        return self.ignored and (path.name.startswith("a.") or path.name.startswith("review.")
                                 or ".reviews" in path.parts or "reviews" in path.parts)

    def changes(self) -> dict[str, bytes | None]:
        """Observe content changes directly, without asking Git for a status."""
        return {name: path.read_bytes() if path.is_file() else None
                for name, before in self.tracked.items()
                if not (path := self.root / name).is_file() or path.read_bytes() != before}


@dataclass
class ReviewRepositories:
    """Answer a closed vocabulary of observations over registered roots."""

    repositories: dict[Path, ReviewFacts] = field(default_factory=dict[Path, ReviewFacts])

    def facts(self, directory: Path) -> ReviewFacts:
        """Return the scenario's typed repository observations."""
        directory = directory.resolve()
        exact = self.repositories.get(directory)
        if exact is not None:
            return exact
        root = next((path for path in directory.parents if path in self.repositories), None)
        assert root is not None, f"No repository observations registered for {directory}"
        return self.repositories[root]

    def install(self, patch: pytest.MonkeyPatch) -> None:
        """Inject domain observations above native command parsing."""
        from tools import (  # noqa: PLC0415 - install only in review scenarios
            prompt_workflow_git,
            review_artifact_configuration,
            review_artifact_migration,
            review_exchange_cli,
            review_exchange_paths,
        )

        patch.setattr(review_artifact_configuration, "_tracked_directory", self.tracked_directory)
        patch.setattr(review_exchange_paths, "repository_present", self.repository_present)
        patch.setattr(review_exchange_paths, "ignored_paths", self.ignored_paths)
        patch.setattr(review_artifact_migration, "_git_ignore_checker", self.paths_ignored)
        patch.setattr(review_exchange_cli, "_is_effectively_ignored", self.path_ignored)
        patch.setattr(prompt_workflow_git, "current_branch", self.current_branch)
        patch.setattr(prompt_workflow_git, "working_tree_changed_files", self.changed_files)
        patch.setattr(prompt_workflow_git, "fork_point", self.fork_point)

    def tracked_directory(self, root: Path, relative: str) -> bool:
        """Return declared tracked membership beneath a directory."""
        return any(Path(name).is_relative_to(relative) for name in self.facts(root).tracked)

    def repository_present(self, root: Path) -> bool:
        """Return whether the scenario declares this root."""
        return root.resolve() in self.repositories

    def ignored_paths(self, root: Path, names: Sequence[str]) -> frozenset[str]:
        """Return declared ignore coverage for relative names."""
        return frozenset(name for name in names if self.facts(root).covers(name))

    def paths_ignored(self, root: Path, paths: Sequence[Path]) -> bool:
        """Check all requested paths against declared ignore coverage."""
        return all(self.path_ignored(root, path) for path in paths)

    def path_ignored(self, root: Path, path: Path) -> bool:
        """Read ignore coverage for one path."""
        return self.facts(root).covers(path.relative_to(root).as_posix())

    def current_branch(self, cwd: Path) -> str:
        """Return the declared branch."""
        return self.facts(cwd).branch

    def changed_files(self, cwd: Path) -> list[str]:
        """Return names whose declared content changed."""
        return list(self.facts(cwd).changes())

    @staticmethod
    def fork_point(_cwd: Path, _branch: str | None = None) -> None:
        """Declare that these scenarios have no branch ancestry observation."""

    @staticmethod
    def which(command: str) -> str:
        """Declare the Git dependency without searching the host executable path."""
        assert command == "git", f"Unspecified executable observation: {command}"
        return "git"

    def register(self, root: Path, tracked: dict[str, bytes] | None = None) -> ReviewFacts:
        """Declare a repository and inert index marker for nonmutation checks."""
        root = root.resolve()
        (root / ".git").mkdir(exist_ok=True)
        (root / ".git/index").write_bytes(b"declared index; never a Git database")
        facts = ReviewFacts(root, dict(tracked or {}))
        self.repositories[root] = facts
        return facts


    def run(self, command: Sequence[str], *, cwd: str | Path | None = None,
            input: str | None = None, check: bool = False, **_options: Any) -> subprocess.CompletedProcess[str]:  # noqa: A002 - subprocess port
        """Provide explicit external reads; reject every unrecognized operation."""
        assert command
        assert Path(command[0]).name.lower() in {"git", "git.exe"}, command
        args = tuple(str(value) for value in command[1:])
        args, facts = self._select(args, cwd)
        output, code = _review_output(args, facts, input or "")
        if check and code:
            raise subprocess.CalledProcessError(code, command, output, "")
        return subprocess.CompletedProcess(list(command), code, output, "")

    def _select(self, args: tuple[str, ...], cwd: str | Path | None) -> tuple[tuple[str, ...], ReviewFacts]:
        """Resolve the declared repository independently of the observation."""
        directory = Path(cwd or Path.cwd()).resolve()
        if args[:1] == ("-C",):
            directory = Path(args[1]).resolve()
            args = args[2:]
        root = next((path for path in (directory, *directory.parents) if path in self.repositories), None)
        assert root is not None, f"No repository observations registered for {directory}"
        return args, self.repositories[root]


def _review_output(args: tuple[str, ...], facts: ReviewFacts, input_text: str) -> tuple[str, int]:
    """Resolve the bounded review-policy observation vocabulary."""
    match args:
        case ("rev-parse", "--is-inside-work-tree"):
            return "true\n", 0
        case ("rev-parse", "--abbrev-ref", "HEAD") | ("for-each-ref", "--format=%(refname:short)", "refs/heads/"):
            return facts.branch + "\n", 0
        case ("status", "--porcelain") | ("status", "--porcelain", "--untracked-files=all"):
            return "".join(f" M {name}\n" for name in facts.changes()), 0
        case ("ls-files", "--", directory):
            return _tracked_directory(facts, directory), 0
        case ("check-ignore", "-z", "--stdin"):
            return _ignored_inputs(facts, input_text)
        case ("check-ignore", "-q", "--", name):
            return "", 0 if facts.covers(name) else 1
        case _:
            message = f"Unspecified review repository observation: {args!r}"
            raise AssertionError(message)


def _tracked_directory(facts: ReviewFacts, directory: str) -> str:
    """Read only tracked paths beneath the requested directory."""
    return "".join(name + "\n" for name in facts.tracked if Path(name).is_relative_to(Path(directory)))


def _ignored_inputs(facts: ReviewFacts, input_text: str) -> tuple[str, int]:
    """Return declared ignore coverage for the requested NUL-delimited paths."""
    paths = filter(None, input_text.split("\0"))
    output = "".join(path + "\0" for path in paths if facts.covers(path))
    return output, 0 if output else 1


# eof
