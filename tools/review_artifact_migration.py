"""Bounded check and journaled migration for review runtime artifacts.

Step 1 scans only the root, default home, and configured home. It fingerprints
recognized candidates once, blocks every ambiguity before movement, and uses a
strict atomically replaced JSON snapshot for rollback and crash recovery.
"""

# ruff: noqa: EM101, EM102, S607, TRY003

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_journal import write_journal
from tools.review_artifact_registry import (
    RegisteredArtifact,
    RegisteredArtifactKind,
    ReviewArtifactLocator,
    ReviewArtifactRegistry,
)
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Sequence

_JOURNAL_VERSION: Final = 1
_PHASES: Final = frozenset({"prepared", "moving", "committed"})


class MigrationState(StrEnum):
    """Typed placement outcomes returned by the bounded preflight."""

    READY = "ready"
    MIGRATION_REQUIRED = "migration-required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class MigrationMove:
    """One validated source-to-target action with immutable fingerprint."""

    source: Path
    target: Path
    fingerprint: str
    duplicate: bool = False


@dataclass(frozen=True)
class MigrationCheckResult:
    """Complete bounded placement result used by migration and callers."""

    state: MigrationState
    configuration: ReviewArtifactConfiguration
    inspected_locations: tuple[Path, ...]
    moves: tuple[MigrationMove, ...]
    diagnostics: tuple[str, ...]
    home_exists: bool


def _enumerate_directory(location: Path) -> tuple[str, ...]:
    """Read one directory non-recursively and return stable candidate names."""
    if not location.exists():
        return ()
    if not location.is_dir():
        raise ReviewExchangeError(f"artifact location is not a directory: {location}")
    return tuple(path.name for path in location.iterdir())


def _replace(source: Path, target: Path) -> None:
    """Atomically rename one file on its current volume."""
    source.replace(target)


def _unlink(path: Path) -> None:
    """Remove one exact migrated source or journal."""
    path.unlink(missing_ok=True)


def _git_ignore_checker(root: Path, paths: Sequence[Path]) -> bool:
    """Verify all prospective home paths through one NUL-delimited Git query."""
    relative = tuple(path.relative_to(root).as_posix() for path in paths)
    payload = "".join(f"{path}\0" for path in relative)
    completed = subprocess.run(
        ["git", "check-ignore", "-z", "--stdin"],
        cwd=root,
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        raise OSError(
            f"git check-ignore failed (exit={completed.returncode}): {completed.stderr.strip()}",
        )
    matched = {value for value in completed.stdout.split("\0") if value}
    return all(value in matched for value in relative)


class ReviewArtifactMigration:
    """Check, migrate, roll back, and recover one repository artifact layout."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        project_root: Path,
        load_configuration: Callable[[], ReviewArtifactConfiguration | Path] | None = None,
        enumerate_directory: Callable[[Path], tuple[str, ...]] = _enumerate_directory,
        parse_candidate: Callable[[str], object | None] | None = None,
        project_status: Callable[[], object] | None = None,
        read_bytes: Callable[[Path], bytes] = Path.read_bytes,
        replace: Callable[[Path, Path], None] = _replace,
        unlink: Callable[[Path], None] = _unlink,
        ignore_checker: Callable[[Path, Sequence[Path]], bool] | None = None,
    ) -> None:
        """Bind explicit filesystem ports while excluding full status projection."""
        self.project_root = project_root.resolve()
        self._load_configuration = load_configuration or (
            lambda: ReviewArtifactConfiguration.load(self.project_root)
        )
        self._enumerate_directory = enumerate_directory
        registry = ReviewArtifactRegistry()
        self._parse_candidate = parse_candidate or registry.parse_name
        self._read_bytes = read_bytes
        self._replace = replace
        self._unlink = unlink
        self._ignore_checker = ignore_checker or self._default_ignore_checker
        del project_status

    def _default_ignore_checker(
        self,
        _home: Path,
        paths: Sequence[Path],
    ) -> bool:
        """Verify prospective paths against the bound repository's Git rules."""
        return _git_ignore_checker(self.project_root, paths)

    @property
    def journal_path(self) -> Path:
        """Return the one known-path journal inside the configured home."""
        return self._journal_path(self._configuration())

    @staticmethod
    def _journal_path(configuration: ReviewArtifactConfiguration) -> Path:
        """Derive the journal without reloading an invocation's configuration."""
        return ReviewArtifactLocator(configuration).fixed_path(
            RegisteredArtifactKind.MIGRATION_JOURNAL,
        )

    def _configuration(self) -> ReviewArtifactConfiguration:
        """Normalize the production configuration or the Step 0 path spy."""
        loaded = self._load_configuration()
        if isinstance(loaded, ReviewArtifactConfiguration):
            return loaded
        home = loaded.resolve()
        relative = home.relative_to(self.project_root).as_posix()
        return ReviewArtifactConfiguration(
            self.project_root,
            home,
            relative,
            declared=True,
        )

    def migration_check(self) -> MigrationCheckResult:
        """Inspect three bounded locations without status projection or recursion."""
        configuration = self._configuration()
        locations = self._inspection_locations(configuration)
        diagnostics: list[str] = []
        moves: list[MigrationMove] = []
        planned: dict[Path, str] = {}
        self._inspect_existing_home(configuration, diagnostics)
        if self._journal_path(configuration).exists():
            diagnostics.append("migration journal requires recovery")
        for location in locations:
            self._inspect_location(
                location,
                configuration,
                planned,
                moves,
                diagnostics,
            )
        self._inspect_ignore_coverage(configuration, moves, diagnostics)
        state = self._state_for(moves, diagnostics)
        return MigrationCheckResult(
            state,
            configuration,
            locations,
            tuple(moves),
            tuple(diagnostics),
            configuration.home.exists(),
        )

    def _inspection_locations(
        self,
        configuration: ReviewArtifactConfiguration,
    ) -> tuple[Path, ...]:
        """Return the bounded, de-duplicated location set in stable order."""
        return tuple(
            dict.fromkeys(
                (
                    self.project_root,
                    self.project_root / ".reviews",
                    configuration.home,
                ),
            ),
        )

    @staticmethod
    def _inspect_existing_home(
        configuration: ReviewArtifactConfiguration,
        diagnostics: list[str],
    ) -> None:
        """Validate an existing home without repairing its ignore contract."""
        if not configuration.home.exists():
            return
        try:
            configuration.prepare_home()
        except ReviewExchangeError as error:
            diagnostics.append(str(error))

    def _inspect_location(
        self,
        location: Path,
        configuration: ReviewArtifactConfiguration,
        planned: dict[Path, str],
        moves: list[MigrationMove],
        diagnostics: list[str],
    ) -> None:
        """Inspect one flat directory and append recognized migration actions."""
        try:
            names = self._enumerate_directory(location)
        except (OSError, ReviewExchangeError) as error:
            diagnostics.append(str(error))
            return
        for name in names:
            parsed = self._parse_candidate(name)
            if not isinstance(parsed, RegisteredArtifact) or location == configuration.home:
                continue
            move = self._candidate_move(
                location / name,
                configuration.home / name,
                planned,
                diagnostics,
            )
            if move is not None:
                moves.append(move)

    def _candidate_move(
        self,
        source: Path,
        target: Path,
        planned: dict[Path, str],
        diagnostics: list[str],
    ) -> MigrationMove | None:
        """Validate one source and resolve target collision semantics."""
        fingerprint = self._candidate_fingerprint(source, diagnostics)
        if fingerprint is None:
            return None
        expected = planned.get(target)
        if expected is not None:
            return self._planned_duplicate(source, target, fingerprint, expected, diagnostics)
        if target.exists():
            return self._existing_duplicate(source, target, fingerprint, planned, diagnostics)
        planned[target] = fingerprint
        return MigrationMove(source, target, fingerprint)

    def _candidate_fingerprint(
        self,
        source: Path,
        diagnostics: list[str],
    ) -> str | None:
        """Fingerprint one regular non-link source or record its damage."""
        if source.is_symlink() or not source.is_file():
            diagnostics.append(f"damaged review artifact {source}: not a regular file")
            return None
        try:
            return self._fingerprint(source)
        except OSError as error:
            diagnostics.append(f"damaged review artifact {source}: {error}")
            return None

    @staticmethod
    def _planned_duplicate(
        source: Path,
        target: Path,
        fingerprint: str,
        expected: str,
        diagnostics: list[str],
    ) -> MigrationMove | None:
        """Accept an identical earlier source or diagnose an ambiguous duplicate."""
        if expected == fingerprint:
            return MigrationMove(source, target, fingerprint, duplicate=True)
        diagnostics.append(
            f"duplicate review artifact has different bytes: {target.name}",
        )
        return None

    def _existing_duplicate(
        self,
        source: Path,
        target: Path,
        fingerprint: str,
        planned: dict[Path, str],
        diagnostics: list[str],
    ) -> MigrationMove | None:
        """Accept an identical existing target or diagnose a collision."""
        try:
            target_fingerprint = self._fingerprint(target)
        except OSError as error:
            diagnostics.append(f"cannot inspect migration target {target}: {error}")
            return None
        if target_fingerprint != fingerprint:
            diagnostics.append(f"migration target has different bytes: {target.name}")
            return None
        planned[target] = target_fingerprint
        return MigrationMove(source, target, fingerprint, duplicate=True)

    def _inspect_ignore_coverage(
        self,
        configuration: ReviewArtifactConfiguration,
        moves: list[MigrationMove],
        diagnostics: list[str],
    ) -> None:
        """Validate effective coverage when the destination already exists."""
        if not configuration.home.exists():
            return
        prospective = (configuration.ignore_path, *(move.target for move in moves))
        if not self._ignore_checker(configuration.home, prospective):
            diagnostics.append(
                f"artifact home ignore coverage is ineffective: {configuration.home}",
            )

    @staticmethod
    def _state_for(
        moves: list[MigrationMove],
        diagnostics: list[str],
    ) -> MigrationState:
        """Project one typed state from complete bounded findings."""
        if diagnostics:
            return MigrationState.BLOCKED
        if moves:
            return MigrationState.MIGRATION_REQUIRED
        return MigrationState.READY

    def migrate(
        self,
        checked: MigrationCheckResult | None = None,
    ) -> MigrationCheckResult:
        """Apply one fresh migration-required result or return an existing ready state."""
        with self._migration_lock():
            fresh = self._fresh_migration(checked)
            if fresh.state is MigrationState.READY:
                return fresh
            configuration = fresh.configuration
            created = configuration.prepare_home()
            try:
                self._require_migration_ignore(configuration, fresh.moves)
                self._execute_migration(configuration, fresh.moves)
            except OSError as error:
                if created:
                    configuration.rollback_prepared_home()
                raise ReviewExchangeError(f"migration failed and was rolled back: {error}") from error
        return self.migration_check()

    def _fresh_migration(
        self,
        checked: MigrationCheckResult | None,
    ) -> MigrationCheckResult:
        """Require a fresh unblocked migration result."""
        fresh = self.migration_check()
        if fresh.state is MigrationState.BLOCKED:
            detail = "; ".join(fresh.diagnostics)
            raise ReviewExchangeError(f"migration is blocked: {detail}")
        if checked is not None and checked.moves != fresh.moves:
            raise ReviewExchangeError("migration check is stale")
        return fresh

    def _require_migration_ignore(
        self,
        configuration: ReviewArtifactConfiguration,
        moves: tuple[MigrationMove, ...],
    ) -> None:
        """Require effective ignore coverage for every prospective destination."""
        prospective = (
            configuration.ignore_path,
            self._journal_path(configuration),
            *(move.target for move in moves),
        )
        if not self._ignore_checker(configuration.home, prospective):
            raise OSError("artifact home ignore coverage is ineffective")

    def _execute_migration(
        self,
        configuration: ReviewArtifactConfiguration,
        moves: tuple[MigrationMove, ...],
    ) -> None:
        """Journal, move, verify, commit, and clean one transaction."""
        journal_path = self._journal_path(configuration)
        self._write_journal(
            journal_path,
            self._journal_payload("prepared", moves, set()),
        )
        completed: set[int] = set()
        try:
            self._move_all(moves, completed, journal_path)
            self._verify_targets(moves)
            self._write_journal(
                journal_path,
                self._journal_payload("committed", moves, completed),
            )
        except OSError:
            self._rollback(moves, journal_path)
            raise
        try:
            self._clean_duplicate_sources(moves)
            self._unlink(journal_path)
        except OSError as error:
            raise ReviewExchangeError(
                f"migration committed; recovery is required: {error}",
            ) from error

    def _move_all(
        self,
        moves: tuple[MigrationMove, ...],
        completed: set[int],
        journal_path: Path,
    ) -> None:
        """Move every non-duplicate source and snapshot each completion."""
        for index, move in enumerate(moves):
            if not move.duplicate:
                move.target.parent.mkdir(parents=True, exist_ok=True)
                self._replace(move.source, move.target)
            completed.add(index)
            self._write_journal(
                journal_path,
                self._journal_payload("moving", moves, completed),
            )

    def _verify_targets(self, moves: tuple[MigrationMove, ...]) -> None:
        """Require exact target fingerprints before committing cleanup."""
        for move in moves:
            if self._fingerprint(move.target) != move.fingerprint:
                raise OSError(f"target fingerprint differs: {move.target}")

    def _clean_duplicate_sources(self, moves: tuple[MigrationMove, ...]) -> None:
        """Remove identical sources only after the committed snapshot exists."""
        for move in moves:
            if move.duplicate:
                self._unlink(move.source)

    def recover(self) -> MigrationCheckResult:
        """Rollback an uncommitted journal or finish committed source cleanup."""
        configuration = self._configuration()
        journal_path = self._journal_path(configuration)
        payload = self._read_journal(journal_path)
        phase = cast("str", payload["phase"])
        moves = self._moves_from_journal(payload)
        try:
            if phase == "committed":
                self._verify_committed_recovery(moves)
                self._clean_all_sources(moves)
                self._unlink(journal_path)
            else:
                self._rollback(moves, journal_path)
        except OSError as error:
            raise ReviewExchangeError(f"migration recovery failed: {error}") from error
        return self.migration_check()

    def _verify_committed_recovery(self, moves: tuple[MigrationMove, ...]) -> None:
        """Require every committed target before finishing source cleanup."""
        for move in moves:
            if not move.target.is_file() or self._fingerprint(move.target) != move.fingerprint:
                raise OSError(f"committed target is invalid: {move.target}")

    def _clean_all_sources(self, moves: tuple[MigrationMove, ...]) -> None:
        """Finish idempotent source cleanup for one committed transaction."""
        for move in moves:
            self._unlink(move.source)

    def _fingerprint(self, path: Path) -> str:
        """Return one SHA-256 digest for exact byte-preservation checks."""
        return hashlib.sha256(self._read_bytes(path)).hexdigest()

    def _journal_payload(
        self,
        phase: str,
        moves: Sequence[MigrationMove],
        completed: set[int],
    ) -> dict[str, object]:
        """Render the complete strict journal snapshot for one phase."""
        return {
            "version": _JOURNAL_VERSION,
            "phase": phase,
            "moves": [
                {
                    "source": move.source.relative_to(self.project_root).as_posix(),
                    "target": move.target.relative_to(self.project_root).as_posix(),
                    "fingerprint": move.fingerprint,
                    "duplicate": move.duplicate,
                    "completed": index in completed,
                }
                for index, move in enumerate(moves)
            ],
        }

    def _write_journal(self, path: Path, payload: dict[str, object]) -> None:
        """Atomically replace the one complete JSON journal snapshot."""
        write_journal(path, payload)

    def _read_journal(self, path: Path) -> dict[str, object]:
        """Parse and validate the strict versioned journal envelope."""
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ReviewExchangeError(f"invalid migration journal: {error}") from error
        if not isinstance(payload, dict):
            raise ReviewExchangeError("invalid migration journal: unexpected fields")
        journal = cast("dict[str, object]", payload)
        if set(journal) != {"version", "phase", "moves"}:
            raise ReviewExchangeError("invalid migration journal: unexpected fields")
        if journal["version"] != _JOURNAL_VERSION or journal["phase"] not in _PHASES:
            raise ReviewExchangeError("invalid migration journal: unsupported version or phase")
        if not isinstance(journal["moves"], list):
            raise ReviewExchangeError("invalid migration journal: moves must be a list")
        return journal

    def _moves_from_journal(self, payload: dict[str, object]) -> tuple[MigrationMove, ...]:
        """Validate every journal move and restore repository-bound paths."""
        moves: list[MigrationMove] = []
        for raw in cast("list[object]", payload["moves"]):
            if not isinstance(raw, dict):
                raise ReviewExchangeError("invalid migration journal: malformed move")
            move_payload = cast("dict[str, object]", raw)
            if set(move_payload) != {
                "source", "target", "fingerprint", "duplicate", "completed",
            }:
                raise ReviewExchangeError("invalid migration journal: malformed move")
            if not all(
                isinstance(move_payload[key], expected)
                for key, expected in (
                    ("source", str),
                    ("target", str),
                    ("fingerprint", str),
                    ("duplicate", bool),
                    ("completed", bool),
                )
            ):
                raise ReviewExchangeError("invalid migration journal: malformed move value")
            source = (
                self.project_root / cast("str", move_payload["source"])
            ).resolve()
            target = (
                self.project_root / cast("str", move_payload["target"])
            ).resolve()
            try:
                source.relative_to(self.project_root)
                target.relative_to(self.project_root)
            except ValueError as error:
                raise ReviewExchangeError("invalid migration journal: path escapes root") from error
            moves.append(
                MigrationMove(
                    source,
                    target,
                    cast("str", move_payload["fingerprint"]),
                    cast("bool", move_payload["duplicate"]),
                ),
            )
        return tuple(moves)

    def _rollback(self, moves: Sequence[MigrationMove], journal_path: Path) -> None:
        """Restore every physically moved source, including unsnapshotted renames."""
        for move in reversed(moves):
            if move.duplicate:
                continue
            source_exists = move.source.exists()
            target_exists = move.target.exists()
            if source_exists and not target_exists:
                continue
            if not source_exists and target_exists:
                if self._fingerprint(move.target) != move.fingerprint:
                    raise OSError(f"rollback target fingerprint differs: {move.target}")
                self._replace(move.target, move.source)
                continue
            raise OSError(f"rollback paths are ambiguous: {move.source}, {move.target}")
        self._unlink(journal_path)

    @contextmanager
    def _migration_lock(self) -> Generator[None]:
        """Hold one repository-scoped exclusive creation lock for migration."""
        parent = self.project_root / ".git"
        if not parent.is_dir():
            parent = self.project_root
        lock = parent / "review-artifact-migration.lock"
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as error:
            raise ReviewExchangeError("artifact migration is already running") from error
        os.close(descriptor)
        try:
            yield
        finally:
            lock.unlink(missing_ok=True)


__all__ = [
    "MigrationCheckResult",
    "MigrationMove",
    "MigrationState",
    "ReviewArtifactMigration",
]


# eof
