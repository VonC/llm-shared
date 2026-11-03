"""Exchange entry-point behavior and batch source wiring without shell execution."""

from __future__ import annotations

import json

from tests.acceptance.review_resume.cli_support import run_inline
from tests.acceptance.review_resume.conftest import (
    EXCHANGE_LAUNCHER,
    ReviewRepository,
    module_session_environment,
)


def test_cli_needs_no_activated_environment(repository: ReviewRepository) -> None:
    """The public Python entry locates its caller and returns one machine result."""
    environment = module_session_environment("codex")
    for inherited in ("PYTHONPATH", "VIRTUAL_ENV", "LLM_SHARED_DIR", "PRJ_DIR"):
        environment.pop(inherited, None)
    result = run_inline(("migration-check",), repository.root, environment)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert len(result.stdout.splitlines()) == 1
    payload = json.loads(result.stdout)
    assert payload["operation"] == "migration-check"
    assert payload["outcome"] == "ready"


def test_launcher_source_self_locates_and_forwards_arguments() -> None:
    """Keep batch wiring explicit without claiming OS launch behavior."""
    source = EXCHANGE_LAUNCHER.read_text(encoding="utf-8")
    assert 'if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."' in source
    assert 'set "PYTHON_BASE=%LLM_SHARED_DIR%\\venvs"' in source
    assert '"%PYTHON_EXE%" "%LLM_SHARED_DIR%\\tools\\review_exchange_cli.py" %*' in source


# eof
