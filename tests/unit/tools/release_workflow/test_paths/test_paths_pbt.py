"""Bounded path properties, with explicit shortest and deepest examples.

Each generated case resolves real filesystem ancestors twice. Keep the same
strategy and assertions with twenty examples plus deterministic boundaries.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from tools.release_workflow.paths import (
    ProjectIdentity,
    ProjectPathError,
    authorize_path,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("_batch", range(4))
@settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
@example(parts=["a"])
@example(parts=["a0123456789bc"] * 8)
@given(parts=st.lists(st.text(alphabet="abcdefgh0123456789", min_size=1, max_size=12), min_size=1, max_size=8))
def test_future_segments_stay_under_root(tmp_path: Path, _batch: int, parts: list[str]) -> None:
    """Ordinary future segments preserve their relative value without I/O scans."""
    identity = ProjectIdentity(tmp_path, tmp_path / ".git", tmp_path / ".git", str(tmp_path))
    target = authorize_path(identity, "/".join(parts))
    assert target == tmp_path.joinpath(*parts)
    assert authorize_path(identity, "./" + "/".join(parts)) == target


@pytest.mark.parametrize("levels", range(1, 13))
def test_parent_segments_cannot_escape(tmp_path: Path, levels: int) -> None:
    """Exhaust every supported traversal depth without a subprocess."""
    identity = ProjectIdentity(tmp_path, tmp_path / ".git", tmp_path / ".git", str(tmp_path))
    with pytest.raises(ProjectPathError):
        authorize_path(identity, "../" * levels + "foreign-release-file")


# eof
