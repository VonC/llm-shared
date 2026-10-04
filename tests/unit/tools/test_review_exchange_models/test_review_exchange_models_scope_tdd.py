"""Optional scope metadata is strict while legacy envelopes and records round trip."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.review_exchange_test_support import (
    review_artifact,
    review_context,
    review_policy,
)
from tools.review_exchange_models import (
    Actor,
    CoordinationStatus,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import Envelope, parse_envelope_markdown
from tools.scope_capture import WHOLE_SCOPE

if TYPE_CHECKING:
    from pathlib import Path


def _scope() -> dict[str, str | None]:
    """Return complete whole-suite evidence without inventing saved proof."""
    return {"scope": "whole", "group": None, "fingerprint": WHOLE_SCOPE.fingerprint,
            "requirement": None, "proof": "missing"}


def test_scope_and_legacy_metadata_round_trip(tmp_path: Path) -> None:
    """Serialization keeps new evidence explicit and old payloads unchanged."""
    context = review_context(tmp_path, ReviewFamily.CODE, "topic", step="6")
    legacy, _ = parse_envelope_markdown(review_artifact(context, ReviewRole.REQUESTOR, 1))
    assert "test_scope" not in legacy.to_dict()
    assert Envelope.from_dict(legacy.to_dict()) == legacy
    scoped = replace(legacy, test_scope=_scope())
    assert Envelope.from_dict(scoped.to_dict()) == scoped
    record = CoordinationRecord(context, review_policy(context), CoordinationStatus.ACTIVE,
                                Actor.REQUESTOR, Actor.REVIEWER, 1, legacy.created_at)
    assert "bound_scope_fingerprint" not in record.to_dict()
    assert CoordinationRecord.from_dict(record.to_dict()) == record
    bound = replace(record, bound_scope_fingerprint=WHOLE_SCOPE.fingerprint)
    assert CoordinationRecord.from_dict(bound.to_dict()) == bound
    with pytest.raises(ReviewExchangeError, match="bound scope fingerprint"):
        replace(record, bound_scope_fingerprint="invalid")


@pytest.mark.parametrize(("field", "value"), [
    ("scope", "group:other"), ("group", "INVALID"), ("fingerprint", "bad"),
    ("proof", "ready"), ("requirement", 1), ("extra", "field"),
])
def test_invalid_scope_metadata_rejected(tmp_path: Path, field: str, value: object) -> None:
    """Invalid values and extra fields are never silently accepted as evidence."""
    context = review_context(tmp_path, ReviewFamily.CODE, "topic", step="6")
    envelope, _ = parse_envelope_markdown(review_artifact(context, ReviewRole.REQUESTOR, 1))
    payload = envelope.to_dict()
    payload["test_scope"] = {**_scope(), field: value}
    with pytest.raises(ReviewExchangeError):
        Envelope.from_dict(payload)


def test_scope_only_belongs_to_code_requests(tmp_path: Path) -> None:
    """Specification requests cannot claim implementation validation scope."""
    context = review_context(tmp_path, ReviewFamily.SPECIFICATION, "topic")
    envelope, _ = parse_envelope_markdown(review_artifact(context, ReviewRole.REQUESTOR, 1))
    with pytest.raises(ReviewExchangeError, match="only valid for code requests"):
        replace(envelope, test_scope=_scope())


# eof
