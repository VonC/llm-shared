"""Shared fast boundaries for tools unit tests.

Fix: the new_draft workflow suites stub `main_worktree_root`, so computing a
worktree path never runs a real `git rev-parse` against a temporary directory.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest

from tools import new_draft_workflow
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


def _unknown_main_worktree_root(_cwd: Path) -> None:
    """Model a root whose main checkout is not resolved through Git."""


@pytest.fixture(autouse=True)
def no_git_main_worktree_lookup(
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep new_draft workflow tests off the real Git main checkout lookup."""
    if not request.path.name.startswith("test_new_draft_workflow"):
        return
    monkeypatch.setattr(
        new_draft_workflow,
        "main_worktree_root",
        _unknown_main_worktree_root,
    )


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
