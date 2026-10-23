"""Real offline uv locks prove both supported empty release group shapes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import ENV
from tools.release_workflow.markers import evaluate, satisfies
from tools.release_workflow.readiness import validate

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("dev_edges", [False, True], ids=["no-dev-edges", "with-dev-edges"])
def test_uv_generated_empty_shapes(uv_empty_shape: Path) -> None:
    """Both real uv shapes pass readiness without querying dev-only packages."""
    installed: dict[str, str] = {}
    assert validate(uv_empty_shape, ENV, installed.__getitem__, evaluate, satisfies) == ()

# eof
