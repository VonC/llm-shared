"""Tests for clean-tree completion after an authorized code-review commit.

The cases keep durable authority alive while residual work is grouped, prove
the reviewed plan runs first, and reject completion when cleanup leaves paths.
"""

from __future__ import annotations

import logging
import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_prompt_workflow_code_review.test_prompt_workflow_code_review_tdd import (
    _context,
    _coordination,
    _effort,
)
from tools import prompt_workflow_code_review as code_review
from tools.review_exchange_models import (
    ArtifactState,
    CoordinationStatus,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

# Test doubles intentionally replace functions with smaller signatures.
# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState
    from tools.review_exchange_models import ReviewContext


def _authorized(
    root: Path,
) -> tuple[
    Topic,
    WorkflowState,
    MemoryRecord,
    ReviewContext,
    ReviewExchangeStore,
]:
    """Create one authorized exact route and return its workflow inputs."""
    topic, state, record = _effort(root)
    context = _context(root)
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    store.write_coordination(
        _coordination(context, CoordinationStatus.AWAITING_HUMAN_CONFIRMATION),
    )
    return topic, state, record, context, store


def test_primary_batch_stages_every_residual_path_and_keeps_authority(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A successful reviewed plan hands all remaining changes to grouping."""
    topic, state, record, context, store = _authorized(tmp_path)
    batches: list[tuple[str, ...]] = []
    staged: list[Path] = []
    monkeypatch.setattr(
        code_review,
        "run_batch_commit",
        lambda args, **_kwargs: (
            batches.append(args) or subprocess.CompletedProcess(args, 0)
        ),
    )
    monkeypatch.setattr(
        code_review.git,
        "status_entries",
        lambda _root: [(" M", "review.md"), ("??", "new.txt")],
    )
    monkeypatch.setattr(code_review.git, "stage_all", staged.append)

    caplog.set_level(logging.INFO)
    result = code_review.continue_authorized_commit(tmp_path, topic, state, record)

    assert result == code_review.RESIDUAL_GROUPING_REQUIRED
    assert batches == [("--root-a-commit", "--non-interactive")]
    assert staged == [tmp_path.resolve()]
    assert code_review._read_phase(tmp_path, context) == "residual"
    assert store.read_coordination(required=True) is not None
    assert capsys.readouterr().out == ""
    output = caplog.text
    assert "$llm-shared:group-commits-msg" in output
    assert "pw code-review-commit --residual" in output


def test_pending_residual_reentry_restages_without_replaying_primary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A resumed first-phase call preserves the residual grouping boundary."""
    topic, state, record, context, _store = _authorized(tmp_path)
    code_review._write_phase(tmp_path, context, "residual")
    staged: list[Path] = []
    monkeypatch.setattr(code_review.git, "stage_all", staged.append)
    monkeypatch.setattr(
        code_review,
        "run_batch_commit",
        lambda *_args, **_kwargs: pytest.fail("primary batch was replayed"),
    )

    result = code_review.continue_authorized_commit(tmp_path, topic, state, record)

    assert result == code_review.RESIDUAL_GROUPING_REQUIRED
    assert staged == [tmp_path.resolve()]


def test_residual_batch_completes_only_with_a_clean_tree(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The replacement plan consumes authority only after the final clean check."""
    topic, state, record, context, store = _authorized(tmp_path)
    code_review._write_phase(tmp_path, context, "residual")
    monkeypatch.setattr(
        code_review,
        "run_batch_commit",
        lambda args, **_kwargs: subprocess.CompletedProcess(args, 0),
    )
    monkeypatch.setattr(code_review.git, "status_entries", lambda _root: [])

    result = code_review.continue_authorized_commit(
        tmp_path,
        topic,
        state,
        record,
        residual=True,
    )

    assert result == 0
    assert not code_review._phase_marker(tmp_path).exists()
    assert not store.paths.coordination.exists()


def test_residual_batch_rejects_dirty_completion_and_retains_authority(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A remaining path prevents both marker removal and exchange completion."""
    topic, state, record, context, store = _authorized(tmp_path)
    code_review._write_phase(tmp_path, context, "residual")
    monkeypatch.setattr(
        code_review,
        "run_batch_commit",
        lambda args, **_kwargs: subprocess.CompletedProcess(args, 0),
    )
    monkeypatch.setattr(
        code_review.git,
        "status_entries",
        lambda _root: [("??", "left-behind.txt")],
    )

    with pytest.raises(code_review.CodeReviewRoutingError, match="dirty working tree"):
        code_review.continue_authorized_commit(
            tmp_path,
            topic,
            state,
            record,
            residual=True,
        )

    assert code_review._phase_marker(tmp_path).exists()
    route = code_review.resolve_code_review_route(tmp_path, topic, state, record)
    assert route is not None
    assert route.state is ArtifactState.OWNING_ACTION_PENDING
    assert store.read_coordination(required=True) is not None


def test_residual_flag_requires_a_durable_pending_phase(tmp_path: Path) -> None:
    """The cleanup entry cannot bypass the reviewed primary commit plan."""
    topic, state, record, _context_value, _store = _authorized(tmp_path)

    with pytest.raises(code_review.CodeReviewRoutingError, match="no staged residual"):
        code_review.continue_authorized_commit(
            tmp_path,
            topic,
            state,
            record,
            residual=True,
        )


def test_stale_phase_marker_rejects_another_review_identity(tmp_path: Path) -> None:
    """A marker that cannot prove the exact phase and identity fails closed."""
    topic, state, record, _context_value, _store = _authorized(tmp_path)
    code_review._phase_marker(tmp_path).write_text("stale\n", encoding="utf-8")

    with pytest.raises(code_review.CodeReviewRoutingError, match="marker is stale"):
        code_review.continue_authorized_commit(tmp_path, topic, state, record)


def test_failed_residual_batch_keeps_phase_and_authority(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A failed cleanup batch remains replayable without completing exchange."""
    topic, state, record, context, store = _authorized(tmp_path)
    code_review._write_phase(tmp_path, context, "residual")
    failed_exit = 9
    monkeypatch.setattr(
        code_review,
        "run_batch_commit",
        lambda args, **_kwargs: subprocess.CompletedProcess(args, failed_exit),
    )

    result = code_review.continue_authorized_commit(
        tmp_path,
        topic,
        state,
        record,
        residual=True,
    )

    assert result == failed_exit
    assert code_review._read_phase(tmp_path, context) == "residual"
    assert store.read_coordination(required=True) is not None
