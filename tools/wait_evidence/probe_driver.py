"""Freeze complete seeds and prepare immutable, explicitly bound live trials.

The human starts and seeds each measured TUI. This ordinary-code driver reserves
fresh run/thread IDs, captures pre-prompt offsets and retains failed validation.
Indexed trial ordinals avoid scanning retained attempts on each preparation.
It never creates a model conversation or changes host configuration.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from .claude_monitor import prepare as prepare_claude
from .models import (
    JsonObject,
    TrialManifest,
    number_value,
    object_value,
    reject,
    text_value,
)
from .probe_files import save
from .prototype import run_directory
from .telemetry import Telemetry

SEEDS = ("docs/v0.13.0/draft.v0.13.0.no_polling.md", "docs/v0.13.0/draft.v0.13.0.shared-wait-service.md")
ORDER = ("A", "B-prototype", "B-prototype", "A", "A", "B-prototype")
SOURCE_SECONDS = 240
BASELINE_SECONDS = 600
CONTEXT_TOLERANCE = 0.05
COMMIT_LENGTH = 40


def git_bytes(repository: Path, revision: str) -> bytes:
    """Read one commit ID or full blob through argv without a shell."""
    command = ["git", "-C", str(repository), "show", revision] if ":" in revision else [
        "git", "-C", str(repository), "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"]
    return subprocess.run(command, check=True, capture_output=True, timeout=30).stdout  # noqa: S603 - Git argv, no shell.


def capture_stream(path: Path) -> JsonObject:
    """Capture identity and a bounded anchor at the pre-prompt end of a stream."""
    if not path.is_absolute():
        reject("Telemetry paths must be absolute")
    with path.open("rb") as stream:
        stat = os.fstat(stream.fileno())
        stream.seek(max(0, stat.st_size - 4096))
        anchor = sha256(stream.read(4096)).hexdigest()
    return {"path": str(path), "offset": stat.st_size, "file_id": [stat.st_dev, stat.st_ino],
            "anchor_sha256": anchor}


class Experiment:
    """Own a frozen series with indexed identities, pair lookup and trial order."""

    def __init__(self, directory: Path) -> None:
        """Load a selected series without searching the repository or host home."""
        self.directory = run_directory(directory)
        self.settings = object_value(json.loads((self.directory / "series.json").read_text(encoding="utf-8")))

    @classmethod
    def freeze(cls, directory: Path, repository: Path, commit: str, settings: JsonObject) -> Experiment:
        """Freeze both complete draft blobs from one commit and lock series controls."""
        directory = run_directory(directory)
        if not repository.is_absolute():
            reject("Repository must be absolute")
        for key in ("series_id", "host", "build", "schema", "model", "profile", "home"):
            text_value(settings, key)
        revision = git_bytes(repository, commit).decode("ascii").strip()
        if len(revision) != COMMIT_LENGTH or any(char not in "0123456789abcdef" for char in revision):
            reject("Git did not resolve a full commit ID")
        blobs = {name: git_bytes(repository, f"{revision}:{name}") for name in SEEDS}
        configuration = object_value(settings.get("configuration"))
        frozen: JsonObject = {**settings, "repository": str(repository), "seed_commit": revision,
                              "seed_hashes": {name: sha256(blob).hexdigest() for name, blob in blobs.items()},
                              "configuration_hash": sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest(),
                              "wake_bound": 60, "duplicate_window": 120, "drain_bound": 120,
                              "source_seconds": SOURCE_SECONDS, "baseline_seconds": BASELINE_SECONDS}
        directory.mkdir(parents=True, exist_ok=False)
        (directory / "seeds").mkdir()
        for name, blob in blobs.items():
            (directory / "seeds" / Path(name).name).write_bytes(blob)
        save(directory / "series.json", frozen)
        seed_paths = "\n".join("- " + str(directory / "seeds" / Path(name).name) for name in SEEDS)
        (directory / "seed-prompt.txt").write_text(
            "Read these two files completely and keep their contents in context for the next task:\n\n"
            + seed_paths + "\n\nDo not analyze or summarize them yet. When finished, reply exactly:\n\nREADY\n",
            encoding="utf-8")
        connection = sqlite3.connect(directory / "trials.sqlite3")
        try:
            with connection:
                connection.execute("CREATE TABLE trials (run TEXT PRIMARY KEY, thread TEXT UNIQUE, "
                                   "pair TEXT, arm TEXT, mode TEXT, context INTEGER, ordinal INTEGER)")
                connection.execute("CREATE INDEX pair_lookup ON trials(pair, mode)")
                connection.execute("CREATE INDEX trial_order ON trials(mode, ordinal)")
        finally:
            connection.close()
        return cls(directory)

    def prepare(self, request: JsonObject, now: float) -> Path:
        """Reserve a run, validate READY and capture the manifest before its prompt."""
        run = text_value(request, "run_id")
        self._validate_run(run)
        directory = self.directory / run
        directory.mkdir(exist_ok=False)
        save(directory / "request.json", request)
        try:
            self._claim_thread(request)
            data = self._manifest(request, now)
            header = {key: data[key] for key in ("schema", "host", "build", "thread", "profile", "source_id")}
            header["type"] = "probe_meta"
            events = directory / "probe-events.jsonl"
            events.write_text(json.dumps(header) + "\n", encoding="utf-8")
            streams = data["streams"]
            assert isinstance(streams, list)  # noqa: S101 - _manifest builds the list.
            streams.append({**capture_stream(events), "role": "probe"})
            manifest = TrialManifest.from_dict(data)
            self._validate_binding(manifest, now)
            self._reserve(manifest, text_value(request, "mode"))
            if data["host"] == "claude":
                prompt = prepare_claude(directory, data)
            else:
                prompt = self._prompt(directory, data)
            save(directory / "manifest.json", data)
            # The prompt is intentionally the last artifact made available.
            (directory / "benchmark.txt").write_text(prompt, encoding="utf-8")
        except (ValueError, OSError, sqlite3.Error) as error:
            save(directory / "invalid.json", {"status": "invalid", "reason": str(error), "at": now})
            raise
        return directory

    @staticmethod
    def _validate_run(run: str) -> None:
        if Path(run).name != run or run in {".", "..", "seeds"} or ":" in run or "\\" in run:
            reject("Run ID must be one directory component")

    @staticmethod
    def _validate_binding(manifest: TrialManifest, now: float) -> None:
        for event in Telemetry(manifest).read(now):
            if event.kind == "gap":
                reject("Native binding failed: " + text_value(event.data, "reason"))

    def _claim_thread(self, request: JsonObject) -> None:
        """Reserve even invalid measured attempts across series under this evidence root."""
        thread = text_value(request, "thread")
        if str(UUID(thread)) != thread:
            reject("Use an exact canonical native thread UUID")
        if thread == os.environ.get("CODEX_THREAD_ID"):
            reject("The implementing conversation cannot be a measured fresh thread")
        root = next(parent for parent in self.directory.parents if parent.name == "a.shared-wait-service")
        connection = sqlite3.connect(root / "measured-threads.sqlite3")
        try:
            with connection:
                connection.execute("CREATE TABLE IF NOT EXISTS threads (thread TEXT PRIMARY KEY, run TEXT NOT NULL)")
                try:
                    connection.execute("INSERT INTO threads VALUES (?, ?)", (thread, str(self.directory / text_value(request, "run_id"))))
                except sqlite3.IntegrityError:
                    reject("Each attempt requires a fresh thread, including repeats and new series")
        finally:
            connection.close()

    def _manifest(self, request: JsonObject, now: float) -> JsonObject:
        self._validate_ready(request, now)
        paths = request.get("streams")
        if not isinstance(paths, list) or not paths or any(not isinstance(path, str) for path in paths):
            reject("Explicit native telemetry paths are required")
        if request.get("mode") not in {"trial", "baseline"}:
            reject("Unknown trial mode")
        return {**self.settings, **{key: request[key] for key in
                ("run_id", "thread", "arm", "pair_id", "ready_at", "context_tokens", "mode")},
                "created_at": now, "source_id": str(uuid4()), "wait_id": str(uuid4()), "event_id": str(uuid4()),
                "streams": [capture_stream(Path(path)) for path in paths if isinstance(path, str)],
                "baselines": {}, "cached_input_included": True, "reasoning_included": None}

    def _validate_ready(self, request: JsonObject, now: float) -> None:
        if request.get("arm") not in {"A", "B-prototype"}:
            reject("Only A and B-prototype arms belong to this probe")
        if request.get("complete_reads") is not True or request.get("ready_marker") != "READY":
            reject("Confirm full frozen reads and READY before the manifest")
        if number_value(request, "ready_at") >= now:
            reject("READY must precede manifest creation")
        if request.get("seed_hashes") != self.settings["seed_hashes"]:
            reject("READY seed hashes differ from the frozen series")
        hashes = object_value(self.settings["seed_hashes"])
        for name in SEEDS:
            if sha256((self.directory / "seeds" / Path(name).name).read_bytes()).hexdigest() != hashes[name]:
                reject("Frozen seed bytes changed; start a new series")

    def _reserve(self, manifest: TrialManifest, mode: str) -> None:
        connection = sqlite3.connect(f"{(self.directory / 'trials.sqlite3').as_uri()}?mode=rw", uri=True)
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                ordinal = connection.execute("SELECT COALESCE(MAX(ordinal) + 1, 0) FROM trials WHERE mode='trial'").fetchone()[0]
                if mode == "trial" and manifest.arm != ORDER[ordinal % len(ORDER)]:
                    reject("Initial trial order is A/B, B/A, A/B; retain repeats in a new series")
                pair = connection.execute("SELECT context, arm FROM trials WHERE pair=? AND mode=?",
                                          (manifest.pair_id, mode)).fetchall()
                if len(pair) > 1 or (pair and pair[0][1] == manifest.arm):
                    reject("Pair already contains this arm")
                if pair and abs(manifest.context_tokens - pair[0][0]) / max(manifest.context_tokens, pair[0][0]) > CONTEXT_TOLERANCE:
                    reject("Pair context differs by more than five percent")
                connection.execute("INSERT INTO trials VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (manifest.run_id, manifest.thread, manifest.pair_id, manifest.arm, mode,
                                    manifest.context_tokens, ordinal))
        finally:
            connection.close()

    @staticmethod
    def _prompt(directory: Path, data: JsonObject) -> str:
        script = Path(__file__).resolve().parents[2] / "docs/v0.13.0/probe.shared-wait-service.py"
        instructions = (f"Synthetic native-wake benchmark. Read {directory / 'manifest.json'} and preserve its exact "
                        f"thread, source, wait and event IDs. Use the verified project Python to run {script}. "
                        f"Run register --directory {json.dumps(str(directory))} once. ")
        if data["mode"] == "baseline":
            return instructions + "End this turn normally. Leave the source unchanged for at least 600 seconds after normal end."
        if data["arm"] == "A":
            return instructions + ("Run source --directory " + json.dumps(str(directory))
                                   + " using initial yield_time_ms 1000 (or the supported minimum), then wait with "
                                   "yield_time_ms 60000 until ready. These waits are a benchmark-only exception. "
                                   "Validate identities, run consume with the event and thread IDs, then reply exactly WAIT_TEST_DONE.")
        return instructions + ("End this turn normally. The independent native route must wake this same thread automatically. "
                               "Validate the delivered identities and result; run consume with the exact IDs once, "
                               "then reply exactly WAIT_TEST_DONE. Do not nudge or replace the conversation.")


# eof
