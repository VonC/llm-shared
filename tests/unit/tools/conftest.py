"""Shared fast boundaries for tools unit tests."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest

from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


def _complete_fsync(_descriptor: int) -> None:
    """Model a successful kernel flush without paying physical disk latency."""


@pytest.fixture(autouse=True)
def successful_kernel_flush(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep unit tests at the fsync call boundary.

    Failure behavior remains covered by tests that replace this seam with a
    raising implementation; successful state-machine tests need only exercise
    that the durable-write path reaches the boundary.
    """
    monkeypatch.setattr(os, "fsync", _complete_fsync)


@contextmanager
def _uncontended_transition_lock(
    _store: ReviewExchangeStore,
) -> Generator[None]:
    """Model exclusive ownership for single-threaded state-machine tests."""
    yield


def _prepare_same_directory_file(target: Path, content: bytes) -> Path:
    """Prepare complete bytes beside their target without a kernel temp call."""
    target.parent.mkdir(parents=True, exist_ok=True)
    prepared = target.with_name(f".{target.name}.unit.tmp")
    prepared.write_bytes(content)
    return prepared


@pytest.fixture(autouse=True)
def fast_review_exchange_storage(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep higher-level exchange tests above the OS persistence boundary."""
    if "test_review_exchange_store" in request.path.parts:
        return
    monkeypatch.setattr(
        ReviewExchangeStore,
        "transition_lock",
        _uncontended_transition_lock,
    )
    monkeypatch.setattr(
        ReviewExchangeStore,
        "_prepare_atomic",
        staticmethod(_prepare_same_directory_file),
    )
