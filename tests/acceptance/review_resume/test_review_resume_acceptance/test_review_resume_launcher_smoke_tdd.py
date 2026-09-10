"""The shipped exchange launcher resolves itself without an activated project.

The other resume scenarios drive ``python -m tools.review_exchange_cli``, a
real isolated child over the same CLI, because spawning ``cmd.exe`` in front of
every call doubled process creation on the hottest path of the suite. The batch
launcher still carries logic of its own: it self-locates ``LLM_SHARED_DIR``
from its own ``bin`` folder and picks the newest matching virtual-environment
Python without ``senv.bat`` having run. This module keeps that shim under
acceptance coverage, the way ``commit_plan_check`` guards its own launcher by
running both adapters over one service.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

import pytest

from tests.acceptance.review_resume.conftest import (
    EXCHANGE_LAUNCHER,
    ReviewRepository,
    module_session_environment,
)

pytestmark = pytest.mark.xdist_group("resume-launcher-smoke")


@pytest.fixture
def launcher_run(repository: ReviewRepository) -> dict[str, Any]:
    """Run the shipped launcher with no shared variables and no project environment."""
    environment = module_session_environment("codex")
    for inherited in ("PYTHONPATH", "VIRTUAL_ENV", "LLM_SHARED_DIR", "PRJ_DIR"):
        environment.pop(inherited, None)
    result = subprocess.run(  # noqa: S603
        [str(EXCHANGE_LAUNCHER), "migration-check"],
        cwd=repository.root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {"result": result, "environment": environment}


def test_launcher_self_locates_its_python_and_returns_one_result(launcher_run: dict[str, Any]) -> None:
    """The batch shim finds its own venv Python and answers with one machine result."""
    result: subprocess.CompletedProcess[str] = launcher_run["result"]
    environment: dict[str, str] = launcher_run["environment"]

    # Self-location is only proved when nothing in the child named the paths.
    assert "LLM_SHARED_DIR" not in environment
    assert "PYTHONPATH" not in environment
    assert "VIRTUAL_ENV" not in environment

    assert result.returncode == 0, (result.returncode, result.stdout, result.stderr)
    assert "No python_3" not in result.stderr
    lines = result.stdout.splitlines()
    assert len(lines) == 1, result.stdout
    payload = json.loads(lines[0])
    assert payload["operation"] == "migration-check"
    assert payload["outcome"] == "ready"


# eof
