"""Provide declared repository inputs to the production commit-plan policy."""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.commit_plan_check.commit_plan_check_support import (
    build_repository_seed,
)
from tests.acceptance.commit_plan_check.repository_observations import (
    REVIEW_REPOSITORIES,
    read_index,
)
from tools import code_review_evidence, commit_plan_support

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def repository_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep production parsing and validation over declared external observations."""
    monkeypatch.setattr(commit_plan_support, "run_cross_platform_git_command", read_index)
    monkeypatch.setattr(code_review_evidence, "run_cross_platform_git_command", read_index)
    monkeypatch.setattr(subprocess, "run", REVIEW_REPOSITORIES.run)
    monkeypatch.setattr(shutil, "which", REVIEW_REPOSITORIES.which)


@pytest.fixture(scope="session")
def commit_plan_repository_seed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Seed small data files; each scenario owns its index observations."""
    root = tmp_path_factory.mktemp("commit-plan-seed")
    build_repository_seed(root)
    return root


# eof
