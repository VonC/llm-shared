"""Declared external observations for the production evidence implementation."""

from __future__ import annotations

import pytest

from tests.code_review_repository_observations import install_observations


@pytest.fixture(autouse=True)
def repository_observations(monkeypatch: pytest.MonkeyPatch) -> None:
    """No subprocess, command mutation or executable fallback is available."""
    install_observations(monkeypatch)


# eof
