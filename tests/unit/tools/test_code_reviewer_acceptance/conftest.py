"""Reusable data files and declared repository inputs for reviewer scenarios."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.code_review_repository_observations import install_observations

from .fixtures import configure_repository_template, create_repository_template

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def repository_template(tmp_path_factory: pytest.TempPathFactory) -> Iterator[None]:
    """Write one small file template for independent scenario copies."""
    root: Path = tmp_path_factory.mktemp("code-reviewer-template") / "repository"
    create_repository_template(root)
    configure_repository_template(root)
    try:
        yield
    finally:
        configure_repository_template(None)


@pytest.fixture(autouse=True)
def repository_observations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bind external reads without process or command-mutation fallbacks."""
    install_observations(monkeypatch)
