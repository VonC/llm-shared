"""Check physical editor and selector refusals through the shipping terminal adapters."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.resume_paused.fakes import REQUESTOR_PANE, Scenario
from tests.acceptance.resume_paused.test_resume_paused_acceptance.test_resume_paused_public_terminal_tdd import (
    BORDER,
    CLAUDE,
    configure,
    run,
)
from tools.resume_paused_evidence import ScreenVerdict
from tools.resume_paused_profiles import CommandResult, Host
from tools.resume_paused_terminal import editor_state

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


@pytest.mark.parametrize(("row", "verdict"), [
    ("\u276f \x1b[38;2;2;22;0mTry tests", ScreenVerdict.DRAFT),
    ("\u276f \x1b[48;5;2mTry tests", ScreenVerdict.DRAFT),
    ("\u276f \x1b[2;38;2;0;22;0mTry tests", ScreenVerdict.IDLE_EMPTY),
    ("\u276f ", ScreenVerdict.DRAFT),
    ("\u276f  \x1b[2mTry tests", ScreenVerdict.DRAFT),
])
def test_only_dim_suggestion_text_proves_an_empty_editor(row: str, verdict: ScreenVerdict) -> None:
    """Color arguments do not alter intensity, and a typed leading space remains a draft."""
    assert editor_state(Host.CLAUDE, (BORDER, row, *CLAUDE[2:])) is verdict


@pytest.mark.parametrize("rows", [(BORDER, CLAUDE[1]), (BORDER, CLAUDE[1], BORDER[:-1]), (BORDER, "history", BORDER)])
def test_incomplete_editor_geometry_is_unsupported(rows: tuple[str, ...]) -> None:
    """The editor must be present and bounded by matching borders."""
    assert editor_state(Host.CLAUDE, rows) is ScreenVerdict.UNSUPPORTED


@pytest.mark.parametrize("fault", ["error", "invalid", "missing-token", "multiple"])
def test_unconfirmed_selection_leaves_the_pane_untouched(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str) -> None:
    """A final selector refusal prevents typing even after planning found an eligible UUID."""
    scenario = Scenario(tmp_path)
    scenario.single()
    configure(scenario, scenario.requestor, Host.CODEX)
    original = scenario.tuios.run

    def select(arguments: Sequence[str]) -> CommandResult:
        if "--select" not in arguments:
            return original(arguments)
        if fault == "error":
            return CommandResult(1, "")
        if fault == "invalid":
            return CommandResult(0, "{")
        if fault == "multiple":
            response = json.loads(original(("tuios", "list-agents", "--json")).stdout)
            return CommandResult(0, json.dumps(response | {"confirm": "both"}))
        response = json.loads(original(arguments).stdout)
        del response["confirm"]
        return CommandResult(0, json.dumps(response))

    monkeypatch.setattr(scenario.tuios, "run", select)
    code, report = run(scenario)
    assert code == 1, report
    assert "selector-confirmation-unavailable" in report
    assert scenario.requestor.record.pane_id == REQUESTOR_PANE
    assert not scenario.tuios.inputs()


# eof
