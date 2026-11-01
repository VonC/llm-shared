"""Reuse stable path observations in lifecycle scenarios with live records."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture(autouse=True)
def lifecycle_paths(stable_review_inputs: Callable[[], None]) -> None:
    """Keep every state transition live; these scenarios never alter symlinks."""
    del stable_review_inputs


# eof
