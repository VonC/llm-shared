"""Explicit repository observations for requestor orchestration acceptance."""

from __future__ import annotations

import pytest

from tests.code_review_repository_observations import install_observations


@pytest.fixture(autouse=True)
def repository_observations(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep production policy over declared inputs without process fallbacks."""
    install_observations(monkeypatch)
