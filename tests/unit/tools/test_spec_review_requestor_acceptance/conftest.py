"""Fast Git protocol boundary for specification requestor acceptance tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import review_exchange_cli, spec_review_request
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_paths import transient_paths_for_ignore

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models import ArtifactPaths


def _is_ignored(root: Path, path: Path) -> bool:
    """Declare ignored scratch inputs and the prepared artifact home."""
    relative = path.relative_to(root)
    return relative.parts[0] == ".reviews" or (
        len(relative.parts) == 1 and relative.name.startswith("a.")
    )


def _validate_activation(root: Path, paths: ArtifactPaths) -> None:
    resolved = root.resolve()
    if not (resolved / ".git").is_dir():
        message = "review mode requires a Git repository"
        raise ReviewExchangeError(message)
    ReviewArtifactConfiguration.load(resolved).prepare_home()
    assert (resolved / ".reviews/.gitignore").read_bytes() == b"*\n"
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
    """Keep acceptance journeys at the parsed Git-result boundary."""
    monkeypatch.setattr(review_exchange_cli, "validate_activation", _validate_activation)
    monkeypatch.setattr(review_exchange_cli, "_is_effectively_ignored", _is_ignored)
    monkeypatch.setattr(spec_review_request, "_is_effectively_ignored", _is_ignored)
