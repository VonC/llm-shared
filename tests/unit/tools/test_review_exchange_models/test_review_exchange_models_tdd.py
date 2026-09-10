"""TDD coverage for the v0.11.0 review-exchange protocol models.

Step 1: specify strict immutable identities, contexts, policies, envelopes,
coordination records, marker configuration, timestamps, and summary checks.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

import pytest

from tools import review_exchange_models as models
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    _FALLBACK_WAIT_SECONDS,
    _PACKAGE_ROOT,
    _SETTINGS_NAME,
    Actor,
    ArtifactState,
    ConfirmationOutcome,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    _wait_setting_of,
    format_local_timestamp,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    Envelope,
    parse_envelope_markdown,
    render_envelope_markdown,
    validate_summary_identity,
)
from tools.review_exchange_paths import load_review_configuration

if TYPE_CHECKING:
    from pathlib import Path

_VERSION = "v0.11.0"
_SLUG = "review-exchange_core"
_TIMESTAMP = "2026-08-03T14:30:05+02:00"
_PROJECT_WAIT = 600
_MARKER_WAIT = 90
_SHIPPED_WAIT = 7200


def _identity(*, code: bool = False) -> ExchangeIdentity:
    """Return a valid identity for the requested family."""
    family = ReviewFamily.CODE if code else ReviewFamily.SPECIFICATION
    token = "code" if code else "feature-request"
    return ExchangeIdentity(family, token, _VERSION, _SLUG)


def _context(tmp_path: Path, *, code: bool = False) -> ReviewContext:
    """Create a context with real reviewed-document and umbrella files."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    prefix = "plan" if code else "feature-request"
    document = tmp_path / f"{prefix}.{_VERSION}.{_SLUG}.md"
    umbrella = tmp_path / "draft.v0.11.0.review-mode.md"
    document.write_text("# Reviewed document\n", encoding="utf-8")
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    return ReviewContext(
        _identity(code=code),
        document,
        umbrella,
        "1" if code else None,
    )


@pytest.mark.parametrize(
    ("family", "type_token"),
    [
        (ReviewFamily.SPECIFICATION, "feature-request"),
        (ReviewFamily.SPECIFICATION, "issue"),
        (ReviewFamily.SPECIFICATION, "design-specification"),
        (ReviewFamily.SPECIFICATION, "plan"),
        (ReviewFamily.CODE, "code"),
    ],
)
def test_exchange_identity_accepts_supported_immutable_tuples(
    family: ReviewFamily,
    type_token: str,
) -> None:
    """Each supported family and type pair forms one frozen key."""
    identity = ExchangeIdentity(family, type_token, _VERSION, _SLUG)

    assert identity.key == f"{family.value}/{type_token}/{_VERSION}/{_SLUG}"
    assert ExchangeIdentity.from_dict(identity.to_dict()) == identity
    with pytest.raises(FrozenInstanceError):
        setattr(identity, "slug", "changed")


@pytest.mark.parametrize(
    ("family", "token", "version", "slug", "message"),
    [
        (ReviewFamily.CODE, "plan", _VERSION, _SLUG, "code family requires"),
        (ReviewFamily.SPECIFICATION, "code", _VERSION, _SLUG, "unsupported"),
        (ReviewFamily.SPECIFICATION, "plan", "0.11.0", _SLUG, "invalid version"),
        (ReviewFamily.SPECIFICATION, "plan", _VERSION, "Bad Slug", "invalid slug"),
    ],
)
def test_exchange_identity_rejects_invalid_values(
    family: ReviewFamily,
    token: str,
    version: str,
    slug: str,
    message: str,
) -> None:
    """Incomplete or ambiguous identity input fails with a stable diagnostic."""
    with pytest.raises(ReviewExchangeError, match=message):
        ExchangeIdentity(family, token, version, slug)


def test_context_resolves_paths_and_round_trips(tmp_path: Path) -> None:
    """Exact document, umbrella, and code-step context survive serialization."""
    context = _context(tmp_path, code=True)

    assert context.document_path == context.document_path.resolve()
    assert context.umbrella_path is not None
    assert context.umbrella_path == context.umbrella_path.resolve()
    assert ReviewContext.from_dict(context.to_dict()) == context


def test_context_rejects_missing_mismatched_or_family_specific_data(
    tmp_path: Path,
) -> None:
    """Context paths and the implementation step must match their identity."""
    missing = tmp_path / f"feature-request.{_VERSION}.{_SLUG}.md"
    with pytest.raises(ReviewExchangeError, match="reviewed document does not exist"):
        ReviewContext(_identity(), missing, None, None)

    missing.write_text("# Feature\n", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match="only valid for code review"):
        ReviewContext(_identity(), missing, None, "1")
    with pytest.raises(ReviewExchangeError, match="implementation step"):
        ReviewContext(_identity(code=True), missing, None, None)
    with pytest.raises(ReviewExchangeError, match="does not match exchange identity"):
        ReviewContext(_identity(code=True), missing, None, "1")
    with pytest.raises(ReviewExchangeError, match="umbrella draft does not exist"):
        ReviewContext(_identity(), missing, tmp_path / "missing.md", None)


def test_family_policy_maps_two_distinct_labels() -> None:
    """A persisted policy maps family labels to role-neutral outcomes."""
    policy = FamilyPolicy(
        "convergence-recommended",
        "Revise and review again",
        "Consolidate",
    )

    assert policy.label_for(ConfirmationOutcome.ANOTHER_ROUND) == "Revise and review again"
    assert policy.outcome_for("Consolidate") is ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
    assert FamilyPolicy.from_dict(policy.to_dict()) == policy


@pytest.mark.parametrize(
    ("signal", "again", "continuing", "message"),
    [
        ("", "Again", "Continue", "convergence signal"),
        ("Converged", "Again", "Continue", "convergence signal"),
        ("converged", "Same", "Same", "distinct"),
        ("converged", "", "Continue", "choice labels"),
    ],
)
def test_family_policy_rejects_ambiguous_registration(
    signal: str,
    again: str,
    continuing: str,
    message: str,
) -> None:
    """Invalid signals and labels cannot enter durable policy state."""
    with pytest.raises(ReviewExchangeError, match=message):
        FamilyPolicy(signal, again, continuing)


def test_envelope_uses_only_the_first_fenced_json_block(tmp_path: Path) -> None:
    """A titled JSON section leaves later authored JSON fences untouched."""
    context = _context(tmp_path)
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        None,
        ReviewRole.REQUESTOR,
        2,
        _TIMESTAMP,
    )
    content = '## Request\n\nPlease review.\n\n```json\n{"authored": true}\n```\n'

    rendered = render_envelope_markdown(envelope, content)
    parsed, parsed_content = parse_envelope_markdown(rendered)

    assert parsed == envelope
    assert parsed_content == content
    assert rendered.startswith(
        "# Review request for "
        "specification/feature-request/v0.11.0/review-exchange_core\n\n"
        "## JSON\n\n```json\n",
    )
    with pytest.raises(ReviewExchangeError, match="first Markdown section"):
        parse_envelope_markdown(
            "# Review request\n\n## Metadata\n\n```json\n{}\n```\n",
        )


def test_envelope_rejects_unknown_fields_role_errors_and_utc_z(tmp_path: Path) -> None:
    """Strict metadata rejects schema drift, invalid roles, and missing offsets."""
    context = _context(tmp_path)
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        None,
        ReviewRole.REQUESTOR,
        1,
        _TIMESTAMP,
    )
    data = envelope.to_dict()
    data["unexpected"] = True
    with pytest.raises(ReviewExchangeError, match="unexpected envelope fields"):
        Envelope.from_dict(data)
    with pytest.raises(ReviewExchangeError, match="requestor envelope cannot declare"):
        Envelope(
            context.identity,
            context.umbrella_path,
            context.document_path,
            None,
            ReviewRole.REQUESTOR,
            1,
            _TIMESTAMP,
            ReviewDisposition.CHANGES_REQUESTED,
        )
    with pytest.raises(ReviewExchangeError, match="numeric UTC offset"):
        Envelope(
            context.identity,
            context.umbrella_path,
            context.document_path,
            None,
            ReviewRole.REQUESTOR,
            1,
            "2026-08-03T12:30:05Z",
        )


def test_summary_identity_matches_specification_and_code(tmp_path: Path) -> None:
    """Human fields must equal machine context before publication."""
    spec = _context(tmp_path / "spec")
    code = _context(tmp_path / "code", code=True)
    assert spec.umbrella_path is not None
    assert code.umbrella_path is not None
    spec_summary = (
        f"Umbrella draft: {spec.umbrella_path.as_posix()}\n"
        f"Reviewed specification: {spec.document_path.as_posix()}\n"
        "Review round: 3\n"
    )
    code_summary = (
        f"Umbrella draft: {code.umbrella_path.as_posix()}\n"
        f"Implementation plan: {code.document_path.as_posix()}\n"
        "Implementation step: 1\n"
        "Review round: 4\n"
    )

    validate_summary_identity(spec_summary, spec, 3)
    validate_summary_identity(code_summary, code, 4)
    with pytest.raises(ReviewExchangeError, match="summary identity mismatch"):
        validate_summary_identity(spec_summary.replace("round: 3", "round: 4"), spec, 3)


def test_coordination_record_round_trips_recovery_fields(tmp_path: Path) -> None:
    """Durable state reconstructs policy, recovery marker, and confirmation."""
    context = _context(tmp_path, code=True)
    record = CoordinationRecord(
        context=context,
        policy=FamilyPolicy("commit-ready", "Rework and review again", "Commit"),
        status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
        owner=Actor.REQUESTOR,
        expected_next_actor=Actor.HUMAN,
        round_number=3,
        lease_renewed_at=_TIMESTAMP,
        reviewed_work_changed=False,
        convergence_recommended=True,
        no_progress_streak=0,
        clarification_used=True,
        incomplete_transition=IncompleteTransitionKind.HUMAN_CONFIRMATION,
        transcript_entry_id="human-confirmation-3",
        transcript_offset=512,
        confirmation_label="Commit",
        confirmed_outcome=ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW,
        confirmation_timestamp=_TIMESTAMP,
    )

    assert CoordinationRecord.from_dict(record.to_dict()) == record


def test_coordination_record_rejects_impossible_states(tmp_path: Path) -> None:
    """Lease, escalation, and marker fields obey their state invariants."""
    context = _context(tmp_path)
    policy = FamilyPolicy("converged", "Again", "Consolidate")
    with pytest.raises(ReviewExchangeError, match="active coordination requires a lease"):
        CoordinationRecord(
            context=context,
            policy=policy,
            status=CoordinationStatus.ACTIVE,
            owner=Actor.REQUESTOR,
            expected_next_actor=Actor.REVIEWER,
            round_number=1,
            lease_renewed_at=None,
        )
    with pytest.raises(ReviewExchangeError, match="escalated coordination requires a reason"):
        CoordinationRecord(
            context=context,
            policy=policy,
            status=CoordinationStatus.ESCALATED,
            owner=Actor.REQUESTOR,
            expected_next_actor=Actor.REVIEWER,
            round_number=1,
            lease_renewed_at=None,
        )
    with pytest.raises(ReviewExchangeError, match="incomplete transition fields"):
        CoordinationRecord(
            context=context,
            policy=policy,
            status=CoordinationStatus.ACTIVE,
            owner=Actor.REQUESTOR,
            expected_next_actor=Actor.REVIEWER,
            round_number=1,
            lease_renewed_at=_TIMESTAMP,
            incomplete_transition=IncompleteTransitionKind.PUBLISH_REQUEST,
        )


def test_configuration_state_vocabulary_and_local_timestamp(tmp_path: Path) -> None:
    """Marker defaults, state names, and local time match the design contract."""
    assert ReviewConfiguration.load(tmp_path) == ReviewConfiguration(
        enabled=False,
        wait_timeout_seconds=_FALLBACK_WAIT_SECONDS,
    )
    marker = tmp_path / "a.review-mode"
    marker.write_text("", encoding="utf-8")
    assert ReviewConfiguration.load(tmp_path) == ReviewConfiguration(
        enabled=True,
        wait_timeout_seconds=_FALLBACK_WAIT_SECONDS,
    )
    marker.write_text("wait_timeout_seconds=2400\n", encoding="utf-8")
    assert ReviewConfiguration.load(tmp_path) == ReviewConfiguration(
        enabled=True,
        wait_timeout_seconds=2400,
    )
    assert ArtifactState.OWNING_ACTION_PENDING.value == "owning-action-pending"
    assert ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND.value == "interrupted-transcript-append"
    timestamp = format_local_timestamp()
    assert timestamp[-6] in {"+", "-"}
    assert timestamp[-3] == ":"


def test_review_configuration_rejects_another_repository_artifact_context(
    tmp_path: Path,
) -> None:
    """Invocation-bound configuration cannot cross repository boundaries."""
    other = tmp_path / "other"
    other.mkdir()
    artifacts = ReviewArtifactConfiguration.load(other)

    with pytest.raises(ReviewExchangeError, match="another repository"):
        load_review_configuration(
            tmp_path,
            configuration=artifacts,
        )


def test_shipped_settings_match_the_fallback_constant() -> None:
    """The shipped file governs, and the constant beside it may not drift."""
    assert _wait_setting_of(_PACKAGE_ROOT / _SETTINGS_NAME) == _FALLBACK_WAIT_SECONDS


def test_project_settings_take_precedence_over_the_shipped_default(
    tmp_path: Path,
) -> None:
    """A settings file at the reviewed repository root wins over the shipped one."""
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    assert ReviewConfiguration.load(tmp_path).wait_timeout_seconds == _FALLBACK_WAIT_SECONDS
    (tmp_path / ".review-exchange.ini").write_text(
        "[review-exchange]\nwait_timeout_seconds = 600\n",
        encoding="utf-8",
    )
    assert ReviewConfiguration.load(tmp_path).wait_timeout_seconds == _PROJECT_WAIT


def test_marker_override_wins_over_the_project_settings(tmp_path: Path) -> None:
    """The per-exchange marker still decides when both are present."""
    (tmp_path / ".review-exchange.ini").write_text(
        "[review-exchange]\nwait_timeout_seconds = 600\n",
        encoding="utf-8",
    )
    (tmp_path / "a.review-mode").write_text(
        "wait_timeout_seconds=90\n",
        encoding="utf-8",
    )
    assert ReviewConfiguration.load(tmp_path).wait_timeout_seconds == _MARKER_WAIT


@pytest.mark.parametrize(
    "content",
    [
        "",
        "not an ini at all\n",
        "[review-exchange]\n",
        "[review-exchange]\nwait_timeout_seconds =\n",
        "[review-exchange]\nwait_timeout_seconds = 0\n",
        "[review-exchange]\nwait_timeout_seconds = slow\n",
        "[review-exchange]\nwait_timeout_seconds = %broken\n",
        "[review-exchange]\nwait_timeout_seconds = -5\n",
        "[other]\nwait_timeout_seconds = 600\n",
    ],
)
def test_unusable_project_settings_fall_back_without_failing(
    tmp_path: Path,
    content: str,
) -> None:
    """A broken settings file is ignored, never fatal: a review must still run."""
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    (tmp_path / ".review-exchange.ini").write_text(content, encoding="utf-8")
    assert ReviewConfiguration.load(tmp_path).wait_timeout_seconds == _FALLBACK_WAIT_SECONDS


def test_unreadable_project_settings_fall_back_without_failing(tmp_path: Path) -> None:
    """A directory where the settings file is expected is ignored the same way."""
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    (tmp_path / ".review-exchange.ini").mkdir()
    assert ReviewConfiguration.load(tmp_path).wait_timeout_seconds == _FALLBACK_WAIT_SECONDS


def test_invalid_project_settings_fall_through_to_the_shipped_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unusable repository value does not hide a valid shipped value."""
    project = tmp_path / "project"
    shipped = tmp_path / "shipped"
    project.mkdir()
    shipped.mkdir()
    (project / "a.review-mode").write_text("", encoding="utf-8")
    (project / ".review-exchange.ini").write_text(
        "[review-exchange]\nwait_timeout_seconds = invalid\n",
        encoding="utf-8",
    )
    (shipped / ".review-exchange.ini").write_text(
        f"[review-exchange]\nwait_timeout_seconds = {_SHIPPED_WAIT}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(models, "_PACKAGE_ROOT", shipped)

    assert ReviewConfiguration.load(project).wait_timeout_seconds == _SHIPPED_WAIT


@pytest.mark.parametrize(
    "content",
    [
        "unknown=10\n",
        "wait_timeout_seconds=0\n",
        "wait_timeout_seconds=slow\n",
        "wait_timeout_seconds=10\nwait_timeout_seconds=20\n",
    ],
)
def test_configuration_rejects_invalid_marker_without_writes(
    tmp_path: Path,
    content: str,
) -> None:
    """Invalid marker data fails before an exchange artifact can be written."""
    marker = tmp_path / "a.review-mode"
    marker.write_text(content, encoding="utf-8")

    with pytest.raises(ReviewExchangeError, match=r"invalid a\.review-mode"):
        ReviewConfiguration.load(tmp_path)
    assert tuple(tmp_path.iterdir()) == (marker,)


# eof
