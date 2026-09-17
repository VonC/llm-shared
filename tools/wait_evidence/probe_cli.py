"""Standalone entry point for human-operated synthetic native-wake experiments.

Commands never start a model conversation. Operator markers measure normal end
only; the durable harness has no CLI command that fabricates host gate evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from . import claude_monitor
from .claude_observer import observe_claude
from .models import JsonObject, number_value, object_value, reject, text_value
from .probe_driver import Experiment
from .probe_observer import observe, record
from .prototype import Prototype, Route

if TYPE_CHECKING:
    from collections.abc import Sequence


def read_object(path: Path) -> JsonObject:
    """Read one explicit JSON input without host or repository discovery."""
    return object_value(json.loads(path.read_text(encoding="utf-8")))


def parser() -> argparse.ArgumentParser:
    """Expose explicit paths and exact identities for the operator procedure."""
    result = argparse.ArgumentParser(description="Durable synthetic native-wake prototype; human-started trials only")
    commands = result.add_subparsers(dest="command", required=True)
    freeze = commands.add_parser("freeze", help="Freeze complete draft blobs and fixed initial series settings")
    freeze.add_argument("--directory", type=Path, required=True)
    freeze.add_argument("--repository", type=Path, required=True)
    freeze.add_argument("--commit", required=True)
    freeze.add_argument("--settings", type=Path, required=True)
    prepare = commands.add_parser("prepare", help="Record READY, reserve identities and publish the prompt last")
    prepare.add_argument("--directory", type=Path, required=True)
    prepare.add_argument("--request", type=Path, required=True)
    observer = commands.add_parser("observe", help="Run the independent finite collector and native route")
    observer.add_argument("--directory", type=Path, required=True)
    observer.add_argument("--registering-turn", default="")
    observer.add_argument("--codex-executable", type=Path)
    marker = commands.add_parser("mark", help="Record an externally verified measurement with its native evidence reference")
    marker.add_argument("--directory", type=Path, required=True)
    marker.add_argument("--measurement", type=Path, required=True)
    for name in ("register", "source", "mark-normal-end", "status", "consume", "suppress",
                 "claude-bridge", "claude-confirm", "claude-consume"):
        command = commands.add_parser(name)
        command.add_argument("--directory", type=Path, required=True)
        if name == "consume":
            command.add_argument("--event", required=True)
            command.add_argument("--thread", required=True)
        if name == "suppress":
            command.add_argument("--reason", choices=["stop", "cancel", "interrupted", "closed", "stale", "bridge-failed"],
                                 required=True)
    return result


def register(directory: Path) -> Prototype:
    """Start the source from the measured registration action, after manifest creation."""
    return claude_monitor.register(directory)


def source(prototype: Prototype) -> JsonObject:
    """Wait once in ordinary code, emit one outcome and exit; never poll a model."""
    state = prototype.snapshot()
    if state.get("baseline") is True:
        reject("Unchanged-source baselines cannot release the source")
    remaining = number_value(state, "due_at") - time.time()
    if remaining > 0:
        time.sleep(remaining)
    prototype.advance(time.time(), Route("unavailable", lambda: "unavailable", lambda _: None))
    return prototype.snapshot()


def main(argv: Sequence[str] | None = None) -> int:
    """Execute one bounded driver action, or the explicitly requested source timer."""
    args = parser().parse_args(argv)
    if args.command == "freeze":
        series = Experiment.freeze(args.directory, args.repository, args.commit, read_object(args.settings))
        sys.stdout.write(str(series.directory / "seed-prompt.txt") + "\n")
    elif args.command == "prepare":
        directory = Experiment(args.directory).prepare(read_object(args.request), time.time())
        sys.stdout.write(str(directory / "benchmark.txt") + "\n")
    elif args.command == "observe":
        _observe(args)
    elif args.command == "claude-bridge":
        claude_monitor.bridge(args.directory)
    elif args.command in {"claude-confirm", "claude-consume"}:
        action = claude_monitor.confirm if args.command == "claude-confirm" else claude_monitor.consume
        sys.stdout.write(json.dumps(action(args.directory)) + "\n")
    elif args.command == "mark":
        _mark(args)
    else:
        sys.stdout.write(json.dumps(_state_command(args)) + "\n")
    return 0


def _observe(args: argparse.Namespace) -> None:
    if read_object(args.directory / "manifest.json")["host"] == "claude":
        observe_claude(args.directory)
        return
    if not args.registering_turn:
        reject("Codex observation requires the exact registering turn")
    observe(args.directory, args.registering_turn, args.codex_executable)


def _mark(args: argparse.Namespace) -> None:
    measurement = read_object(args.measurement)
    data = object_value(measurement.get("data"))
    text_value(data, "evidence")
    kind = text_value(measurement, "kind")
    if kind not in {"benchmark_prompt", "pending_return", "useful_continuation", "final_turn_end"}:
        reject("Only prompt/pending/useful/final measurements can be marked")
    record(args.directory, kind, number_value(measurement, "at"), data)


def _state_command(args: argparse.Namespace) -> JsonObject:
    prototype = register(args.directory) if args.command == "register" else Prototype(args.directory)
    if args.command == "mark-normal-end":
        at = time.time()
        prototype.mark_normal_end(at)
        record(args.directory, "normal_turn_end", at, {"origin": "operator-measurement-only"})
    elif args.command == "suppress":
        prototype.suppress(args.reason, time.time())
    elif args.command == "consume":
        at = time.time()
        consumed = prototype.consume(args.event, args.thread, at)
        record(args.directory, "consumption", at, {"logical_id": args.event, "accepted": consumed})
        return {"consumed": consumed}
    elif args.command == "source":
        return source(prototype)
    return prototype.snapshot()


# eof
