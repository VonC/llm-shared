"""Exact-path persistence with delegated ownership and unlocked publication."""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import os
import re
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import (
    ArchiveKind,
    ArtifactPaths,
    IncompleteTransitionKind,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    mapping_value,
    validate_local_timestamp,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    parse_envelope_markdown,
    parse_json_markdown,
)
from tools.review_exchange_ownership_store import ReviewExchangeOwnershipStore
from tools.review_exchange_paths import archive_path

if TYPE_CHECKING:
    from contextlib import AbstractContextManager

    from tools.llm_nature import LlmNature
    from tools.review_exchange_models import Actor
    from tools.review_exchange_ownership import (
        OwnershipCapability,
        OwnershipClaim,
        OwnershipService,
    )

_TEMPLATE_ROOT: Final[Path] = Path(__file__).resolve().parents[1] / "templates"
_ENTRY_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_TRANSCRIPT_OUTCOMES: Final[frozenset[str]] = frozenset(
    {
        "request",
        "answer",
        "escalation",
        "human-confirmation",
        "human-completion",
        "human-reclaim",
        "human-resolution",
    },
)
_ENTRY_FOOTER_PREFIX: Final[str] = "<!-- review-entry-id:"
_ATOMIC_REPLACE_ATTEMPTS: Final[int] = 5
_ATOMIC_REPLACE_DELAY_SECONDS: Final[float] = 0.01


@dataclass(frozen=True)
class TranscriptEntry:
    """Complete current-round transcript content with a stable repair identity."""

    entry_id: str
    role: ReviewRole
    outcome: str
    recorded_at: str
    authored_content: str
    occurrence: int = 1

    def __post_init__(self) -> None:
        """Reject ambiguous footer data and unsupported transcript outcomes."""
        if _ENTRY_ID_RE.fullmatch(self.entry_id) is None:
            raise ReviewExchangeError("invalid transcript entry identifier")
        if self.occurrence < 1:
            raise ReviewExchangeError("transcript entry occurrence must be positive")
        if self.outcome not in _TRANSCRIPT_OUTCOMES:
            raise ReviewExchangeError(
                f"unsupported transcript outcome: {self.outcome}",
            )
        validate_local_timestamp(self.recorded_at)
        if _ENTRY_FOOTER_PREFIX in self.authored_content:
            raise ReviewExchangeError(
                "authored content contains reserved entry footer",
            )


class ReviewExchangeStore:
    """Publish fixed artifacts and delegate locked coordination persistence.

    Complete same-directory replacements and byte-offset transcript repair keep
    partial writes recoverable without owning counterpart work.
    """

    def __init__(
        self,
        paths: ArtifactPaths,
        *,
        template_root: Path | None = None,
    ) -> None:
        """Bind persistence to one already-derived exact artifact set."""
        self.paths = paths
        self._template_root = (
            template_root.resolve() if template_root is not None else _TEMPLATE_ROOT
        )
        self.ownership_store = ReviewExchangeOwnershipStore(paths)

    def transition_lock(self) -> AbstractContextManager[None]:
        """Delegate the identity-specific lock to focused ownership storage."""
        return self.ownership_store.transition_lock()

    def claim_ownership(
        self,
        record: CoordinationRecord,
        service: OwnershipService,
        actor: Actor,
        *,
        presented: OwnershipCapability | None = None,
        force: bool = False,
    ) -> OwnershipClaim:
        """Delegate one locked compare-and-swap ownership claim."""
        return self.ownership_store.claim(
            record,
            service,
            actor,
            presented=presented,
            force=force,
        )

    def publish_atomic(self, path: Path, content: str) -> None:
        """Validate and atomically create or replace one exact artifact."""
        target = self._require_exact_path(path)
        self._validate_content(target, content)
        prepared = self._prepare_atomic(target, content.encode("utf-8"))
        try:
            self._commit_prepared(prepared, target)
        except OSError as error:
            raise ReviewExchangeError(f"atomic publication failed: {error}") from error
        finally:
            self._discard_prepared(prepared)

    def publish_request(self, content: str) -> None:
        """Remove a valid stale answer before publishing a complete request."""
        self._validate_envelope(content, ReviewRole.REQUESTOR)
        prepared = self._prepare_atomic(self.paths.request, content.encode("utf-8"))
        try:
            self.remove_exact(self.paths.answer)
            self._commit_prepared(prepared, self.paths.request)
        except OSError as error:
            raise ReviewExchangeError(f"request publication failed: {error}") from error
        finally:
            self._discard_prepared(prepared)

    def publish_answer(self, content: str) -> None:
        """Consume the exact request to a tombstone before exposing its answer."""
        self._validate_envelope(content, ReviewRole.REVIEWER)
        prepared = self._prepare_atomic(self.paths.answer, content.encode("utf-8"))
        try:
            self.consume_request_to_tombstone()
            self._commit_prepared(prepared, self.paths.answer)
        except OSError as error:
            raise ReviewExchangeError(f"answer publication failed: {error}") from error
        finally:
            self._discard_prepared(prepared)

    def consume_request_to_tombstone(self) -> None:
        """Atomically rename the validated request to its stable tombstone."""
        if not self.paths.request.is_file():
            raise ReviewExchangeError("matching review request does not exist")
        if self.paths.tombstone.exists():
            raise ReviewExchangeError("matching request tombstone already exists")
        self.read_artifact(self.paths.request)
        try:
            self.paths.request.replace(self.paths.tombstone)
        except OSError as error:
            raise ReviewExchangeError(f"request consumption failed: {error}") from error

    def read_artifact(self, path: Path) -> str:
        """Read and identity-check one exact request, answer, or tombstone."""
        target = self._require_exact_path(path)
        if target not in {
            self.paths.request,
            self.paths.answer,
            self.paths.tombstone,
        }:
            raise ReviewExchangeError("path is not a review-content artifact")
        try:
            content = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ReviewExchangeError(f"cannot read review artifact: {error}") from error
        expected_role = (
            ReviewRole.REVIEWER
            if target == self.paths.answer
            else ReviewRole.REQUESTOR
        )
        self._validate_envelope(content, expected_role)
        return content

    def remove_exact(self, path: Path) -> bool:
        """Remove one matching transient after validating its identity."""
        target = self._require_exact_path(path)
        if not target.exists():
            return False
        if target in {self.paths.request, self.paths.answer, self.paths.tombstone}:
            self.read_artifact(target)
        elif target == self.paths.coordination:
            self.read_coordination(required=True)
        else:
            raise ReviewExchangeError("path is not an exact cleanup target")
        try:
            target.unlink()
        except OSError as error:
            raise ReviewExchangeError(f"exact cleanup failed: {error}") from error
        return True

    def entry_occurrence(
        self,
        entry_id: str,
        *,
        discriminator: str | None = None,
        before_offset: int | None = None,
    ) -> int:
        """Return the next occurrence for one stable transcript identity family."""
        if not self.paths.transcript.is_file():
            return 1
        content = self.paths.transcript.read_bytes()
        if before_offset is not None:
            content = content[:before_offset]
        text = content.decode("utf-8")
        suffix = (
            rf"(?:-{re.escape(discriminator)}-\d+)?"
            if discriminator is not None
            else r"(?:-\d+)?"
        )
        footer = re.compile(
            rf"{re.escape(_ENTRY_FOOTER_PREFIX)} {re.escape(entry_id)}{suffix} -->",
        )
        return len(footer.findall(text)) + 1

    def current_entry_offset(self, entry_id: str) -> int:
        """Locate the current final legacy entry without scanning authored headings."""
        content = self.paths.transcript.read_bytes()
        footer = f"{_ENTRY_FOOTER_PREFIX} {entry_id} -->".encode()
        footer_offset = content.rfind(footer)
        if footer_offset < 0 or content[footer_offset + len(footer):].strip():
            raise ReviewExchangeError("legacy transcript entry is not the final entry")
        prior_footer = content.rfind(_ENTRY_FOOTER_PREFIX.encode(), 0, footer_offset)
        heading_offset = content.find(b"\n## Round ", prior_footer, footer_offset)
        if prior_footer < 0 or heading_offset < 0:
            raise ReviewExchangeError("legacy transcript entry boundary is unavailable")
        return heading_offset

    def initialize_transcript(self, context: ReviewContext) -> bool:
        """Initialize a missing family transcript and preserve an existing one."""
        self._validate_context(context)
        if self.paths.transcript.exists():
            if not self.paths.transcript.is_file():
                raise ReviewExchangeError("transcript path is not a file")
            return False
        template_name = (
            "review-code-transcript.template.md"
            if context.identity.family is ReviewFamily.CODE
            else "review-specification-transcript.template.md"
        )
        try:
            template = Template(
                (self._template_root / template_name).read_text(encoding="utf-8"),
            )
            content = template.substitute(
                version=context.identity.version,
                exchange_identity=context.identity.key,
                reviewed_document=self._transcript_path(context.document_path),
            )
        except (KeyError, OSError, UnicodeError) as error:
            raise ReviewExchangeError(f"cannot initialize transcript: {error}") from error
        prepared = self._prepare_atomic(self.paths.transcript, content.encode("utf-8"))
        try:
            if self.paths.transcript.exists():
                return False
            self._commit_prepared(prepared, self.paths.transcript)
        except OSError as error:
            raise ReviewExchangeError(f"transcript initialization failed: {error}") from error
        finally:
            self._discard_prepared(prepared)
        return True

    def write_coordination(self, record: CoordinationRecord) -> None:
        """Delegate strict coordination persistence to ownership storage."""
        self.ownership_store.write_coordination(record)

    def read_coordination(
        self,
        *,
        required: bool = False,
    ) -> CoordinationRecord | None:
        """Delegate one exact coordination read to ownership storage."""
        return self.ownership_store.read_coordination(required=required)

    def append_transcript_once(
        self,
        record: CoordinationRecord,
        *,
        transition: IncompleteTransitionKind,
        entry: TranscriptEntry,
        clear_marker: bool = True,
    ) -> CoordinationRecord:
        """Append or repair one entry and optionally leave its marker durable.

        Step 3 lifecycle transitions can retain the marker until their
        post-append artifact cleanup and final coordination write are durable.
        Existing direct store callers keep the Step 2 behavior that clears the
        marker immediately after a complete append.
        """
        self._validate_context(record.context)
        if not self.paths.transcript.is_file():
            raise ReviewExchangeError("transcript must be initialized before append")
        stored = self.read_coordination(required=True)
        if stored is None:
            raise ReviewExchangeError("coordination record does not exist")
        marked = self._ensure_transcript_marker(
            stored,
            record,
            transition,
            entry.entry_id,
        )
        offset = marked.transcript_offset
        if offset is None:
            raise ReviewExchangeError("transcript repair marker has no byte offset")
        rendered = self._render_transcript_entry(marked, entry).encode("utf-8")
        suffix = self._read_suffix(self.paths.transcript, offset)
        if suffix != rendered:
            self._truncate_transcript(offset)
            try:
                self._append_bytes(self.paths.transcript, rendered)
            except OSError as error:
                raise ReviewExchangeError(f"transcript append failed: {error}") from error
        if not clear_marker:
            return marked
        cleared = replace(
            marked,
            incomplete_transition=None,
            transcript_entry_id=None,
            transcript_offset=None,
        )
        self.write_coordination(cleared)
        return cleared

    def archive_evidence(
        self,
        kind: ArchiveKind,
        compact_timestamp: str,
    ) -> Path:
        """Move one exact validated transient to its identity-scoped archive."""
        sources = {
            ArchiveKind.REQUEST: self.paths.request,
            ArchiveKind.ANSWER: self.paths.answer,
            ArchiveKind.CONSUMED: self.paths.tombstone,
            ArchiveKind.COORDINATION: self.paths.coordination,
        }
        source = sources[kind]
        if source == self.paths.coordination:
            self.read_coordination(required=True)
        else:
            self.read_artifact(source)
        destination = archive_path(self.paths, compact_timestamp, kind)
        if destination.exists():
            raise ReviewExchangeError(f"review archive already exists: {destination.name}")
        try:
            source.replace(destination)
        except OSError as error:
            raise ReviewExchangeError(f"evidence archive failed: {error}") from error
        return destination

    def _require_exact_path(self, path: Path) -> Path:
        """Reject any path outside this exchange's constant fixed set."""
        target = path.resolve()
        fixed = {candidate.resolve() for candidate in self.paths.fixed_paths}
        if target not in fixed:
            raise ReviewExchangeError("path is outside the exact artifact set")
        if target == self.paths.transition_lock.resolve():
            raise ReviewExchangeError("transition lock is not a content artifact")
        return target

    def _validate_content(self, target: Path, content: str) -> None:
        """Validate identity-bearing content according to its exact target."""
        if target == self.paths.transcript:
            raise ReviewExchangeError(
                "transcript is append-only: use transcript operations",
            )
        if target in {self.paths.request, self.paths.tombstone}:
            self._validate_envelope(content, ReviewRole.REQUESTOR)
        elif target == self.paths.answer:
            self._validate_envelope(content, ReviewRole.REVIEWER)
        elif target == self.paths.coordination:
            data = self._coordination_json(content)
            record = CoordinationRecord.from_dict(mapping_value(data, "coordination JSON"))
            self._validate_context(record.context)

    def _validate_envelope(self, content: str, expected_role: ReviewRole) -> None:
        """Verify artifact role and complete identity before any mutation."""
        envelope, _ = parse_envelope_markdown(content)
        if envelope.identity != self.paths.identity:
            raise ReviewExchangeError("artifact identity does not match exact path")
        if envelope.role is not expected_role:
            raise ReviewExchangeError(
                f"artifact role must be {expected_role.value}",
            )

    def _validate_context(self, context: ReviewContext) -> None:
        """Verify one context belongs to the store's exact path set."""
        if context.identity != self.paths.identity:
            raise ReviewExchangeError("coordination identity does not match exact paths")
        if context.document_path.parent != self.paths.transcript.parent:
            raise ReviewExchangeError("reviewed document differs from transcript parent")

    @staticmethod
    def _coordination_json(content: str) -> object:
        """Parse a titled coordination record with JSON as its first section."""
        data, trailing = parse_json_markdown(content)
        if trailing.strip():
            raise ReviewExchangeError("coordination record has unexpected trailing content")
        return data

    def _ensure_transcript_marker(
        self,
        stored: CoordinationRecord,
        requested: CoordinationRecord,
        transition: IncompleteTransitionKind,
        entry_id: str,
    ) -> CoordinationRecord:
        """Persist or validate the marker that owns one append repair."""
        if stored.incomplete_transition is None:
            if stored != requested:
                raise ReviewExchangeError("stale coordination record for transcript append")
            offset = self.paths.transcript.stat().st_size
            marked = replace(
                stored,
                incomplete_transition=transition,
                transcript_entry_id=entry_id,
                transcript_offset=offset,
            )
            self.write_coordination(marked)
            return marked
        if (
            stored.incomplete_transition is not transition
            or stored.transcript_entry_id != entry_id
        ):
            raise ReviewExchangeError("another transcript repair is already pending")
        return stored

    def _render_transcript_entry(
        self,
        record: CoordinationRecord,
        entry: TranscriptEntry,
    ) -> str:
        """Render one portable entry with its complete role-nature snapshot."""
        context = record.context
        umbrella = (
            self._transcript_path(context.umbrella_path)
            if context.umbrella_path is not None
            else "none"
        )
        heading = f"## Round {record.round_number} by {entry.role.value}"
        if context.implementation_step is not None:
            heading += f" - Step {context.implementation_step}"
        if entry.role is ReviewRole.HUMAN:
            # One round holds at most one request and one answer, so role and
            # round identify those headings. A human may act more than once in
            # the same round, so only that role needs its outcome to stay unique.
            heading += f" - {entry.outcome}"
        if entry.occurrence > 1:
            if entry.role is ReviewRole.HUMAN:
                # A stop-and-resume cycle can repeat the same human outcome.
                heading += f" - attempt {entry.occurrence}"
            else:
                # A completed exchange can restart at round one for the same
                # document, so request and answer headings name that exchange.
                heading += f" (exchange {entry.occurrence})"
        lines = [
            "",
            heading,
            "",
            f"- Recorded: {entry.recorded_at}",
            f"- Exchange: {context.identity.key}",
            f"- Umbrella: {umbrella}",
            f"- Reviewed document: {self._transcript_path(context.document_path)}",
            "- Requestor LLM nature: "
            + self._render_nature(record.role_natures.requestor),
            "- Reviewer LLM nature: "
            + self._render_nature(record.role_natures.reviewer),
        ]
        if context.implementation_step is not None:
            lines.append(f"- Implementation step: {context.implementation_step}")
        lines.extend(
            [
                f"- Outcome: {entry.outcome}",
                "",
                self._portable_transcript_content(entry.authored_content).rstrip("\n"),
                "",
            ],
        )
        lines.append(f"<!-- review-entry-id: {entry.entry_id} -->")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _render_nature(nature: LlmNature | None) -> str:
        """Render one nullable role nature without any host evidence detail."""
        return nature.value if nature is not None else "unrecorded"

    def _transcript_path(self, path: Path) -> str:
        """Render an in-repository transcript path without host identity."""
        try:
            return path.relative_to(self.paths.project_root).as_posix()
        except ValueError as error:
            raise ReviewExchangeError(
                "transcript path is outside the project root",
            ) from error

    def _portable_transcript_content(self, content: str) -> str:
        """Remove this repository's absolute prefix from authored evidence."""
        root = self.paths.project_root
        prefixes = (f"{root.as_posix()}/", f"{root}\\")
        portable = content
        for prefix in prefixes:
            portable = portable.replace(prefix, "")
        return portable

    @staticmethod
    def _prepare_atomic(target: Path, content: bytes) -> Path:
        """Write and synchronize one same-directory temporary file."""
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(
            prefix=".review-exchange-",
            suffix=".tmp",
            dir=target.parent,
        )
        prepared = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            prepared.unlink(missing_ok=True)
            raise
        return prepared

    @staticmethod
    def _commit_prepared(prepared: Path, target: Path) -> None:
        """Expose a prepared file with bounded transient-sharing retries."""
        for attempt in range(_ATOMIC_REPLACE_ATTEMPTS):
            try:
                prepared.replace(target)
            except PermissionError:
                if attempt + 1 == _ATOMIC_REPLACE_ATTEMPTS:
                    raise
                time.sleep(_ATOMIC_REPLACE_DELAY_SECONDS * (2**attempt))
            else:
                return

    @staticmethod
    def _discard_prepared(prepared: Path) -> None:
        """Remove an uncommitted temporary file after success or failure."""
        prepared.unlink(missing_ok=True)

    @staticmethod
    def _read_suffix(path: Path, offset: int) -> bytes:
        """Read only the current entry suffix from its persisted byte offset."""
        try:
            with path.open("rb") as stream:
                stream.seek(offset)
                return stream.read()
        except OSError as error:
            raise ReviewExchangeError(f"cannot read transcript suffix: {error}") from error

    def _truncate_transcript(self, offset: int) -> None:
        """Discard a torn current-entry suffix without loading prior history."""
        try:
            with self.paths.transcript.open("r+b") as stream:
                stream.truncate(offset)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as error:
            raise ReviewExchangeError(f"cannot truncate transcript suffix: {error}") from error

    @staticmethod
    def _append_bytes(path: Path, content: bytes) -> None:
        """Append and synchronize one already-rendered complete entry."""
        with path.open("ab") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())


# eof
