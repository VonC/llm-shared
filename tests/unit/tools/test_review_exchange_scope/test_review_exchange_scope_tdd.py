"""Bind one validated scope to a review and preserve legacy missing evidence."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.review_exchange_test_support import (
    configured_home,
    review_context,
    review_policy,
)
from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    FakeTime,
    _answer,
    _harness,
    _request,
)
from tools import review_exchange_scope as scopes
from tools.review_artifact_registry import (
    RegisteredArtifactKind,
    ReviewArtifactRegistry,
)
from tools.review_exchange_models import (
    Actor,
    CoordinationStatus,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    parse_envelope_markdown,
    render_envelope_markdown,
)
from tools.review_exchange_paths import (
    derive_artifact_paths,
    transient_paths_for_ignore,
)
from tools.scope_capture import WHOLE_SCOPE

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_core import ReviewExchangeCore
    from tools.review_exchange_models import ReviewContext
    from tools.scope_capture import ResolvedScope


def test_publish_status_archive_and_remove(tmp_path: Path) -> None:
    """A capture is registered, validated on status, archived and removed exactly."""
    configured_home(tmp_path)
    context = review_context(tmp_path, ReviewFamily.CODE, "topic", step="6")
    paths = derive_artifact_paths(tmp_path, context)
    record = CoordinationRecord(context, review_policy(context), CoordinationStatus.ACTIVE,
                                Actor.REQUESTOR, Actor.REVIEWER, 1, "2026-10-04T12:00:00+02:00")
    assert scopes.bound_scope_payload(paths, record) == "missing"
    scopes.publish_scope_capture(paths, WHOLE_SCOPE.to_json(), WHOLE_SCOPE.fingerprint)
    bound = replace(record, bound_scope_fingerprint=WHOLE_SCOPE.fingerprint)
    assert scopes.bound_scope_payload(paths, bound) == {
        "scope": "whole", "group": None, "fingerprint": WHOLE_SCOPE.fingerprint,
    }
    archived = scopes.archive_scope_capture(paths, "20261004-120000")
    assert archived is not None
    assert not paths.scope.exists()
    assert scopes.archive_scope_capture(paths, "20261004-120000") is None
    scopes.publish_scope_capture(paths, WHOLE_SCOPE.to_json(), WHOLE_SCOPE.fingerprint)
    scopes.remove_scope_capture(paths)
    scopes.remove_scope_capture(paths)
    assert archived.is_file()
    assert not paths.scope.exists()


def test_capture_registry_and_ignore_contract(tmp_path: Path) -> None:
    """The optional scope path has registered live and archive names and is ignored."""
    configured_home(tmp_path)
    paths = derive_artifact_paths(tmp_path, review_context(tmp_path, ReviewFamily.CODE, "topic", step="6"))
    assert paths.scope.name == "a.review-scope.code.v0.11.0.topic.json"
    assert paths.scope in transient_paths_for_ignore(paths)
    assert paths.scope not in paths.fixed_paths
    scopes.publish_scope_capture(paths, WHOLE_SCOPE.to_json(), WHOLE_SCOPE.fingerprint)
    archived = scopes.archive_scope_capture(paths, "20261004-120000")
    assert archived is not None
    assert archived.name.endswith(".scope.json")
    parsed = ReviewArtifactRegistry().parse_name(archived.name)
    assert parsed is not None
    assert parsed.kind is RegisteredArtifactKind.ARCHIVE


def _scoped_request(context: ReviewContext, clock: FakeTime, number: int = 1, scope: ResolvedScope = WHOLE_SCOPE) -> str:
    """Attach exact scope evidence to the established lifecycle request fixture."""
    envelope, authored = parse_envelope_markdown(_request(context, clock, number))
    evidence = {"scope": scope.key(), "group": scope.name or None, "fingerprint": scope.fingerprint,
                "requirement": None, "proof": "missing"}
    return render_envelope_markdown(replace(envelope, test_scope=evidence), authored)


@pytest.mark.parametrize("operation", ["complete", "force"])
def test_capture_follows_every_coordination_exit(tmp_path: Path, operation: str) -> None:
    """Every lifecycle exit clears the live capture; archive retains exact bytes."""
    configured_home(tmp_path)
    core, store, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_scoped_request(context, clock), "Request evidence.", WHOLE_SCOPE.to_json())
    record = store.read_coordination()
    assert record is not None
    assert record.bound_scope_fingerprint == WHOLE_SCOPE.fingerprint
    if operation == "complete":
        core.publish_answer(_answer(context, clock, 1, ReviewDisposition.CONVERGENCE_RECOMMENDED), "Ready.")
        core.confirm("Commit")
        assert core.complete()
    else:
        core.publish_answer(_answer(context, clock, 1), "Rework.")
        core.consume_answer(reviewed_work_changed=True)
        core.continue_round()
        clock.sleep(600)
        assert core.force_complete("Abandoned work retired.")
    assert not store.paths.scope.exists()
    assert not store.paths.coordination.exists()


@pytest.mark.parametrize("archive", [True, False])
def test_resolution_retires_scope(tmp_path: Path, *, archive: bool) -> None:
    """Resolution starts unbound and archives the exact old capture when requested."""
    configured_home(tmp_path)
    core, store, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_scoped_request(context, clock), "Request evidence.", WHOLE_SCOPE.to_json())
    before = store.paths.scope.read_bytes()
    core.escalate("Needs human decision.", ReviewRole.REQUESTOR)
    result = core.resolve_escalation("Use a fresh round.", archive=archive)
    assert scopes.bound_scope_payload(store.paths, result.record) == "missing"
    archived = [path for path in result.archived_paths if path.name.endswith(".scope.json")]
    if archive:
        assert len(archived) == 1
        assert archived[0].read_bytes() == before
    else:
        assert archived == []
    assert not store.paths.scope.exists()


def _assert_refused_without_mutation(core: ReviewExchangeCore, markdown: str, capture: str | None) -> None:
    """Publication refusal preserves every file already in the artifact home."""
    home = core.store.paths.scope.parent
    before = {path.name: path.read_bytes() for path in home.iterdir() if path.is_file()}
    with pytest.raises(ReviewExchangeError):
        core.publish_request(markdown, "Report.", capture)
    after = {path.name: path.read_bytes() for path in home.iterdir() if path.is_file()}
    assert after == before


@pytest.mark.parametrize("problem", ["missing", "invalid", "fingerprint", "identity", "legacy"])
def test_publication_refuses_capture_before_any_write(tmp_path: Path, problem: str) -> None:
    """A rejected request leaves all existing coordination and transcript bytes intact."""
    configured_home(tmp_path)
    core, _store, context, clock = _harness(tmp_path)
    core.start()
    markdown = _scoped_request(context, clock)
    capture = None if problem == "missing" else WHOLE_SCOPE.to_json()
    if problem == "invalid":
        capture = "{}"
    elif problem in {"fingerprint", "identity"}:
        envelope, authored = parse_envelope_markdown(markdown)
        assert envelope.test_scope is not None
        evidence = dict(envelope.test_scope)
        evidence.update({"fingerprint": "f" * 64} if problem == "fingerprint" else {"scope": "group:sentinel", "group": "sentinel"})
        markdown = render_envelope_markdown(replace(envelope, test_scope=evidence), authored)
    elif problem == "legacy":
        markdown = _request(context, clock, 1)
    _assert_refused_without_mutation(core, markdown, capture)


def test_status_missing_and_write_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing, invalid and unwritable captures retain stable missing/error behavior."""
    configured_home(tmp_path)
    core, store, _context, _clock = _harness(tmp_path)
    record = replace(core.start(), bound_scope_fingerprint=WHOLE_SCOPE.fingerprint)
    assert scopes.bound_scope_payload(store.paths, None) == "missing"
    assert scopes.bound_scope_payload(store.paths, record) == "missing"
    store.paths.scope.write_text("{}", encoding="utf-8")
    assert scopes.bound_scope_payload(store.paths, record) == "missing"
    scopes.publish_scope_capture(store.paths, WHOLE_SCOPE.to_json(), WHOLE_SCOPE.fingerprint)
    scopes.archive_scope_capture(store.paths, "20261004-120000")
    scopes.publish_scope_capture(store.paths, WHOLE_SCOPE.to_json(), WHOLE_SCOPE.fingerprint)
    with pytest.raises(ReviewExchangeError, match="already exists"):
        scopes.archive_scope_capture(store.paths, "20261004-120000")

    def fail(*_args: object) -> None:
        message = "unwritable"
        raise scopes.scope_capture.CaptureError(message)

    monkeypatch.setattr(scopes.scope_capture, "write_capture", fail)
    with pytest.raises(ReviewExchangeError, match="unwritable"):
        scopes.publish_scope_capture(store.paths, WHOLE_SCOPE.to_json(), WHOLE_SCOPE.fingerprint)


@pytest.mark.parametrize(("text", "fingerprint"), [("{}", WHOLE_SCOPE.fingerprint), (WHOLE_SCOPE.to_json(), "bad")])
def test_invalid_capture_never_writes(tmp_path: Path, text: str, fingerprint: str) -> None:
    """Missing capture fields or envelope mismatch cannot replace live evidence."""
    configured_home(tmp_path)
    paths = derive_artifact_paths(tmp_path, review_context(tmp_path, ReviewFamily.CODE, "topic", step="6"))
    with pytest.raises(ReviewExchangeError):
        scopes.publish_scope_capture(paths, text, fingerprint)
    assert not paths.scope.exists()
