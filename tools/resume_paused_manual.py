"""Record a manual receiver's first observation of a bulk-routable pause."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from tools.resume_paused_artifacts import (
    PromptState,
    RoutingState,
    read_checkout_snapshot,
)
from tools.resume_paused_delivery_model import GuardState
from tools.resume_paused_evidence import DuplicateEvidence, DuplicateSignal
from tools.resume_paused_models import (
    ArtifactError,
    SessionRole,
    checked_timestamp,
    pane_id,
)
from tools.resume_paused_profiles import Host, as_mapping, loads_strict

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_delivery_model import GuardPort

COMMANDS = ("resume-session", "review-resume", "review-resume requestor", "review-resume reviewer")


def _path(snapshot: CheckoutSnapshot) -> Path:
    """Scope an attempt to the same validated artifact home and bytes as dispatch."""
    if snapshot.home is None or snapshot.prompt is None:
        raise ArtifactError("manual-prompt-unavailable")  # noqa: EM101
    return snapshot.home / f"a.resume-paused.{snapshot.prompt.digest.value}.manual.local.json"


def manual_evidence(snapshot: CheckoutSnapshot) -> DuplicateEvidence | None:
    """Read the first counted attempt, including one whose pane has since closed."""
    try:
        record = as_mapping(loads_strict(_path(snapshot).read_text(encoding="utf-8")))
        command, pane = record["command"], record["pane"]
        host = Host(str(record["host"]))
        at = datetime.fromisoformat(checked_timestamp(record["at"], "manual attempt"))
        source = pane_id(pane, "manual pane") if pane is not None else None
    except FileNotFoundError:
        return None
    except (KeyError, ValueError, OSError, RecursionError) as error:
        raise ArtifactError("manual-attempt-unreadable") from error  # noqa: EM101
    if command not in COMMANDS:
        raise ArtifactError("manual-attempt-unreadable")  # noqa: EM101
    routing = snapshot.routing.routing if snapshot.routing else None
    if command == "review-resume" and routing and routing.pause.session_role is not SessionRole.REVIEWER:
        raise ArtifactError("manual-review-role-uncertain")  # noqa: EM101
    return DuplicateEvidence(DuplicateSignal.COMMAND, source, f"{command} ({host.value})", at)


def record_attempt(snapshot: CheckoutSnapshot, command: str, host: Host, pane: str | None, guard: GuardPort) -> str:
    """Publish before consent or reconciliation. Only bulk-eligible prompt states need a fence."""
    routing = snapshot.routing
    if snapshot.state not in {PromptState.UNUSED, PromptState.NEW_SINCE_USE} or not routing or routing.state is not RoutingState.RESOLVED:
        return "no routable unused prompt"
    if command == "review-resume reviewer" and routing.routing and routing.routing.pause.session_role is not SessionRole.REVIEWER:
        return "reviewer-only continuation"
    path = _path(snapshot)
    record = {
        "at": datetime.now(UTC).isoformat(timespec="seconds"), "command": command,
        "host": host.value, "pane": pane_id(pane, "manual pane") if pane else None,
    }
    with guard.acquire(snapshot.root) as lease:
        if lease.state is not GuardState.ACQUIRED:
            reason = f"manual-resume-guard-{lease.state.value}"
            raise ArtifactError(reason)
        try:
            with path.open("x", encoding="utf-8") as stream:
                json.dump(record, stream)
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            pass  # The existing attempt already fences bulk delivery of these bytes.
    return path.name


def main(argv: Sequence[str] | None = None) -> int:
    """Register an unmarked receiver without recording consent, consumption or a review claim."""
    # The guard uses msvcrt. Reading evidence is also supported outside the Windows receiver.
    from tools.resume_paused_guard import CheckoutGuard  # noqa: PLC0415

    parser = argparse.ArgumentParser()
    parser.add_argument("--command", choices=COMMANDS, required=True)
    parser.add_argument("--host", choices=tuple(Host), required=True)
    args = parser.parse_args(argv)
    try:
        result = record_attempt(read_checkout_snapshot(Path.cwd()), args.command, Host(args.host), os.environ.get("TUIOS_PANE_ID"), CheckoutGuard())
    except (ArtifactError, OSError) as error:
        sys.stderr.write(f"{error}\n")
        return 1
    sys.stdout.write(f"{result}\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


# eof
