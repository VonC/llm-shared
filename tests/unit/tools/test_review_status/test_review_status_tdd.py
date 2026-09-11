"""Example coverage for bounded, read-only review-status discovery."""

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# ruff: noqa: ARG001, ARG005, C901, D103, EM102, PLR0913, PLR2004, TC003, TRY003

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import render_json_markdown
from tools.review_exchange_observer import ExchangeObservation
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_status import (
    _DEFAULT_DEPENDENCIES,
    _collect_review_status,
    _enumerate_candidates,
    _lease_for,
    _next_action_for,
    _observe,
    _outcome_for_state,
    _relative,
    _role_for,
    _StatusDependencies,
    collect_review_status,
)
from tools.review_status_models import (
    ArtifactKind,
    DamagedCandidateStatus,
    ExchangeStatus,
    LeaseFreshness,
    ReviewStatusOutcome,
    ReviewStatusResult,
    RoleSpecialization,
)


def _allow_git_ignore(_root: Path, _paths: Sequence[Path]) -> bool:
    """Stub successful ignored-path validation for migration fixtures."""
    return True


_NOW = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
_RENEWED = "2026-08-30T09:59:30+00:00"


class _StoreSpy:
    """Minimal observer store that makes mutation attempts fail loudly."""

    def __init__(self, paths: object) -> None:
        self.paths = paths

    def __getattr__(self, name: str) -> object:
        if name.startswith(
            (
                "append",
                "archive",
                "consume",
                "initialize",
                "publish",
                "remove",
                "transition_lock",
                "write",
            ),
        ):
            raise AssertionError(f"status attempted store mutation: {name}")
        raise AttributeError(name)


def _identity(slug: str = "topic") -> ExchangeIdentity:
    return ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", slug)


def _record(root: Path, slug: str = "topic") -> CoordinationRecord:
    identity = _identity(slug)
    document = root / "docs" / f"plan.v0.11.0.{slug}.md"
    umbrella = root / "docs" / "draft.v0.11.0.collection.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Plan\n", encoding="utf-8")
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    return CoordinationRecord(
        ReviewContext(identity, document, umbrella, "2"),
        FamilyPolicy("ready", "Again", "Commit"),
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        _RENEWED,
    )


def _encoded(record: CoordinationRecord) -> bytes:
    return render_json_markdown(
        "Review coordination",
        record.to_dict(),
        "",
    ).encode()


def _candidate(root: Path, identity: ExchangeIdentity) -> Path:
    configuration = ReviewArtifactConfiguration.load(root)
    configuration.prepare_home()
    return configuration.home / (
        "a.review-active."
        f"{identity.family.value}.{identity.type_token}.{identity.version}."
        f"{identity.slug}.md"
    )


def _dependencies(
    record: CoordinationRecord,
    candidate: Path,
    *,
    state: ArtifactState = ArtifactState.REQUEST_PENDING,
    second_bytes: bytes | None = None,
    counters: dict[str, int] | None = None,
    probe_paths: list[Path] | None = None,
) -> _StatusDependencies:
    first = _encoded(record)
    reads = 0
    project_root = record.context.document_path.parents[1]

    def load_artifacts(root: Path) -> ReviewArtifactConfiguration:
        assert root == project_root.resolve()
        if counters is not None:
            counters["artifact_config"] = counters.get("artifact_config", 0) + 1
        return ReviewArtifactConfiguration.load(root)

    def load(
        root: Path,
        artifacts: ReviewArtifactConfiguration,
    ) -> ReviewConfiguration:
        assert root == project_root.resolve()
        assert artifacts.project_root == root
        if counters is not None:
            counters["config"] = counters.get("config", 0) + 1
        return ReviewConfiguration(enabled=True, wait_timeout_seconds=90)

    def enumerate_candidates(
        artifacts: ReviewArtifactConfiguration,
    ) -> tuple[Path, ...]:
        assert artifacts.project_root == project_root.resolve()
        if counters is not None:
            counters["enumerate"] = counters.get("enumerate", 0) + 1
        return (candidate,)

    def read_bytes(path: Path) -> bytes:
        nonlocal reads
        assert path == candidate
        reads += 1
        if counters is not None:
            counters["coordination_reads"] = reads
        return second_bytes if reads == 2 and second_bytes is not None else first

    def exists(path: Path) -> bool:
        if probe_paths is not None:
            probe_paths.append(path)
        if counters is not None:
            counters["artifact_probes"] = counters.get("artifact_probes", 0) + 1
        return path in {candidate, derive_artifact_paths(project_root, record.context).transcript}

    def observe(*args: object) -> ExchangeObservation:
        if counters is not None:
            counters["observers"] = counters.get("observers", 0) + 1
        fixed_clock = cast("Callable[[], datetime]", args[-1])
        assert callable(fixed_clock)
        assert fixed_clock() == _NOW
        return ExchangeObservation(state, record, None, None, "observed")

    return replace(
        _DEFAULT_DEPENDENCIES,
        load_artifact_configuration=load_artifacts,
        load_configuration=load,
        enumerate_candidates=enumerate_candidates,
        read_bytes=read_bytes,
        path_exists=exists,
        make_store=_StoreSpy,
        observe=observe,
        occurrence=lambda *args: 2,
    )


def _collect(
    root: Path,
    dependencies: _StatusDependencies,
) -> ReviewStatusResult:
    return _collect_review_status(root, lambda: _NOW, dependencies)


def _assert_normalized_exchange(
    exchange: ExchangeStatus,
    record: CoordinationRecord,
) -> None:
    assert exchange.identity == record.context.identity
    assert exchange.umbrella == "docs/draft.v0.11.0.collection.md"
    assert exchange.occurrence == 2
    assert exchange.continuing_role is ReviewRole.REVIEWER
    assert exchange.specialization is RoleSpecialization.CODE_REVIEWER
    assert exchange.lease.timeout_seconds == 90


def _assert_bounded_io(
    counts: dict[str, int],
    probes: list[Path],
    expected_paths: tuple[Path, ...],
) -> None:
    assert counts == {
        "artifact_config": 1,
        "config": 1,
        "enumerate": 1,
        "coordination_reads": 2,
        "observers": 1,
        "artifact_probes": 6,
    }
    assert set(probes) == set(expected_paths)


def test_empty_repository_is_trustworthy_and_loads_configuration_once(
    tmp_path: Path,
) -> None:
    counts: dict[str, int] = {}
    dependencies = replace(
        _DEFAULT_DEPENDENCIES,
        load_configuration=lambda root, artifacts: (
            counts.__setitem__("config", counts.get("config", 0) + 1)
            or ReviewConfiguration(enabled=False, wait_timeout_seconds=41)
        ),
        enumerate_candidates=lambda artifacts: (
            counts.__setitem__("enumerate", counts.get("enumerate", 0) + 1) or ()
        ),
    )

    result = _collect(tmp_path, dependencies)

    assert result.outcome is ReviewStatusOutcome.TRUSTWORTHY
    assert result.exchanges == ()
    assert counts == {"config": 1, "enumerate": 1}


def test_default_candidate_enumerator_accepts_an_absent_home(tmp_path: Path) -> None:
    """An unused repository has no configured-home candidates and no error."""
    assert _enumerate_candidates(ReviewArtifactConfiguration.load(tmp_path)) == ()


def test_valid_candidate_is_normalized_with_bounded_read_only_io(tmp_path: Path) -> None:
    record = _record(tmp_path)
    candidate = _candidate(tmp_path, record.context.identity)
    counts: dict[str, int] = {}
    probes: list[Path] = []

    result = _collect(
        tmp_path,
        _dependencies(record, candidate, counters=counts, probe_paths=probes),
    )

    exchange = result.exchanges[0]
    assert isinstance(exchange, ExchangeStatus)
    assert result.outcome is ReviewStatusOutcome.TRUSTWORTHY
    _assert_normalized_exchange(exchange, record)
    _assert_bounded_io(
        counts,
        probes,
        derive_artifact_paths(tmp_path, record.context).fixed_paths,
    )


@pytest.mark.parametrize(
    ("first", "second", "diagnostic"),
    [
        (b"not markdown", None, "coordination"),
        (b"not markdown", b"changed", "coordination"),
    ],
)
def test_malformed_content_is_retained_as_damaged_candidate(
    tmp_path: Path,
    first: bytes,
    second: bytes | None,
    diagnostic: str,
) -> None:
    candidate = tmp_path / "a.review-active.code.code.v0.11.0.broken.md"
    reads = iter((first, second or first))
    dependencies = replace(
        _DEFAULT_DEPENDENCIES,
        enumerate_candidates=lambda artifacts: (candidate,),
        read_bytes=lambda path: next(reads),
    )

    result = _collect(tmp_path, dependencies)

    assert result.outcome is ReviewStatusOutcome.UNTRUSTWORTHY
    assert isinstance(result.exchanges[0], DamagedCandidateStatus)
    assert diagnostic in result.exchanges[0].diagnostic


def test_malformed_name_does_not_hide_a_healthy_exchange(tmp_path: Path) -> None:
    record = _record(tmp_path)
    healthy = _candidate(tmp_path, record.context.identity)
    malformed = tmp_path / "a.review-active.this-is-not-valid.md"
    dependencies = _dependencies(record, healthy)
    dependencies = replace(
        dependencies,
        enumerate_candidates=lambda artifacts: (malformed, healthy),
        read_bytes=lambda path: _encoded(record),
    )

    result = _collect(tmp_path, dependencies)

    assert result.outcome is ReviewStatusOutcome.UNTRUSTWORTHY
    assert len(result.exchanges) == 2
    assert any(isinstance(entry, DamagedCandidateStatus) for entry in result.exchanges)


def test_filename_record_mismatch_is_damaged(tmp_path: Path) -> None:
    record = _record(tmp_path)
    candidate = _candidate(tmp_path, _identity("different"))

    result = _collect(tmp_path, _dependencies(record, candidate))

    damaged = result.exchanges[0]
    assert isinstance(damaged, DamagedCandidateStatus)
    assert "filename identity" in damaged.diagnostic


def test_missing_umbrella_and_noncanonical_coordination_are_damaged(tmp_path: Path) -> None:
    record = _record(tmp_path)
    assert record.context.umbrella_path is not None
    record.context.umbrella_path.unlink()
    candidate = _candidate(tmp_path, record.context.identity)

    missing = _collect(tmp_path, _dependencies(record, candidate))

    assert "umbrella" in missing.exchanges[0].diagnostic


def test_changed_during_read_never_reports_trustworthy(tmp_path: Path) -> None:
    record = _record(tmp_path)
    candidate = _candidate(tmp_path, record.context.identity)

    result = _collect(
        tmp_path,
        _dependencies(record, candidate, second_bytes=_encoded(record) + b"\n"),
    )

    damaged = result.exchanges[0]
    assert isinstance(damaged, DamagedCandidateStatus)
    assert damaged.diagnostic == "changed-during-read"


def test_idle_candidate_is_excluded(tmp_path: Path) -> None:
    record = _record(tmp_path)
    candidate = _candidate(tmp_path, record.context.identity)

    result = _collect(
        tmp_path,
        _dependencies(record, candidate, state=ArtifactState.IDLE),
    )

    assert result.exchanges == ()
    assert result.outcome is ReviewStatusOutcome.TRUSTWORTHY


def test_public_entry_point_uses_disabled_fallback_and_marker_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tools.review_artifact_migration._git_ignore_checker",
        _allow_git_ignore,
    )
    record = _record(tmp_path)
    candidate = _candidate(tmp_path, record.context.identity)
    candidate.write_bytes(_encoded(record))

    disabled = collect_review_status(tmp_path, lambda: _NOW)

    exchange = disabled.exchanges[0]
    assert isinstance(exchange, ExchangeStatus)
    assert exchange.lease.timeout_seconds == 10800
    (tmp_path / "a.review-mode").write_text(
        "wait_timeout_seconds=73\n",
        encoding="utf-8",
    )

    enabled = collect_review_status(tmp_path, lambda: _NOW)

    exchange = enabled.exchanges[0]
    assert isinstance(exchange, ExchangeStatus)
    assert exchange.lease.timeout_seconds == 73


def test_public_entry_point_blocks_when_repository_root_is_missing(tmp_path: Path) -> None:
    """Root-resolution failures return typed operational status instead of raising."""
    missing = tmp_path / "missing"

    result = collect_review_status(missing, lambda: _NOW)

    assert result.outcome is ReviewStatusOutcome.OPERATIONAL_FAILURE
    assert result.migration.state.value == "blocked"
    assert result.migration.diagnostics


def test_serialized_missing_umbrella_field_is_damaged(tmp_path: Path) -> None:
    record = _record(tmp_path)
    candidate = _candidate(tmp_path, record.context.identity)
    payload = record.to_dict()
    context = cast("dict[str, object]", payload["context"])
    del context["umbrella_path"]
    encoded = render_json_markdown("Review coordination", payload, "Active.\n").encode()
    dependencies = replace(
        _dependencies(record, candidate),
        read_bytes=lambda path: encoded,
    )

    result = _collect(tmp_path, dependencies)

    damaged = result.exchanges[0]
    assert isinstance(damaged, DamagedCandidateStatus)
    assert "missing context fields: umbrella_path" in damaged.diagnostic


def test_derived_canonical_path_mismatch_is_damaged(tmp_path: Path) -> None:
    record = _record(tmp_path)
    candidate = _candidate(tmp_path, record.context.identity)

    def mismatched(
        artifacts: ReviewArtifactConfiguration,
        context: ReviewContext,
    ) -> object:
        root = artifacts.project_root
        return replace(derive_artifact_paths(root, context), coordination=root / "other.md")

    dependencies = replace(
        _dependencies(record, candidate),
        derive_paths=mismatched,
    )

    result = _collect(tmp_path, dependencies)

    damaged = result.exchanges[0]
    assert isinstance(damaged, DamagedCandidateStatus)
    assert "not its canonical path" in damaged.diagnostic


def test_multiple_valid_candidates_are_sorted_by_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tools.review_artifact_migration._git_ignore_checker",
        _allow_git_ignore,
    )
    records = (_record(tmp_path, "zulu"), _record(tmp_path, "alpha"))
    for record in records:
        _candidate(tmp_path, record.context.identity).write_bytes(_encoded(record))

    result = collect_review_status(tmp_path, lambda: _NOW)

    assert all(isinstance(entry, ExchangeStatus) for entry in result.exchanges)
    assert [
        entry.identity.slug
        for entry in result.exchanges
        if isinstance(entry, ExchangeStatus)
    ] == ["alpha", "zulu"]


@pytest.mark.parametrize("relative_home", [".reviews", "runtime/reviews"])
def test_status_reuses_one_artifact_configuration_for_multiple_candidates(
    tmp_path: Path,
    relative_home: str,
) -> None:
    """One status invocation reads and validates either home layout exactly once."""
    if relative_home != ".reviews":
        (tmp_path / ".review-artifacts.ini").write_text(
            f"[review-artifacts]\nhome={relative_home}\n",
            encoding="utf-8",
        )
    records = (_record(tmp_path, "zulu"), _record(tmp_path, "alpha"))
    for record in records:
        _candidate(tmp_path, record.context.identity).write_bytes(_encoded(record))
    counts = {"configuration": 0, "tracking": 0}

    def tracked_directory(root: Path, relative: str) -> bool:
        assert root == tmp_path.resolve()
        assert relative == relative_home
        counts["tracking"] += 1
        return False

    def load_artifacts(root: Path) -> ReviewArtifactConfiguration:
        counts["configuration"] += 1
        return ReviewArtifactConfiguration.load(
            root,
            tracked_directory=tracked_directory,
        )

    dependencies = replace(
        _DEFAULT_DEPENDENCIES,
        load_artifact_configuration=load_artifacts,
    )

    result = _collect(tmp_path, dependencies)

    assert all(isinstance(entry, ExchangeStatus) for entry in result.exchanges)
    assert counts == {"configuration": 1, "tracking": 1}


def test_operational_failure_does_not_claim_partial_evidence(tmp_path: Path) -> None:
    dependencies = replace(
        _DEFAULT_DEPENDENCIES,
        load_artifact_configuration=lambda root: (_ for _ in ()).throw(
            OSError("unreadable"),
        ),
    )

    result = _collect(tmp_path, dependencies)

    assert result.outcome is ReviewStatusOutcome.OPERATIONAL_FAILURE
    assert result.exchanges == ()
    assert result.process_status == 2


def test_default_observer_adapter_delegates_to_existing_classifier(tmp_path: Path) -> None:
    record = _record(tmp_path)
    paths = derive_artifact_paths(tmp_path, record.context)

    observation = _observe(
        ReviewExchangeStore(paths),
        record.context,
        record.policy,
        ReviewConfiguration(enabled=False, wait_timeout_seconds=60),
        lambda: _NOW,
    )

    assert observation.state is ArtifactState.IDLE


def test_projection_fail_closed_branches_are_explicit(tmp_path: Path) -> None:
    presence = dict.fromkeys(ArtifactKind, False)

    assert (
        _lease_for(ArtifactState.REQUEST_PENDING, None, 60, _NOW).freshness
        is LeaseFreshness.MISSING
    )
    with pytest.raises(ReviewExchangeError, match="no continuing agent role"):
        _role_for(ArtifactState.ROUND_IN_PROGRESS, Actor.REVIEWER, Actor.HUMAN, presence)
    with pytest.raises(ReviewExchangeError, match="artifact shape"):
        _role_for(ArtifactState.ESCALATED, Actor.REVIEWER, Actor.HUMAN, presence)
    presence[ArtifactKind.REQUEST] = True
    presence[ArtifactKind.ANSWER] = True
    with pytest.raises(ReviewExchangeError, match="artifact shape"):
        _role_for(ArtifactState.ESCALATED, Actor.REVIEWER, Actor.HUMAN, presence)
    with pytest.raises(ReviewExchangeError, match="no active next action"):
        _next_action_for(ArtifactState.IDLE)
    with pytest.raises(ReviewExchangeError, match="idle state"):
        _outcome_for_state(ArtifactState.IDLE)
    with pytest.raises(ReviewExchangeError, match="outside repository"):
        _relative(tmp_path, tmp_path.parent / "outside.md")
