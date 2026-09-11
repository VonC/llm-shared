"""Validation-branch tests for v0.11.0 review-exchange models.

Step 1 coverage: exercises fail-closed serialized values, configuration IO,
coordination invariants, fenced metadata failures, and summary identity errors.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from tools.review_exchange_models import (
    Actor,
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
    enum_value,
    mapping_value,
    non_negative_integer,
    optional_boolean,
    optional_path_value,
    optional_string,
    path_value,
    positive_integer,
    strict_fields,
    validate_local_timestamp,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    Envelope,
    parse_envelope_markdown,
    parse_json_markdown,
    render_envelope_markdown,
    render_json_markdown,
    validate_summary_identity,
)

_VERSION = "v0.11.0"
_SLUG = "review-exchange-core"
_TIMESTAMP = "2026-08-03T14:30:05+02:00"


def _context(tmp_path: Path, *, code: bool = False) -> ReviewContext:
    """Create one valid review context for validation tests."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    identity = ExchangeIdentity(
        ReviewFamily.CODE if code else ReviewFamily.SPECIFICATION,
        "code" if code else "plan",
        _VERSION,
        _SLUG,
    )
    document = tmp_path / f"plan.{_VERSION}.{_SLUG}.md"
    document.write_text("# Plan\n", encoding="utf-8")
    return ReviewContext(identity, document, None, "1" if code else None)


def _policy() -> FamilyPolicy:
    """Return a valid family policy shared by coordination tests."""
    return FamilyPolicy("converged", "Another round", "Continue")


def test_serialized_value_helpers_reject_each_invalid_shape() -> None:
    """Shared JSON validators reject missing, mistyped, and invalid values."""
    with pytest.raises(ReviewExchangeError, match="missing sample fields"):
        strict_fields({"one": 1}, {"one", "two"}, "sample")
    with pytest.raises(ReviewExchangeError, match="expected a string"):
        enum_value(ReviewFamily, 3, "family")
    with pytest.raises(ReviewExchangeError, match="invalid family"):
        enum_value(ReviewFamily, "other", "family")
    with pytest.raises(ReviewExchangeError, match="string or null"):
        optional_string(3, "value")
    with pytest.raises(ReviewExchangeError, match="positive integer"):
        positive_integer(value=True, label="value")
    with pytest.raises(ReviewExchangeError, match="non-negative integer"):
        non_negative_integer(-1, "value")
    with pytest.raises(ReviewExchangeError, match="boolean or null"):
        optional_boolean("yes", "value")
    with pytest.raises(ReviewExchangeError, match="path string"):
        path_value("", "value")
    assert optional_path_value(None, "value") is None
    with pytest.raises(ReviewExchangeError, match="expected an object"):
        mapping_value([], "value")


def test_local_timestamp_rejects_invalid_calendar_and_missing_timezone() -> None:
    """Offset-looking text must still parse and carry actual timezone data."""
    with pytest.raises(ReviewExchangeError, match="valid ISO-8601"):
        validate_local_timestamp("2026-99-03T14:30:05+02:00")
    with pytest.raises(ReviewExchangeError, match="numeric UTC offset"):
        validate_local_timestamp("2026-08-03+02:00")


def test_identity_and_policy_reject_mistyped_serialized_fields() -> None:
    """Strict model factories do not coerce machine-readable field types."""
    identity_data: dict[str, object] = {
        "family": "specification",
        "type_token": 3,
        "version": _VERSION,
        "slug": _SLUG,
    }
    with pytest.raises(ReviewExchangeError, match="invalid identity type_token"):
        ExchangeIdentity.from_dict(identity_data)

    policy = _policy()
    assert policy.label_for(ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW) == "Continue"
    with pytest.raises(ReviewExchangeError, match="unsupported confirmation outcome"):
        policy.label_for(cast("ConfirmationOutcome", "other"))
    assert policy.outcome_for("Another round") is ConfirmationOutcome.ANOTHER_ROUND
    with pytest.raises(ReviewExchangeError, match="unregistered confirmation label"):
        policy.outcome_for("Unknown")
    policy_data = cast("dict[str, object]", policy.to_dict())
    policy_data["convergence_signal"] = 4
    with pytest.raises(ReviewExchangeError, match="fields must be strings"):
        FamilyPolicy.from_dict(policy_data)


def test_configuration_rejects_marker_directory_and_read_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Marker activation fails before writes when its content cannot be read."""
    directory_root = tmp_path / "directory"
    directory_root.mkdir()
    (directory_root / "a.review-mode").mkdir()
    with pytest.raises(ReviewExchangeError, match="marker is not a file"):
        ReviewConfiguration.load(directory_root)

    unreadable_root = tmp_path / "unreadable"
    unreadable_root.mkdir()
    marker = unreadable_root / "a.review-mode"
    marker.write_text("", encoding="utf-8")
    def fail_marker_read(
        path: Path,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> str:
        del path, encoding, errors, newline
        message = "denied"
        raise OSError(message)

    monkeypatch.setattr(Path, "read_text", fail_marker_read)
    with pytest.raises(ReviewExchangeError, match="denied"):
        ReviewConfiguration.load(unreadable_root)


def test_coordination_accepts_empty_overlays_and_rejects_status_conflicts(
    tmp_path: Path,
) -> None:
    """Valid active state has no overlays; invalid actor and lease states fail."""
    context = _context(tmp_path)
    record = CoordinationRecord(
        context=context,
        policy=_policy(),
        status=CoordinationStatus.ACTIVE,
        owner=Actor.REQUESTOR,
        expected_next_actor=Actor.REVIEWER,
        round_number=1,
        lease_renewed_at=_TIMESTAMP,
    )
    assert record.incomplete_transition is None
    assert record.confirmed_outcome is None

    with pytest.raises(ReviewExchangeError, match="human as next actor"):
        CoordinationRecord(
            context=context,
            policy=_policy(),
            status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
            owner=Actor.REQUESTOR,
            expected_next_actor=Actor.REVIEWER,
            round_number=1,
            lease_renewed_at=_TIMESTAMP,
        )
    with pytest.raises(ReviewExchangeError, match="cannot carry an active lease"):
        CoordinationRecord(
            context=context,
            policy=_policy(),
            status=CoordinationStatus.ESCALATED,
            owner=Actor.REQUESTOR,
            expected_next_actor=Actor.HUMAN,
            round_number=1,
            lease_renewed_at=_TIMESTAMP,
            escalation_reason="stopped",
        )


def test_coordination_rejects_partial_confirmation_and_mistyped_flag(
    tmp_path: Path,
) -> None:
    """Confirmation triples and serialized progress flags remain strict."""
    context = _context(tmp_path)
    with pytest.raises(ReviewExchangeError, match="confirmation fields"):
        CoordinationRecord(
            context=context,
            policy=_policy(),
            status=CoordinationStatus.ACTIVE,
            owner=Actor.REQUESTOR,
            expected_next_actor=Actor.REVIEWER,
            round_number=1,
            lease_renewed_at=_TIMESTAMP,
            confirmation_label="Continue",
        )

    record = CoordinationRecord(
        context=context,
        policy=_policy(),
        status=CoordinationStatus.ACTIVE,
        owner=Actor.REQUESTOR,
        expected_next_actor=Actor.REVIEWER,
        round_number=1,
        lease_renewed_at=_TIMESTAMP,
        incomplete_transition=IncompleteTransitionKind.PUBLISH_REQUEST,
        transcript_entry_id="request-1",
        transcript_offset=0,
    )
    data = record.to_dict()
    data["clarification_used"] = "no"
    with pytest.raises(ReviewExchangeError, match="clarification-used"):
        CoordinationRecord.from_dict(data)


def test_envelope_rejects_role_family_and_serialized_time_conflicts(
    tmp_path: Path,
) -> None:
    """Request and answer metadata enforce reviewer and family requirements."""
    spec = _context(tmp_path / "spec")
    code = _context(tmp_path / "code", code=True)
    with pytest.raises(ReviewExchangeError, match="reviewer envelope requires"):
        Envelope(
            spec.identity,
            None,
            spec.document_path,
            None,
            ReviewRole.REVIEWER,
            1,
            _TIMESTAMP,
        )
    with pytest.raises(ReviewExchangeError, match="code envelope requires"):
        Envelope(
            code.identity,
            None,
            code.document_path,
            None,
            ReviewRole.REQUESTOR,
            1,
            _TIMESTAMP,
        )
    with pytest.raises(ReviewExchangeError, match="only valid for code review"):
        Envelope(
            spec.identity,
            None,
            spec.document_path,
            "1",
            ReviewRole.REQUESTOR,
            1,
            _TIMESTAMP,
        )
    envelope = Envelope(
        spec.identity,
        None,
        spec.document_path,
        None,
        ReviewRole.REVIEWER,
        1,
        _TIMESTAMP,
        ReviewDisposition.CHANGES_REQUESTED,
    )
    data = envelope.to_dict()
    data["created_at"] = 3
    with pytest.raises(ReviewExchangeError, match="creation timestamp"):
        Envelope.from_dict(data)


@pytest.mark.parametrize(
    ("markdown", "message"),
    [
        ("No metadata\n", "start with an H1 title"),
        (
            "# Review request\n\n## JSON\n\n```json\n{}\n",
            "not closed",
        ),
        (
            "# Review request\n\n## JSON\n\n```json\n{bad}\n```\n",
            "invalid envelope JSON",
        ),
    ],
)
def test_envelope_parser_rejects_missing_unclosed_or_invalid_json(
    markdown: str,
    message: str,
) -> None:
    """Every malformed first-fence shape fails with a stable diagnostic."""
    with pytest.raises(ReviewExchangeError, match=message):
        parse_envelope_markdown(markdown)


def test_envelope_parser_rejects_authored_sections_that_start_at_h3(
    tmp_path: Path,
) -> None:
    """Authored sections cannot skip H2 after the document title and JSON."""
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
    markdown = render_envelope_markdown(envelope, "### Skipped level\n")

    with pytest.raises(ReviewExchangeError, match="sections must start at H2"):
        parse_envelope_markdown(markdown)


def test_json_markdown_rejects_a_multiline_title() -> None:
    """A serializer cannot create Markdown whose H1 spills onto another line."""
    with pytest.raises(ReviewExchangeError, match="title must be one non-empty line"):
        render_json_markdown("Broken\ntitle", {}, "")


def test_json_markdown_parses_crlf_before_authored_content() -> None:
    """Windows newlines keep later authored Markdown free of a blank prefix."""
    markdown = (
        "# Review request\r\n\r\n"
        "## JSON\r\n\r\n"
        "```json\r\n{}\r\n```\r\n\r\n"
        "## Review scope\r\n"
    )

    data, content = parse_json_markdown(markdown)

    assert data == {}
    assert content == "## Review scope\r\n"


def test_summary_requires_each_identity_field_once(tmp_path: Path) -> None:
    """A missing or duplicated summary field cannot pass publication checks."""
    context = _context(tmp_path)
    missing_round = (
        "Umbrella draft: none\n"
        f"Reviewed specification: {context.document_path.as_posix()}\n"
    )
    with pytest.raises(ReviewExchangeError, match="expected one Review round"):
        validate_summary_identity(missing_round, context, 1)


# eof
