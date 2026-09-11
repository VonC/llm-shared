"""Failure-path TDD coverage for the v0.11.0 review-exchange stores.

Step 3 keeps exact persistence failure coverage while moving both platform lock
adapters behind the focused ownership store.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tools import review_exchange_ownership_store as ownership_store_module
from tools import review_exchange_store as store_module
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
from tools.review_exchange_paths import archive_path, derive_artifact_paths
from tools.review_exchange_store import (
    ReviewExchangeStore,
    TranscriptEntry,
)

# ruff: noqa: SLF001

_VERSION = "v0.11.0"
_SLUG = "review-exchange-core"
_RECORDED_AT = "2026-08-04T10:30:00+02:00"
_ATOMIC_REPLACE_ATTEMPTS = 5


def _context(root: Path, *, parent: str = "docs") -> ReviewContext:
    """Create a valid code-review context below one selected parent."""
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", _VERSION, _SLUG)
    document = root / parent / f"plan.{_VERSION}.{_SLUG}.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Plan\n", encoding="utf-8")
    return ReviewContext(identity, document, None, "2")


def _store(root: Path) -> tuple[ReviewExchangeStore, ReviewContext]:
    """Build a store bound to one exact temporary exchange."""
    root.mkdir(parents=True, exist_ok=True)
    context = _context(root)
    return ReviewExchangeStore(derive_artifact_paths(root, context)), context


def _record(context: ReviewContext) -> CoordinationRecord:
    """Create one active coordination record for persistence tests."""
    return CoordinationRecord(
        context=context,
        policy=FamilyPolicy("ready", "Another round", "Continue"),
        status=CoordinationStatus.ACTIVE,
        owner=Actor.REQUESTOR,
        expected_next_actor=Actor.REVIEWER,
        round_number=1,
        lease_renewed_at=_RECORDED_AT,
    )


def _artifact(context: ReviewContext, role: ReviewRole) -> str:
    """Render a valid identity-bearing request or answer."""
    disposition = (
        ReviewDisposition.CHANGES_REQUESTED
        if role is ReviewRole.REVIEWER
        else None
    )
    envelope = Envelope(
        identity=context.identity,
        umbrella_path=None,
        document_path=context.document_path,
        implementation_step="2",
        role=role,
        round_number=1,
        created_at=_RECORDED_AT,
        disposition=disposition,
    )
    return render_envelope_markdown(envelope, "Substantive content.\n")


def _entry() -> TranscriptEntry:
    """Return one deterministic request transcript entry."""
    return TranscriptEntry(
        "request-round-1",
        ReviewRole.REQUESTOR,
        "request",
        _RECORDED_AT,
        "Review this work.\n",
    )


def test_transcript_entry_rejects_invalid_identity_outcome_and_footer() -> None:
    """Entry metadata cannot make suffix repair ambiguous."""
    with pytest.raises(ReviewExchangeError, match="entry identifier"):
        TranscriptEntry("Bad id", ReviewRole.REQUESTOR, "request", _RECORDED_AT, "x")
    with pytest.raises(ReviewExchangeError, match="unsupported transcript outcome"):
        TranscriptEntry("valid", ReviewRole.REQUESTOR, "unknown", _RECORDED_AT, "x")
    with pytest.raises(ReviewExchangeError, match="reserved entry footer"):
        TranscriptEntry(
            "valid",
            ReviewRole.REQUESTOR,
            "request",
            _RECORDED_AT,
            "<!-- review-entry-id: forged -->",
        )
    with pytest.raises(ReviewExchangeError, match="occurrence must be positive"):
        TranscriptEntry("valid", ReviewRole.HUMAN, "escalation", _RECORDED_AT, "x", 0)


def test_entry_occurrence_counts_only_existing_transcript_identities(
    tmp_path: Path,
) -> None:
    """A repeatable identity starts at one and advances per recorded footer."""
    store, context = _store(tmp_path)

    assert store.entry_occurrence("escalation-round-1") == 1

    store.initialize_transcript(context)
    assert store.entry_occurrence("escalation-round-1") == 1


def test_content_operations_reject_wrong_roles_and_non_content_paths(
    tmp_path: Path,
) -> None:
    """Exact filenames cannot accept a wrong role or a non-content operation."""
    store, context = _store(tmp_path)

    with pytest.raises(ReviewExchangeError, match="role must be requestor"):
        store.publish_atomic(
            store.paths.request,
            _artifact(context, ReviewRole.REVIEWER),
        )
    with pytest.raises(ReviewExchangeError, match="not a review-content artifact"):
        store.read_artifact(store.paths.transcript)
    store.initialize_transcript(context)
    with pytest.raises(ReviewExchangeError, match="not an exact cleanup target"):
        store.remove_exact(store.paths.transcript)
    with pytest.raises(ReviewExchangeError, match="transcript is append-only"):
        store.publish_atomic(store.paths.transcript, "history rewrite")
    with pytest.raises(ReviewExchangeError, match="lock is not a content artifact"):
        store.publish_atomic(store.paths.transition_lock, "x")


def test_read_artifact_reports_an_unreadable_exact_path(tmp_path: Path) -> None:
    """Unreadable request content fails closed before identity use."""
    store, _ = _store(tmp_path)
    store.paths.request.parent.mkdir(parents=True, exist_ok=True)
    store.paths.request.mkdir()

    with pytest.raises(ReviewExchangeError, match="cannot read review artifact"):
        store.read_artifact(store.paths.request)


def test_publish_request_reports_commit_failure_and_discards_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed request replacement leaves no prepared temporary file."""
    store, context = _store(tmp_path)

    def fail_commit(prepared: Path, target: Path) -> None:
        del prepared, target
        message = "injected request commit failure"
        raise OSError(message)

    monkeypatch.setattr(store, "_commit_prepared", fail_commit)

    with pytest.raises(ReviewExchangeError, match="request publication failed"):
        store.publish_request(_artifact(context, ReviewRole.REQUESTOR))
    assert not tuple(store.paths.request.parent.glob(".review-exchange-*.tmp"))


def test_consume_request_rejects_missing_existing_and_failed_rename(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every request-to-tombstone precondition preserves exact evidence."""
    store, context = _store(tmp_path)
    request = _artifact(context, ReviewRole.REQUESTOR)

    with pytest.raises(ReviewExchangeError, match="request does not exist"):
        store.consume_request_to_tombstone()
    store.publish_atomic(store.paths.request, request)
    store.publish_atomic(store.paths.tombstone, request)
    with pytest.raises(ReviewExchangeError, match="tombstone already exists"):
        store.consume_request_to_tombstone()
    store.paths.tombstone.unlink()
    original_replace = Path.replace

    def fail_request_replace(source: Path, target: Path) -> Path:
        if source == store.paths.request:
            message = "injected request rename failure"
            raise OSError(message)
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_request_replace)
    with pytest.raises(ReviewExchangeError, match="request consumption failed"):
        store.consume_request_to_tombstone()
    assert store.paths.request.is_file()


def test_coordination_cleanup_and_unlink_failure_are_exact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coordination cleanup validates content and reports unlink failure."""
    store, context = _store(tmp_path / "remove")
    store.write_coordination(_record(context))
    assert store.remove_exact(store.paths.coordination) is True

    other, other_context = _store(tmp_path / "failure")
    other.publish_atomic(other.paths.answer, _artifact(other_context, ReviewRole.REVIEWER))
    original_unlink = Path.unlink

    def fail_answer_unlink(path: Path, *, missing_ok: bool = False) -> None:
        if path == other.paths.answer:
            message = "injected cleanup failure"
            raise OSError(message)
        original_unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", fail_answer_unlink)
    with pytest.raises(ReviewExchangeError, match="exact cleanup failed"):
        other.remove_exact(other.paths.answer)


def test_transcript_initialization_reports_invalid_template_and_commit_states(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Transcript initialization preserves winners and reports unsafe failures."""
    directory_store, directory_context = _store(tmp_path / "directory")
    directory_store.paths.transcript.mkdir()
    with pytest.raises(ReviewExchangeError, match="transcript path is not a file"):
        directory_store.initialize_transcript(directory_context)

    missing_store, missing_context = _store(tmp_path / "missing-template")
    missing = ReviewExchangeStore(
        missing_store.paths,
        template_root=tmp_path / "absent-templates",
    )
    with pytest.raises(ReviewExchangeError, match="cannot initialize transcript"):
        missing.initialize_transcript(missing_context)

    race_store, race_context = _store(tmp_path / "race")
    original_prepare = race_store._prepare_atomic

    def prepare_after_winner(target: Path, content: bytes) -> Path:
        prepared = original_prepare(target, content)
        target.write_text("# Concurrent winner\n", encoding="utf-8")
        return prepared

    monkeypatch.setattr(race_store, "_prepare_atomic", prepare_after_winner)
    assert race_store.initialize_transcript(race_context) is False
    assert race_store.paths.transcript.read_text(encoding="utf-8") == (
        "# Concurrent winner\n"
    )

    failed_store, failed_context = _store(tmp_path / "failed-commit")

    def fail_commit(prepared: Path, target: Path) -> None:
        del prepared, target
        message = "injected transcript commit failure"
        raise OSError(message)

    monkeypatch.setattr(failed_store, "_commit_prepared", fail_commit)
    with pytest.raises(ReviewExchangeError, match="initialization failed"):
        failed_store.initialize_transcript(failed_context)


@pytest.mark.parametrize(
    "content",
    [
        "{}",
        "# Coordination\n\n```json\n{}\n```\n",
        "# Coordination\n\n## JSON\n\n```json\n{}",
        "# Coordination\n\n## JSON\n\n```json\n{}\n```\n\ntrailing",
        "# Coordination\n\n## JSON\n\n```json\n{invalid}\n```\n",
    ],
)
def test_coordination_json_rejects_each_invalid_fence_shape(
    tmp_path: Path,
    content: str,
) -> None:
    """Coordination parsing requires a title and complete first JSON section."""
    store, _ = _store(tmp_path)

    with pytest.raises(ReviewExchangeError):
        store.publish_atomic(store.paths.coordination, content)


def test_coordination_read_reports_missing_and_unreadable_paths(tmp_path: Path) -> None:
    """Required and unreadable coordination states have stable diagnostics."""
    missing, _ = _store(tmp_path / "missing")
    assert missing.read_coordination() is None
    with pytest.raises(ReviewExchangeError, match="coordination record does not exist"):
        missing.read_coordination(required=True)

    unreadable, _ = _store(tmp_path / "unreadable")
    unreadable.paths.coordination.parent.mkdir(parents=True, exist_ok=True)
    unreadable.paths.coordination.mkdir()
    with pytest.raises(ReviewExchangeError, match="cannot read coordination record"):
        unreadable.read_coordination()


def test_append_rejects_missing_transcript_coordination_and_offset(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Append prerequisites fail before changing transcript history."""
    store, context = _store(tmp_path)
    record = _record(context)
    with pytest.raises(ReviewExchangeError, match="must be initialized"):
        store.append_transcript_once(
            record,
            transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            entry=_entry(),
        )

    store.initialize_transcript(context)

    def no_coordination(*, required: bool = False) -> None:
        del required

    monkeypatch.setattr(store, "read_coordination", no_coordination)
    with pytest.raises(ReviewExchangeError, match="coordination record does not exist"):
        store.append_transcript_once(
            record,
            transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            entry=_entry(),
        )

    def return_record(*, required: bool = False) -> CoordinationRecord:
        del required
        return record

    def marker_without_offset(
        stored: CoordinationRecord,
        requested: CoordinationRecord,
        transition: IncompleteTransitionKind,
        entry_id: str,
    ) -> CoordinationRecord:
        del stored, requested, transition, entry_id
        return record

    monkeypatch.setattr(store, "read_coordination", return_record)
    monkeypatch.setattr(
        store,
        "_ensure_transcript_marker",
        marker_without_offset,
    )
    with pytest.raises(ReviewExchangeError, match="no byte offset"):
        store.append_transcript_once(
            record,
            transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            entry=_entry(),
        )


def test_append_rejects_stale_coordination_and_another_pending_marker(
    tmp_path: Path,
) -> None:
    """Only the persisted current entry may own suffix repair."""
    stale_store, stale_context = _store(tmp_path / "stale")
    stale_record = _record(stale_context)
    stale_store.initialize_transcript(stale_context)
    stale_store.write_coordination(stale_record)
    with pytest.raises(ReviewExchangeError, match="stale coordination"):
        stale_store.append_transcript_once(
            replace(stale_record, no_progress_streak=1),
            transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            entry=_entry(),
        )

    marked_store, marked_context = _store(tmp_path / "marked")
    marked_store.initialize_transcript(marked_context)
    marked = replace(
        _record(marked_context),
        incomplete_transition=IncompleteTransitionKind.HUMAN_RESOLUTION,
        transcript_entry_id="another-entry",
        transcript_offset=0,
    )
    marked_store.write_coordination(marked)
    with pytest.raises(ReviewExchangeError, match="another transcript repair"):
        marked_store.append_transcript_once(
            marked,
            transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            entry=_entry(),
        )


def test_archive_reports_existing_destination_and_move_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Archiving never overwrites evidence and reports a failed exact move."""
    existing, existing_context = _store(tmp_path / "existing")
    existing.publish_atomic(
        existing.paths.request,
        _artifact(existing_context, ReviewRole.REQUESTOR),
    )
    destination = archive_path(
        existing.paths,
        "20260804-103000",
        ArchiveKind.REQUEST,
    )
    destination.write_text("existing archive\n", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match="archive already exists"):
        existing.archive_evidence(ArchiveKind.REQUEST, "20260804-103000")

    failed, failed_context = _store(tmp_path / "failed")
    failed.publish_atomic(
        failed.paths.request,
        _artifact(failed_context, ReviewRole.REQUESTOR),
    )
    original_replace = Path.replace

    def fail_archive(source: Path, target: Path) -> Path:
        if source == failed.paths.request:
            message = "injected archive failure"
            raise OSError(message)
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_archive)
    with pytest.raises(ReviewExchangeError, match="evidence archive failed"):
        failed.archive_evidence(ArchiveKind.REQUEST, "20260804-103000")
    assert failed.paths.request.is_file()


def test_low_level_io_failures_preserve_prepared_and_transcript_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Permanent replace, preparation, suffix-read, and truncation errors surface."""
    store, context = _store(tmp_path)
    content = _artifact(context, ReviewRole.REQUESTOR)
    replace_attempts = 0

    def deny_replace(source: Path, target: Path) -> Path:
        nonlocal replace_attempts
        del source, target
        replace_attempts += 1
        message = "injected permanent sharing denial"
        raise PermissionError(message)

    def no_sleep(_seconds: float) -> None:
        """Keep the permanent-failure test below the duration floor."""

    monkeypatch.setattr(Path, "replace", deny_replace)
    monkeypatch.setattr(store_module.time, "sleep", no_sleep)
    with pytest.raises(ReviewExchangeError, match="atomic publication failed"):
        store.publish_atomic(store.paths.request, content)
    assert replace_attempts == _ATOMIC_REPLACE_ATTEMPTS

    monkeypatch.undo()

    def fail_fsync(descriptor: int) -> None:
        del descriptor
        message = "injected prepare synchronization failure"
        raise OSError(message)

    monkeypatch.setattr(store_module.os, "fsync", fail_fsync)
    with pytest.raises(OSError, match="prepare synchronization failure"):
        store._prepare_atomic(store.paths.request, b"prepared")
    assert not tuple(store.paths.request.parent.glob(".review-exchange-*.tmp"))

    with pytest.raises(ReviewExchangeError, match="cannot read transcript suffix"):
        store._read_suffix(store.paths.transcript, 0)
    with pytest.raises(ReviewExchangeError, match="cannot truncate transcript suffix"):
        store._truncate_transcript(0)


def test_context_validation_rejects_identity_and_parent_mismatch(tmp_path: Path) -> None:
    """Coordination context must retain both exact identity and document parent."""
    store, context = _store(tmp_path)
    other_identity = ExchangeIdentity(ReviewFamily.CODE, "code", _VERSION, "other")
    other_document = tmp_path / "docs" / f"plan.{_VERSION}.other.md"
    other_document.write_text("# Other\n", encoding="utf-8")
    wrong_identity = ReviewContext(other_identity, other_document, None, "2")
    with pytest.raises(ReviewExchangeError, match="identity does not match"):
        store._validate_context(wrong_identity)

    wrong_parent = _context(tmp_path, parent="elsewhere")
    assert wrong_parent.identity == context.identity
    with pytest.raises(ReviewExchangeError, match="differs from transcript parent"):
        store._validate_context(wrong_parent)


def test_posix_lock_adapter_acquires_and_releases_one_file_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The non-Windows standard-library adapter uses exclusive flock calls."""
    calls: list[tuple[int, int]] = []

    class FakeFcntl:
        LOCK_EX = 1
        LOCK_UN = 2

        @staticmethod
        def flock(descriptor: int, operation: int) -> None:
            calls.append((descriptor, operation))

    with (tmp_path / "posix.lock").open("w+b") as stream:
        monkeypatch.setattr(ownership_store_module.os, "name", "posix")
        monkeypatch.setattr(
            ownership_store_module,
            "fcntl",
            FakeFcntl,
            raising=False,
        )

        ownership_store_module.ReviewExchangeOwnershipStore._lock_stream(stream)
        ownership_store_module.ReviewExchangeOwnershipStore._unlock_stream(stream)

    assert [operation for _, operation in calls] == [
        FakeFcntl.LOCK_EX,
        FakeFcntl.LOCK_UN,
    ]
    assert calls[0][0] == calls[1][0]


# eof
