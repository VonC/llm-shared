"""Session-built real Git template for code-reviewer acceptance efforts.

Every scenario still receives an independent temporary repository. Building
the common baseline once removes repeated Windows Git startup while preserving
real index, object, ignore, and pathspec behavior in every copied effort.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.git_test_double import GitTestDouble, RepositoryState

from .fixtures import configure_repository_template, create_repository_template

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def repository_template(tmp_path_factory: pytest.TempPathFactory) -> Iterator[None]:
    """Build one real staged repository and copy it into each scenario root."""
    root: Path = tmp_path_factory.mktemp("code-reviewer-template") / "repository"
    create_repository_template(root)
    configure_repository_template(root)
    try:
        yield
    finally:
        configure_repository_template(None)


def _copied_repository(root: Path) -> RepositoryState | None:
    """Load the known staged baseline from one copied real repository."""
    if not (root / ".git").is_dir():
        return None
    staged = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(root).parts
        and ".reviews" not in path.relative_to(root).parts
        and not path.relative_to(root).as_posix().startswith("a.")
    }
    committed = dict(staged)
    committed["reviewed.py"] = b"VALUE = 1\n"
    return RepositoryState(staged=staged, committed=committed)


@pytest.fixture
def real_git_commands() -> bool:
    """Select real Git subprocesses for one explicit acceptance boundary."""
    return True


@pytest.fixture(autouse=True)
def fast_git_commands(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skip repeated Git startup outside the explicit real-Git journeys."""
    if "real_git_commands" in request.fixturenames:
        return
    git_double = GitTestDouble(subprocess.run, lazy_repository=_copied_repository)
    monkeypatch.setattr(subprocess, "run", git_double.run)
