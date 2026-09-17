"""SQLite adapter for durable wait records and atomic acknowledgements.

The caller owns the service singleton lock before opening this adapter. Only an
absent file is initialized. Known stores use rollback journaling and FULL sync;
failures retain the database for explicit recovery instead of resetting it.
"""

# ruff: noqa: EM101 - WaitError's first argument is a typed machine code.

from __future__ import annotations

import sqlite3
from contextlib import contextmanager, suppress
from dataclasses import asdict
from hashlib import sha256
from json import dumps, loads
from typing import TYPE_CHECKING, Self
from uuid import uuid4

from tools.wait_service.models import (
    MAX_TEXT,
    Cancellation,
    Capability,
    Continuation,
    DeadlinePolicy,
    Delivery,
    Event,
    HostBinding,
    NormalEnd,
    Observation,
    Outcome,
    Recipient,
    Registration,
    SourceIdentity,
    WaitError,
    WaitIntent,
    require,
    utc,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from pathlib import Path

SCHEMA_VERSION = 1
HISTORY_LIMIT = 32
SCHEMA = (
    "CREATE TABLE sources (source_key TEXT PRIMARY KEY, identity_json TEXT NOT NULL, observation_json TEXT, access_loss_utc REAL)",
    "CREATE TABLE registrations (wait_id TEXT PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE, intent_digest TEXT NOT NULL, intent_json TEXT NOT NULL, source_key TEXT NOT NULL REFERENCES sources(source_key), recipient_key TEXT NOT NULL, state TEXT NOT NULL, created_utc REAL NOT NULL, deadline_utc REAL, diagnostic TEXT NOT NULL DEFAULT '')",
    "CREATE INDEX registrations_source ON registrations(source_key)",
    "CREATE INDEX registrations_recipient ON registrations(recipient_key)",
    "CREATE INDEX registrations_deadline ON registrations(state, deadline_utc)",
    "CREATE TABLE bindings (wait_id TEXT PRIMARY KEY REFERENCES registrations(wait_id), binding_json TEXT NOT NULL)",
    "CREATE TABLE events (event_id TEXT PRIMARY KEY, wait_id TEXT NOT NULL UNIQUE REFERENCES registrations(wait_id), outcome_json TEXT NOT NULL, created_utc REAL NOT NULL)",
    "CREATE TABLE deliveries (event_id TEXT PRIMARY KEY REFERENCES events(event_id), state TEXT NOT NULL, epoch INTEGER NOT NULL, next_eligible_utc REAL, delivery_json TEXT NOT NULL)",
    "CREATE INDEX deliveries_due ON deliveries(state, next_eligible_utc)",
    "CREATE TABLE cancellations (wait_id TEXT PRIMARY KEY REFERENCES registrations(wait_id), cancelled_utc REAL NOT NULL, origin TEXT NOT NULL, decision TEXT NOT NULL)",
    "CREATE TABLE consumption_attempts (attempt_id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES events(event_id), recipient_json TEXT NOT NULL, authority_generation TEXT NOT NULL, decision TEXT NOT NULL, consumption_id TEXT, workflow_receipt TEXT NOT NULL DEFAULT '', execution_state TEXT NOT NULL DEFAULT '', settled_utc REAL, abandonment_reason TEXT NOT NULL DEFAULT '', abandonment_utc REAL, reconciliation_pending INTEGER NOT NULL DEFAULT 0, superseded INTEGER NOT NULL DEFAULT 0)",
    "CREATE INDEX consumption_event ON consumption_attempts(event_id, decision, superseded)",
    "CREATE INDEX consumption_identity ON consumption_attempts(consumption_id)",
    "CREATE TABLE history (sequence INTEGER PRIMARY KEY, wait_id TEXT NOT NULL REFERENCES registrations(wait_id), recorded_utc REAL NOT NULL, code TEXT NOT NULL, detail TEXT NOT NULL)",
    "CREATE INDEX history_wait ON history(wait_id, sequence)",
    "CREATE TABLE tombstones (wait_id TEXT PRIMARY KEY, event_id TEXT UNIQUE, idempotency_key TEXT NOT NULL UNIQUE, intent_digest TEXT NOT NULL, state TEXT NOT NULL, created_utc REAL NOT NULL, cancellation_decision TEXT NOT NULL, consumption_id TEXT, disposition TEXT NOT NULL)",
)


def _connect(location: str) -> sqlite3.Connection:
    return sqlite3.connect(location, uri=True, isolation_level=None, timeout=1.0)


def _encode(value: SourceIdentity | Recipient | WaitIntent | HostBinding | Observation | Outcome | Delivery) -> str:
    return dumps(asdict(value), ensure_ascii=True, separators=(",", ":"))


def _identity(value: SourceIdentity | Recipient) -> str:
    return sha256(_encode(value).encode("utf-8")).hexdigest()


def _intent(value: str) -> WaitIntent:
    data = loads(value)
    data["source"] = SourceIdentity(**data["source"])
    data["recipient"] = Recipient(**data["recipient"])
    data["deadline"] = DeadlinePolicy(**data["deadline"])
    data["continuation"] = Continuation(data["continuation"])
    return WaitIntent(**data)


def _registration(row: sqlite3.Row) -> Registration:
    return Registration(row["wait_id"], _intent(row["intent_json"]), row["state"], row["created_utc"], row["diagnostic"])


class WaitStore:
    """Single-writer adapter; all mutation acknowledgements follow commit.

    Transactions are a persistence-only seam for subsequent consumption operations.
    No source, host or workflow port may be called inside this boundary.
    """

    def __init__(self, path: Path, *, connect: Callable[[str], sqlite3.Connection] = _connect) -> None:
        """Open a known store or initialize only an exclusively created file."""
        self._connection: sqlite3.Connection | None = None
        try:
            try:
                with path.open("xb"):
                    pass
                created = True
            except FileExistsError:
                created = False
            self._connection = connect(f"{path.resolve().as_uri()}?mode=rw")
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            if not created:
                self._check_schema(self._connection)
            self._durability(self._connection)
            if created:
                with self.transaction() as transaction:
                    for statement in SCHEMA:
                        transaction.execute(statement)
                    transaction.execute("PRAGMA user_version = 1")
        except (OSError, sqlite3.Error, WaitError) as error:
            self.close()
            if isinstance(error, WaitError):
                raise
            raise WaitError("storage-unavailable", str(error)) from error

    @staticmethod
    def _check_schema(connection: sqlite3.Connection) -> None:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version != SCHEMA_VERSION:
            raise WaitError("schema-incompatible", f"version {version}")
        actual = {row[0] for row in connection.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL")}
        if actual != set(SCHEMA):
            raise WaitError("schema-incompatible", "schema shape differs")

    @staticmethod
    def _durability(connection: sqlite3.Connection) -> None:
        mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()[0]
        connection.execute("PRAGMA synchronous = FULL")
        if mode != "delete" or connection.execute("PRAGMA synchronous").fetchone()[0] != 2:  # noqa: PLR2004 - SQLite FULL level.
            raise WaitError("storage-unavailable", "durable journal settings unavailable")

    def __enter__(self) -> Self:
        """Keep the connection lifetime explicit."""
        return self

    def __exit__(self, *_exception: object) -> None:
        """Release SQLite handles without deleting durable evidence."""
        self.close()

    def close(self) -> None:
        """Close idempotently, including initialization and rollback failures."""
        if self._connection is not None:
            with suppress(sqlite3.Error):
                self._connection.close()
            self._connection = None

    def _connection_or_fail(self) -> sqlite3.Connection:
        if self._connection is None:
            raise WaitError("storage-unavailable", "store closed")
        return self._connection

    def _rollback(self, connection: sqlite3.Connection) -> None:
        try:
            connection.rollback()
        except sqlite3.Error:
            self.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection]:
        """Commit once or report unavailable; never perform external I/O here."""
        connection = self._connection_or_fail()
        if connection.in_transaction:
            raise WaitError("transaction-active", "nested transactions are forbidden")
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except sqlite3.Error as error:
            self._rollback(connection)
            raise WaitError("storage-unavailable", str(error)) from error
        except BaseException:
            self._rollback(connection)
            raise

    def _one(self, statement: str, values: tuple[str, ...]) -> sqlite3.Row | None:
        try:
            return self._connection_or_fail().execute(statement, values).fetchone()
        except sqlite3.Error as error:
            raise WaitError("storage-unavailable", str(error)) from error

    def register(self, intent: WaitIntent, created_utc: float) -> Registration:
        """Persist preparing once; an exact retry never changes its binding."""
        digest = intent.digest()
        utc(created_utc)
        with self.transaction() as transaction:
            row = self._one("SELECT * FROM registrations WHERE idempotency_key = ?", (intent.idempotency_key,))
            tombstone = None if row else self._one("SELECT * FROM tombstones WHERE idempotency_key = ?", (intent.idempotency_key,))
            existing = row or tombstone
            if existing is not None:
                if existing["intent_digest"] != digest:
                    raise WaitError("idempotency-conflict", "intent differs", existing["wait_id"])
                result = _registration(existing) if row else Registration(existing["wait_id"], intent, existing["state"], existing["created_utc"])
            else:
                source_key = _identity(intent.source)
                transaction.execute("INSERT OR IGNORE INTO sources(source_key, identity_json) VALUES (?, ?)", (source_key, _encode(intent.source)))
                result = Registration(str(uuid4()), intent, "preparing", created_utc)
                transaction.execute(
                    "INSERT INTO registrations(wait_id, idempotency_key, intent_digest, intent_json, source_key, recipient_key, state, created_utc, deadline_utc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (result.wait_id, intent.idempotency_key, digest, _encode(intent), source_key, _identity(intent.recipient), result.state, created_utc, intent.deadline.deadline_utc),
                )
        return result

    def get_registration(self, wait_id: str) -> Registration:
        """Look up the exact wait through its primary key."""
        row = self._one("SELECT * FROM registrations WHERE wait_id = ?", (wait_id,))
        if row is None:
            raise WaitError("wait-not-found", wait_id, wait_id)
        return _registration(row)

    def arm(self, wait_id: str, binding: HostBinding) -> Registration:
        """Commit automatic or explicitly retained acknowledgement after evidence."""
        binding.validate()
        with self.transaction() as transaction:
            registration = self.get_registration(wait_id)
            require(binding.recipient == registration.intent.recipient, "recipient mismatch")
            existing = self.get_binding(wait_id)
            if registration.state != "preparing" and existing is not None and existing != binding:
                raise WaitError("rearm-required", "binding cannot change on retry", wait_id)
            automatic = binding.capability in {Capability.STRICT, Capability.FUNCTIONAL} and binding.normal_end != NormalEnd.UNAVAILABLE
            state = "armed" if automatic else "retained" if binding.capability == Capability.RETAINED else "preparing"
            transaction.execute("INSERT INTO bindings VALUES (?, ?) ON CONFLICT(wait_id) DO UPDATE SET binding_json=excluded.binding_json", (wait_id, _encode(binding)))
            transaction.execute("UPDATE registrations SET state = ?, diagnostic = ? WHERE wait_id = ?", (state, "" if automatic else binding.capability.value, wait_id))
            result = self.get_registration(wait_id)
        return result  # noqa: RET504 - Return the acknowledgement only after commit succeeds.

    def get_binding(self, wait_id: str) -> HostBinding | None:
        """Recover the route without silently replacing its incarnation."""
        row = self._one("SELECT binding_json FROM bindings WHERE wait_id = ?", (wait_id,))
        if row is None:
            return None
        data = loads(row[0])
        data["recipient"] = Recipient(**data["recipient"])
        data["capability"] = Capability(data["capability"])
        data["normal_end"] = NormalEnd(data["normal_end"])
        return HostBinding(**data)

    def observe(self, wait_id: str, observation: Observation) -> None:
        """Retain one shared source observation and its access-loss start."""
        observation.validate()
        with self.transaction() as transaction:
            source = self.get_registration(wait_id).intent.source
            require(source.generation == observation.generation, "source generation mismatch")
            transaction.execute("UPDATE sources SET observation_json = ?, access_loss_utc = ? WHERE source_key = ?", (_encode(observation), observation.access_loss_utc, _identity(source)))

    def get_observation(self, wait_id: str) -> Observation | None:
        """Read the exact shared source via indexed registration identity."""
        row = self._one("SELECT observation_json FROM sources JOIN registrations USING(source_key) WHERE wait_id = ?", (wait_id,))
        return Observation(**loads(row[0])) if row and row[0] is not None else None

    def record_outcome(self, wait_id: str, outcome: Outcome, created_utc: float) -> Event:
        """Commit outcome and stable event together; terminal decisions stay fixed."""
        outcome.validate()
        utc(created_utc)
        with self.transaction() as transaction:
            registration = self.get_registration(wait_id)
            require(registration.intent.source.generation == outcome.observation.generation, "source generation mismatch")
            event = self.get_event(wait_id)
            if event is None:
                event = Event(str(uuid4()), wait_id, outcome, created_utc)
                transaction.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (event.event_id, wait_id, _encode(outcome), created_utc))
        return event

    def get_event(self, wait_id: str) -> Event | None:
        """Read immutable source outcome and event identity from one row."""
        row = self._one("SELECT * FROM events WHERE wait_id = ?", (wait_id,))
        if row is None:
            return None
        data = loads(row["outcome_json"])
        data["observation"] = Observation(**data["observation"])
        return Event(row["event_id"], row["wait_id"], Outcome(**data), row["created_utc"])

    def save_delivery(self, delivery: Delivery) -> None:
        """Persist retry epoch, next UTC and acceptance separately from consumption."""
        delivery.validate()
        with self.transaction() as transaction:
            transaction.execute(
                "INSERT INTO deliveries VALUES (?, ?, ?, ?, ?) ON CONFLICT(event_id) DO UPDATE SET state=excluded.state, epoch=excluded.epoch, next_eligible_utc=excluded.next_eligible_utc, delivery_json=excluded.delivery_json",
                (delivery.event_id, delivery.state, delivery.epoch, delivery.next_eligible_utc, _encode(delivery)),
            )

    def get_delivery(self, event_id: str) -> Delivery | None:
        """Recover retry state through the stable event identity."""
        row = self._one("SELECT delivery_json FROM deliveries WHERE event_id = ?", (event_id,))
        return Delivery(**loads(row[0])) if row else None

    def cancel(self, wait_id: str, cancelled_utc: float, origin: str) -> Cancellation:
        """Commit suppression while preserving source and accepted delivery facts."""
        utc(cancelled_utc)
        require(0 < len(origin) <= MAX_TEXT, "bounded cancellation origin required")
        with self.transaction() as transaction:
            self.get_registration(wait_id)
            cancellation = self.get_cancellation(wait_id)
            if cancellation is None:
                consumed = self._one("SELECT attempt_id FROM consumption_attempts JOIN events USING(event_id) WHERE wait_id = ? AND decision = 'authorized' AND superseded = 0 LIMIT 1", (wait_id,))
                decision = "already-consumed" if consumed else "suppressed"
                cancellation = Cancellation(wait_id, cancelled_utc, origin, decision)
                transaction.execute("INSERT INTO cancellations VALUES (?, ?, ?, ?)", (wait_id, cancelled_utc, origin, decision))
        return cancellation

    def get_cancellation(self, wait_id: str) -> Cancellation | None:
        """Recover the first committed suppression decision without replacing it."""
        row = self._one("SELECT * FROM cancellations WHERE wait_id = ?", (wait_id,))
        return Cancellation(**dict(row)) if row else None

    def add_history(self, wait_id: str, recorded_utc: float, code: str, detail: str) -> None:
        """Retain a bounded diagnostic tail without evicting outcomes or receipts."""
        utc(recorded_utc)
        require(0 < len(code) <= MAX_TEXT and len(detail) <= MAX_TEXT, "bounded diagnostic required")
        with self.transaction() as transaction:
            transaction.execute("INSERT INTO history(wait_id, recorded_utc, code, detail) VALUES (?, ?, ?, ?)", (wait_id, recorded_utc, code, detail))
            transaction.execute("DELETE FROM history WHERE wait_id = ? AND sequence <= (SELECT sequence FROM history WHERE wait_id = ? ORDER BY sequence DESC LIMIT 1 OFFSET ?)", (wait_id, wait_id, HISTORY_LIMIT))


# eof
