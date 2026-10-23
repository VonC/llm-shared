"""Build the real Git baseline once per worker and copy it per scenario.

The seed's setup stays inside pytest's measured fixture phases. Scenario Git
operations, public adapters and immutability snapshots continue using real Git.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.acceptance.commit_plan_check.commit_plan_check_support import (
    build_repository_seed,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="session")
def commit_plan_repository_seed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Seed one repository whose copies have separate files and Git indexes."""
    root = tmp_path_factory.mktemp("commit-plan-seed")
    build_repository_seed(root)
    return root


# eof
