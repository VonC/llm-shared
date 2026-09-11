"""Recorded Git activation boundary for review-exchange acceptance tests."""

from __future__ import annotations

import fnmatch
from typing import TYPE_CHECKING

import pytest

from tools import review_exchange_cli
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_paths import transient_paths_for_ignore

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models import ArtifactPaths


def _is_ignored(root: Path, path: Path) -> bool:
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    checks = ((root / ".gitignore", relative), (path.parent / ".gitignore", path.name))
    return any(
        ignore_file.is_file()
        and any(
            fnmatch.fnmatch(candidate, pattern)
            for pattern in ignore_file.read_text(encoding="utf-8").splitlines()
        )
        for ignore_file, candidate in checks
    )


def _validate_activation(root: Path, paths: ArtifactPaths) -> None:
    resolved = root.resolve()
    if not (resolved / ".git").is_dir():
        message = "review mode requires a Git repository"
        raise ReviewExchangeError(message)
    ReviewArtifactConfiguration.load(resolved).prepare_home()
    missing = [
        path.relative_to(resolved).as_posix()
        for path in transient_paths_for_ignore(paths)
        if not _is_ignored(resolved, path)
    ]
    if missing:
        message = "review transient paths are not effectively ignored: " + ", ".join(
            missing,
        )
        raise ReviewExchangeError(message)


@pytest.fixture(autouse=True)
def recorded_git_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use parsed repository and ignore results without launching Git."""
    monkeypatch.setattr(review_exchange_cli, "validate_activation", _validate_activation)
    monkeypatch.setattr(review_exchange_cli, "_is_effectively_ignored", _is_ignored)
