"""TDD coverage for the v0.11.0 review-exchange artifact store.

Step 2 specifies exact-path atomic publication, identity validation, short
locks, append-only transcript repair, request tombstones, and evidence archives.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.review_exchange_models import (
    Actor,
    ArchiveKind,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore, TranscriptEntry

_VERSION = "v0.11.0"
_SLUG = "review-exchange-core"
_RECORDED_AT = "2026-08-04T10:30:00+02:00"
_MARKER_CLEAR_WRITE_COUNT = 2
_TRANSIENT_REPLACE_ATTEMPTS = 3
_TRANSIENT_REPLACE_DELAYS = (0.01, 0.02)


def _context(tmp_path: Path, family: ReviewFamily) -> ReviewContext:
    """Create one exact reviewed document and validated context."""
    if family is ReviewFamily.CODE:
        identity = ExchangeIdentity(family, "code", _VERSION, _SLUG)
        document_name = f"plan.{_VERSION}.{_SLUG}.md"
        step = "2"
    else:
        identity = ExchangeIdentity(
            family,
            "design-specification",
            _VERSION,
            _SLUG,
        )
        document_name = f"design.{_VERSION}.{_SLUG}.md"
        step = None
    document = tmp_path / "docs" / _VERSION / document_name
    document.parent.mkdir(parents=True)
    document.write_text("# Reviewed document\n", encoding="utf-8")
    return ReviewContext(identity, document, None, step)


def _store(
    tmp_path: Path,
    family: ReviewFamily = ReviewFamily.CODE,
) -> tuple[ReviewExchangeStore, ReviewContext]:
    """Build one store from a constant exact artifact set."""
    context = _context(tmp_path, family)
    paths = derive_artifact_paths(tmp_path, context)
    return ReviewExchangeStore(paths), context


def _record(context: ReviewContext) -> CoordinationRecord:
    """Create active coordination suitable for a request transcript append."""
    return CoordinationRecord(
        context=context,
        policy=FamilyPolicy("ready", "Another round", "Continue"),
        status=CoordinationStatus.ACTIVE,
        owner=Actor.REQUESTOR,
        expected_next_actor=Actor.REVIEWER,
        round_number=1,
        lease_renewed_at=_RECORDED_AT,
    )


def _artifact(
    context: ReviewContext,
    role: ReviewRole,
    content: str,
) -> str:
    """Render one exact request or answer artifact."""
    disposition = (
        ReviewDisposition.CHANGES_REQUESTED
        if role is ReviewRole.REVIEWER
        else None
    )
    envelope = Envelope(
        identity=context.identity,
        umbrella_path=context.umbrella_path,
        document_path=context.document_path,
        implementation_step=context.implementation_step,
        role=role,
        round_number=1,
        created_at=_RECORDED_AT,
        disposition=disposition,
    )
    return render_envelope_markdown(envelope, content)


def _entry(content: str) -> TranscriptEntry:
    """Create one deterministic requestor transcript entry."""
    return TranscriptEntry(
        entry_id="request-round-1",
        role=ReviewRole.REQUESTOR,
        outcome="request",
        recorded_at=_RECORDED_AT,
        authored_content=content,
    )


def test_publish_atomic_replaces_complete_utf8_content(tmp_path: Path) -> None:
    """Atomic replacement exposes the complete encoded artifact."""
    store, context = _store(tmp_path)
    first = _artifact(context, ReviewRole.REQUESTOR, "Première demande\n")
    second = _artifact(context, ReviewRole.REQUESTOR, "Demande corrigée ✓\n")

    store.publish_atomic(store.paths.request, first)
    store.publish_atomic(store.paths.request, second)

    assert store.paths.request.read_bytes() == second.encode("utf-8")
    assert not tuple(tmp_path.glob(".review-exchange-*.tmp"))


def test_failed_atomic_replace_preserves_existing_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure before replacement keeps the previous complete artifact."""
    store, context = _store(tmp_path)
    first = _artifact(context, ReviewRole.REQUESTOR, "Original\n")
    second = _artifact(context, ReviewRole.REQUESTOR, "Replacement\n")
    store.publish_atomic(store.paths.request, first)

    def fail_replace(prepared: Path, target: Path) -> None:
        del prepared, target
        message = "injected replace failure"
        raise OSError(message)

    monkeypatch.setattr(store, "_commit_prepared", fail_replace)

    with pytest.raises(ReviewExchangeError, match="atomic publication failed"):
        store.publish_atomic(store.paths.request, second)
    assert store.paths.request.read_text(encoding="utf-8") == first
    assert not tuple(tmp_path.glob(".review-exchange-*.tmp"))


def test_atomic_replace_retries_a_transient_sharing_denial(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A short-lived sharing denial does not strand a prepared artifact."""
    store, context = _store(tmp_path)
    content = _artifact(context, ReviewRole.REQUESTOR, "Retry safely\n")
    original_replace = Path.replace
    attempts = 0
    delays: list[float] = []

    def flaky_replace(source: Path, target: Path) -> Path:
        nonlocal attempts
        attempts += 1
        if attempts < _TRANSIENT_REPLACE_ATTEMPTS:
            message = "injected transient sharing denial"
            raise PermissionError(message)
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", flaky_replace)
    monkeypatch.setattr("tools.review_exchange_store.time.sleep", delays.append)

    store.publish_atomic(store.paths.request, content)

    assert attempts == _TRANSIENT_REPLACE_ATTEMPTS
    assert tuple(delays) == _TRANSIENT_REPLACE_DELAYS
    assert store.paths.request.read_text(encoding="utf-8") == content


def test_artifact_publication_rejects_cross_identity_content(tmp_path: Path) -> None:
    """A matching filename never accepts another envelope identity."""
    store, context = _store(tmp_path)
    other_identity = ExchangeIdentity(ReviewFamily.CODE, "code", _VERSION, "other")
    envelope = Envelope(
        identity=other_identity,
        umbrella_path=None,
        document_path=context.document_path,
        implementation_step="2",
        role=ReviewRole.REQUESTOR,
        round_number=1,
        created_at=_RECORDED_AT,
    )
    content = render_envelope_markdown(envelope, "Wrong exchange\n")

    with pytest.raises(ReviewExchangeError, match="identity does not match"):
        store.publish_atomic(store.paths.request, content)
    assert not store.paths.request.exists()


def test_publish_request_removes_only_a_valid_stale_answer(tmp_path: Path) -> None:
    """A new request removes its matching stale answer before visibility."""
    store, context = _store(tmp_path)
    store.publish_atomic(
        store.paths.answer,
        _artifact(context, ReviewRole.REVIEWER, "Stale answer\n"),
    )

    store.publish_request(_artifact(context, ReviewRole.REQUESTOR, "New request\n"))

    assert store.paths.request.is_file()
    assert not store.paths.answer.exists()


def test_publish_answer_consumes_request_before_answer_visibility(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The request path disappears into a tombstone before answer publication."""
    store, context = _store(tmp_path)
    request = _artifact(context, ReviewRole.REQUESTOR, "Review this\n")
    answer = _artifact(context, ReviewRole.REVIEWER, "Changes requested\n")
    store.publish_request(request)
    observed: dict[str, bool] = {}

    def stop_after_consume(prepared: Path, target: Path) -> None:
        del prepared, target
        observed["request"] = store.paths.request.exists()
        observed["tombstone"] = store.paths.tombstone.exists()
        observed["answer"] = store.paths.answer.exists()
        message = "injected answer publication failure"
        raise OSError(message)

    monkeypatch.setattr(store, "_commit_prepared", stop_after_consume)

    with pytest.raises(ReviewExchangeError, match="answer publication failed"):
        store.publish_answer(answer)
    assert observed == {"request": False, "tombstone": True, "answer": False}
    assert store.paths.tombstone.read_text(encoding="utf-8") == request


def test_publish_answer_leaves_tombstone_until_exact_cleanup(tmp_path: Path) -> None:
    """Successful answer publication preserves consumed evidence for append repair."""
    store, context = _store(tmp_path)
    request = _artifact(context, ReviewRole.REQUESTOR, "Review this\n")
    answer = _artifact(context, ReviewRole.REVIEWER, "Ready\n")
    store.publish_request(request)

    store.publish_answer(answer)

    assert not store.paths.request.exists()
    assert store.paths.answer.read_text(encoding="utf-8") == answer
    assert store.paths.tombstone.read_text(encoding="utf-8") == request
    store.remove_exact(store.paths.tombstone)
    assert not store.paths.tombstone.exists()


@pytest.mark.parametrize("family", list(ReviewFamily))
def test_initialize_transcript_uses_family_template_and_preserves_existing(
    tmp_path: Path,
    family: ReviewFamily,
) -> None:
    """A missing transcript uses its family template and is never overwritten."""
    store, context = _store(tmp_path, family)

    created = store.initialize_transcript(context)
    initial = store.paths.transcript.read_text(encoding="utf-8")
    store.paths.transcript.write_text(f"{initial}\nHuman note\n", encoding="utf-8")
    preserved = store.initialize_transcript(context)

    assert created is True
    assert preserved is False
    assert context.identity.key in initial
    assert context.document_path.relative_to(store.paths.project_root).as_posix() in initial
    assert context.document_path.as_posix() not in initial
    with pytest.raises(ReviewExchangeError, match="outside the project root"):
        store._transcript_path(tmp_path.parent / "outside.md")
    assert context.identity.family.value.title() in initial
    assert store.paths.transcript.read_text(encoding="utf-8").endswith(
        "Human note\n",
    )


def test_append_transcript_once_labels_role_round_and_stable_footer(
    tmp_path: Path,
) -> None:
    """A complete entry is labeled and clears its durable repair marker."""
    store, context = _store(tmp_path)
    record = _record(context)
    store.initialize_transcript(context)
    store.write_coordination(record)

    first = store.append_transcript_once(
        record,
        transition=IncompleteTransitionKind.PUBLISH_REQUEST,
        entry=_entry("Please review the persistence primitives.\n"),
    )
    transcript = store.paths.transcript.read_text(encoding="utf-8")

    assert transcript.count("## Round 1 by requestor - Step 2") == 1
    assert transcript.count("review-entry-id: request-round-1") == 1
    assert "Implementation step: 2" in transcript
    assert first.incomplete_transition is None
    assert store.read_coordination() == first


def test_torn_append_repairs_only_suffix_from_persisted_offset(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repair truncates a torn suffix and appends one complete entry."""
    store, context = _store(tmp_path)
    record = _record(context)
    store.initialize_transcript(context)
    store.write_coordination(record)
    original_append = store._append_bytes

    def append_torn(path: Path, content: bytes) -> None:
        with path.open("ab") as stream:
            stream.write(content[: len(content) // 2])
            stream.flush()
        message = "injected torn append"
        raise OSError(message)

    monkeypatch.setattr(store, "_append_bytes", append_torn)
    with pytest.raises(ReviewExchangeError, match="transcript append failed"):
        store.append_transcript_once(
            record,
            transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            entry=_entry("Complete substantive content.\n"),
        )
    marked = store.read_coordination()
    assert marked is not None
    assert marked.transcript_offset is not None
    prefix = store.paths.transcript.read_bytes()[: marked.transcript_offset]

    monkeypatch.setattr(store, "_append_bytes", original_append)
    repaired = store.append_transcript_once(
        record,
        transition=IncompleteTransitionKind.PUBLISH_REQUEST,
        entry=_entry("Complete substantive content.\n"),
    )
    final = store.paths.transcript.read_bytes()

    assert final.startswith(prefix)
    assert final.count(b"review-entry-id: request-round-1") == 1
    assert repaired.incomplete_transition is None


def test_complete_append_repairs_marker_without_duplicate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A crash after append clears the marker without appending twice."""
    store, context = _store(tmp_path)
    record = _record(context)
    store.initialize_transcript(context)
    store.write_coordination(record)
    original_write = store.write_coordination
    writes = 0

    def fail_second_write(value: CoordinationRecord) -> None:
        nonlocal writes
        writes += 1
        if writes == _MARKER_CLEAR_WRITE_COUNT:
            message = "injected marker clear failure"
            raise ReviewExchangeError(message)
        original_write(value)

    monkeypatch.setattr(store, "write_coordination", fail_second_write)
    with pytest.raises(ReviewExchangeError, match="marker clear failure"):
        store.append_transcript_once(
            record,
            transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            entry=_entry("Complete content.\n"),
        )

    monkeypatch.setattr(store, "write_coordination", original_write)
    store.append_transcript_once(
        record,
        transition=IncompleteTransitionKind.PUBLISH_REQUEST,
        entry=_entry("Complete content.\n"),
    )

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: request-round-1") == 1


@pytest.mark.parametrize("kind", list(ArchiveKind))
def test_archive_evidence_moves_only_the_selected_exact_artifact(
    tmp_path: Path,
    kind: ArchiveKind,
) -> None:
    """Recovery moves one validated artifact to its identity-scoped archive."""
    store, context = _store(tmp_path)
    record = _record(context)
    sources = {
        ArchiveKind.REQUEST: (
            store.paths.request,
            _artifact(context, ReviewRole.REQUESTOR, "Request\n"),
        ),
        ArchiveKind.ANSWER: (
            store.paths.answer,
            _artifact(context, ReviewRole.REVIEWER, "Answer\n"),
        ),
        ArchiveKind.CONSUMED: (
            store.paths.tombstone,
            _artifact(context, ReviewRole.REQUESTOR, "Consumed\n"),
        ),
        ArchiveKind.COORDINATION: (store.paths.coordination, None),
    }
    source, content = sources[kind]
    if kind is ArchiveKind.COORDINATION:
        store.write_coordination(record)
    else:
        store.publish_atomic(source, content or "")

    archived = store.archive_evidence(kind, "20260804-103000")

    assert not source.exists()
    assert archived.is_file()
    assert archived.name.endswith(f".20260804-103000.{kind.value}.md")


def test_transition_lock_is_released_when_transition_raises(tmp_path: Path) -> None:
    """The short operating-system lock can be reacquired after an exception."""
    store, _ = _store(tmp_path)
    message = "injected transition failure"

    def fail_inside_lock() -> None:
        with store.transition_lock():
            raise RuntimeError(message)

    with pytest.raises(
        RuntimeError,
        match="injected transition failure",
    ):
        fail_inside_lock()

    with store.transition_lock():
        assert store.paths.transition_lock.is_file()


def test_unknown_exact_path_is_rejected_without_directory_discovery(
    tmp_path: Path,
) -> None:
    """Generic persistence cannot escape the fixed artifact set."""
    store, _ = _store(tmp_path)

    with pytest.raises(ReviewExchangeError, match="outside the exact artifact set"):
        store.publish_atomic(tmp_path / "a.review-requested.other.md", "content")


# eof
