"""Tests for strict role snapshots and selected-role reconciliation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import review_role_nature
from tools.llm_nature import LlmNature
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_role_nature import (
    MutableRoleNatureArtifact,
    RoleNatureBackfill,
    RoleNatureBackfillContext,
    RoleNatureEvidence,
    RoleNatureReconciler,
    RoleNatureSnapshot,
)

_SECOND_REPLACE_CALL = 2


def test_backfill_temporary_prefix_is_covered_by_repository_ignore_rule() -> None:
    """Hard-killed replacement files retain the repository's ignored prefix."""
    assert review_role_nature._BACKFILL_TEMP_PREFIX.startswith(".tmp")


def _mutable_artifact(
    path: Path,
    role: ReviewRole,
    nature: LlmNature | None,
    snapshot: RoleNatureSnapshot,
) -> MutableRoleNatureArtifact:
    """Build one JSON artifact whose render and validation seams are observable."""
    path.write_text(json.dumps({"role_natures": snapshot.to_dict()}), encoding="utf-8")

    def render(updated: RoleNatureSnapshot) -> str:
        return json.dumps({"role_natures": updated.to_dict()}, sort_keys=True)

    def validate(content: str) -> None:
        parsed = json.loads(content)
        RoleNatureSnapshot.from_optional_dict(parsed["role_natures"])

    return MutableRoleNatureArtifact(
        RoleNatureEvidence(path, role, nature),
        snapshot,
        render,
        validate,
    )


def test_snapshot_parses_legacy_absence_nulls_and_supported_values() -> None:
    """Legacy absence and nulls stay missing while known enum values round-trip."""
    assert RoleNatureSnapshot.from_optional_dict(None) == RoleNatureSnapshot()
    snapshot = RoleNatureSnapshot.from_optional_dict(
        {"requestor": "codex", "reviewer": None},
    )

    assert snapshot.requestor is LlmNature.CODEX
    assert snapshot.reviewer is None
    assert snapshot.to_dict() == {"requestor": "codex", "reviewer": None}


@pytest.mark.parametrize("nature", list(LlmNature))
def test_snapshot_round_trips_every_supported_nature(nature: LlmNature) -> None:
    """The strict schema accepts every closed enum member, including unknown."""
    snapshot = RoleNatureSnapshot.from_optional_dict(
        {"requestor": nature.value, "reviewer": nature.value},
    )

    assert snapshot == RoleNatureSnapshot(requestor=nature, reviewer=nature)
    assert snapshot.to_dict() == {
        "requestor": nature.value,
        "reviewer": nature.value,
    }


def test_snapshot_rejects_unknown_fields_and_values() -> None:
    """Identity schemas fail closed on field drift and unsupported values."""
    with pytest.raises(ReviewExchangeError, match="role-nature snapshot"):
        RoleNatureSnapshot.from_optional_dict({"requestor": "other", "reviewer": None})
    with pytest.raises(ReviewExchangeError, match="role-nature snapshot"):
        RoleNatureSnapshot.from_optional_dict(
            {"requestor": None, "reviewer": None, "extra": None},
        )
    with pytest.raises(ReviewExchangeError, match="role-nature snapshot"):
        RoleNatureSnapshot.from_optional_dict({"requestor": 1, "reviewer": None})


def test_snapshot_rejects_human_role_lookup() -> None:
    """Only the two LLM protocol roles can own nature evidence."""
    with pytest.raises(ReviewExchangeError, match="human role"):
        RoleNatureSnapshot().for_role(ReviewRole.HUMAN)


def test_recording_one_role_preserves_the_counterpart_and_known_identity() -> None:
    """Missing and unknown values can improve without replacing known evidence."""
    snapshot = RoleNatureSnapshot(requestor=LlmNature.CODEX)

    assert snapshot.record(ReviewRole.REVIEWER, LlmNature.CLAUDE) == RoleNatureSnapshot(
        requestor=LlmNature.CODEX,
        reviewer=LlmNature.CLAUDE,
    )
    with pytest.raises(ReviewExchangeError, match="cannot replace known"):
        snapshot.record(ReviewRole.REQUESTOR, LlmNature.CLAUDE)


def test_snapshot_merge_records_present_values_and_skips_missing_values() -> None:
    """Merge improves either role while a missing counterpart remains unchanged."""
    merged = RoleNatureSnapshot(requestor=LlmNature.CODEX).merge(
        RoleNatureSnapshot(reviewer=LlmNature.CLAUDE),
    )

    assert merged == RoleNatureSnapshot(
        requestor=LlmNature.CODEX,
        reviewer=LlmNature.CLAUDE,
    )


def test_reconciliation_scans_only_the_selected_role_and_collects_all_conflicts() -> None:
    """Counterpart gaps are ignored and every selected-role conflict is retained."""
    evidence = [
        RoleNatureEvidence(Path("missing.json"), ReviewRole.REQUESTOR, None),
        RoleNatureEvidence(Path("matching.json"), ReviewRole.REQUESTOR, LlmNature.CODEX),
        RoleNatureEvidence(Path("conflict-a.json"), ReviewRole.REQUESTOR, LlmNature.CLAUDE),
        RoleNatureEvidence(Path("counterpart.json"), ReviewRole.REVIEWER, None),
        RoleNatureEvidence(Path("conflict-b.json"), ReviewRole.REQUESTOR, LlmNature.GEMINI),
    ]

    result = RoleNatureReconciler().reconcile(
        evidence,
        ReviewRole.REQUESTOR,
        LlmNature.CODEX,
    )

    assert [item.path.name for item in result.missing] == ["missing.json"]
    assert [item.path.name for item in result.matching] == ["matching.json"]
    assert [item.path.name for item in result.conflicts] == [
        "conflict-a.json",
        "conflict-b.json",
    ]


def test_unknown_current_nature_never_backfills_or_conflicts() -> None:
    """A weak current identity preserves missing and known evidence as-is."""
    result = RoleNatureReconciler().reconcile(
        [
            RoleNatureEvidence(Path("missing.json"), ReviewRole.REQUESTOR, None),
            RoleNatureEvidence(Path("known.json"), ReviewRole.REQUESTOR, LlmNature.CLAUDE),
        ],
        ReviewRole.REQUESTOR,
        LlmNature.UNKNOWN,
    )

    assert result.backfill_allowed is False
    assert result.conflicts == ()


def test_backfill_changes_only_missing_selected_role_and_is_repeat_safe(
    tmp_path: Path,
) -> None:
    """Known evidence and counterpart gaps stay untouched; completion is unique."""
    missing_path = tmp_path / "request.json"
    known_path = tmp_path / "answer.json"
    counterpart_path = tmp_path / "coordination.json"
    transcript = tmp_path / "transcript.md"
    transcript.write_text("# Transcript\n", encoding="utf-8")
    missing = _mutable_artifact(
        missing_path,
        ReviewRole.REQUESTOR,
        None,
        RoleNatureSnapshot(),
    )
    known = _mutable_artifact(
        known_path,
        ReviewRole.REQUESTOR,
        LlmNature.CODEX,
        RoleNatureSnapshot(requestor=LlmNature.CODEX),
    )
    counterpart = _mutable_artifact(
        counterpart_path,
        ReviewRole.REVIEWER,
        None,
        RoleNatureSnapshot(),
    )
    known_before = known_path.read_bytes()
    counterpart_before = counterpart_path.read_bytes()
    context = RoleNatureBackfillContext(
        ReviewRole.REQUESTOR,
        LlmNature.CODEX,
        transcript,
        2,
    )

    first = RoleNatureBackfill().apply([missing, known, counterpart], context)
    completed_snapshot = RoleNatureSnapshot.from_optional_dict(
        json.loads(missing_path.read_text(encoding="utf-8"))["role_natures"],
    )
    rescanned = _mutable_artifact(
        missing_path,
        ReviewRole.REQUESTOR,
        LlmNature.CODEX,
        completed_snapshot,
    )
    transcript_after_first = transcript.read_bytes()
    second = RoleNatureBackfill().apply([rescanned, known, counterpart], context)

    assert completed_snapshot.requestor is LlmNature.CODEX
    assert completed_snapshot.reviewer is None
    assert known_path.read_bytes() == known_before
    assert counterpart_path.read_bytes() == counterpart_before
    assert first.changed_paths == (missing_path.resolve(), transcript.resolve())
    assert second.changed_paths == ()
    assert transcript.read_bytes() == transcript_after_first
    assert transcript_after_first.count(
        b"### LLM nature completion for requestor (exchange 2)",
    ) == 1


def test_conflicts_stop_before_mutation_and_override_fills_only_missing(
    tmp_path: Path,
) -> None:
    """Override authorizes missing-only completion without replacing conflicts."""
    missing_path = tmp_path / "request.json"
    conflict_path = tmp_path / "coordination.json"
    transcript = tmp_path / "transcript.md"
    transcript.write_text("# Transcript\n", encoding="utf-8")
    missing = _mutable_artifact(
        missing_path,
        ReviewRole.REQUESTOR,
        None,
        RoleNatureSnapshot(),
    )
    conflict = _mutable_artifact(
        conflict_path,
        ReviewRole.REQUESTOR,
        LlmNature.CLAUDE,
        RoleNatureSnapshot(requestor=LlmNature.CLAUDE),
    )
    originals = {path: path.read_bytes() for path in (missing_path, conflict_path, transcript)}
    context = RoleNatureBackfillContext(
        ReviewRole.REQUESTOR,
        LlmNature.CODEX,
        transcript,
        1,
    )

    with pytest.raises(ReviewExchangeError, match="conflicts require Override"):
        RoleNatureBackfill().apply([missing, conflict], context)
    assert all(path.read_bytes() == content for path, content in originals.items())

    result = RoleNatureBackfill().apply(
        [missing, conflict],
        RoleNatureBackfillContext(
            ReviewRole.REQUESTOR,
            LlmNature.CODEX,
            transcript,
            1,
            override=True,
        ),
    )

    assert result.reconciliation.conflicts == (conflict.evidence,)
    assert conflict_path.read_bytes() == originals[conflict_path]
    assert b'"requestor": "codex"' in missing_path.read_bytes()


def test_unknown_backfill_is_a_no_op(tmp_path: Path) -> None:
    """Unknown host evidence cannot create nature metadata or transcript entries."""
    artifact_path = tmp_path / "request.json"
    transcript = tmp_path / "transcript.md"
    transcript.write_text("# Transcript\n", encoding="utf-8")
    artifact = _mutable_artifact(
        artifact_path,
        ReviewRole.REQUESTOR,
        None,
        RoleNatureSnapshot(),
    )
    originals = (artifact_path.read_bytes(), transcript.read_bytes())

    result = RoleNatureBackfill().apply(
        [artifact],
        RoleNatureBackfillContext(
            ReviewRole.REQUESTOR,
            LlmNature.UNKNOWN,
            transcript,
            1,
        ),
    )

    assert result.changed_paths == ()
    assert (artifact_path.read_bytes(), transcript.read_bytes()) == originals


def test_commit_failure_rolls_back_every_exposed_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A later replace failure restores files already exposed by the transaction."""
    first_path = tmp_path / "request.json"
    second_path = tmp_path / "coordination.json"
    transcript = tmp_path / "transcript.md"
    transcript.write_text("# Transcript\n", encoding="utf-8")
    artifacts = [
        _mutable_artifact(
            path,
            ReviewRole.REQUESTOR,
            None,
            RoleNatureSnapshot(),
        )
        for path in (first_path, second_path)
    ]
    originals = {path: path.read_bytes() for path in (first_path, second_path, transcript)}
    real_replace = Path.replace
    calls = 0

    def fail_second_replace(source: Path, target: Path) -> Path:
        nonlocal calls
        calls += 1
        if calls == _SECOND_REPLACE_CALL:
            message = "simulated replace failure"
            raise OSError(message)
        return real_replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_second_replace)

    with pytest.raises(ReviewExchangeError, match="atomic role-nature backfill failed"):
        RoleNatureBackfill().apply(
            artifacts,
            RoleNatureBackfillContext(
                ReviewRole.REQUESTOR,
                LlmNature.CODEX,
                transcript,
                1,
            ),
        )

    assert all(path.read_bytes() == content for path, content in originals.items())
