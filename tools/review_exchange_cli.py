#!/usr/bin/env python3
"""Non-interactive command adapter for the v0.11.0 review-exchange core.

Step 3 delegates capability parsing, lifecycle typing, and token-safe ownership
stops to a focused adapter. This hub retains caller-file validation, operation
dispatch, gate-aware new-session pickup, and one stable JSON result while
staying below its risk-band target.
"""

# ruff: noqa: BLE001, EM101, EM102, TRY003

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, TextIO

from tools import find_project_root
from tools.review_artifact_configuration import (
    ReviewArtifactConfiguration,
    caller_file_parents,
)
from tools.review_exchange_cli_ownership import (
    CorePort,
    capability_from_args,
    failure_payload,
)
from tools.review_exchange_cli_parser import (
    context_from_document as _context_from_document,
)
from tools.review_exchange_cli_parser import (
    parser as _parser,
)
from tools.review_exchange_cli_result import add_issued_capability
from tools.review_exchange_cli_result import fatal_payload as _fatal_payload
from tools.review_exchange_cli_result import operation_name as _operation_name
from tools.review_exchange_cli_resume import (
    execute_resume_operation,
    is_resume_operation,
)
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactPaths,
    ArtifactState,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewExchangeError,
)
from tools.review_exchange_ownership import OwnershipRejectedError
from tools.review_exchange_paths import (
    derive_artifact_paths,
    load_review_configuration,
    validate_activation,
)
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_exchange_transcript_identity import current_request_occurrence
from tools.review_exchange_wait import WaitOutcome, WaitProgress

if TYPE_CHECKING:
    from tools.review_exchange_observer import ExchangeObservation


_STOP_STATES = frozenset(
    {
        ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS,
        ArtifactState.TRANSCRIPT_REPAIR_PENDING,
        ArtifactState.CONVERGENCE_GATE,
        ArtifactState.OWNING_ACTION_PENDING,
        ArtifactState.ESCALATED,
        ArtifactState.ABANDONED_MID_ROUND,
        ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
        ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND,
        ArtifactState.ABANDONED_REQUEST,
        ArtifactState.ABANDONED_ANSWER,
        ArtifactState.INCONSISTENT,
    },
)


@dataclass(frozen=True)
class Runtime:
    """Exact project, protocol context, paths, configuration, and core port."""

    project_root: Path
    context: ReviewContext
    paths: ArtifactPaths
    configuration: ReviewConfiguration
    core: CorePort


def _empty_extra() -> Mapping[str, Any]:
    """Return one typed empty operation payload."""
    return {}


@dataclass(frozen=True)
class OperationResult:
    """One delegated operation outcome before common JSON rendering."""

    outcome: str
    observation: ExchangeObservation | None = None
    exit_code: int | None = None
    extra: Mapping[str, Any] = field(default_factory=_empty_extra)


def _build_runtime(args: argparse.Namespace, project_root: Path) -> Runtime:
    """Construct the exact-path lifecycle facade for one invocation."""
    context = _context_from_document(
        args.family,
        args.document,
        args.umbrella,
        args.implementation_step,
    )
    policy = FamilyPolicy(
        args.convergence_signal,
        args.another_round_label,
        args.continue_owning_workflow_label,
    )
    artifacts = ReviewArtifactConfiguration.load(project_root)
    configuration = load_review_configuration(project_root, configuration=artifacts)
    paths = derive_artifact_paths(project_root, context, configuration=artifacts)
    store = ReviewExchangeStore(paths)
    core = ReviewExchangeCore(store, context, policy, configuration)
    return Runtime(project_root, context, paths, configuration, core)


def _is_effectively_ignored(project_root: Path, path: Path) -> bool:
    """Ask Git whether one caller-owned root input is effectively ignored."""
    relative = path.relative_to(project_root)
    git_executable = shutil.which("git")
    if git_executable is None:
        raise ReviewExchangeError("cannot validate ignored input: git was not found")
    try:
        result = subprocess.run(  # noqa: S603 - fixed Git command and separated paths
            [
                git_executable,
                "-C",
                str(project_root),
                "check-ignore",
                "-q",
                "--",
                str(relative),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise ReviewExchangeError(f"cannot validate ignored input: {error}") from error
    return result.returncode == 0


def _read_input_file(project_root: Path, value: str | Path, label: str) -> str:
    """Validate and read one ignored home-local ``a.*`` UTF-8 input once."""
    path = Path(value).expanduser().resolve()
    if path.parent not in caller_file_parents(project_root):
        raise ReviewExchangeError(f"{label} file must be in the review artifact home")
    if not path.name.startswith("a."):
        raise ReviewExchangeError(f"{label} file must use an a.* name")
    if not path.is_file():
        raise ReviewExchangeError(f"{label} file does not exist: {path}")
    if not _is_effectively_ignored(project_root, path):
        raise ReviewExchangeError(f"{label} file is not effectively ignored by Git")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot read {label} file as UTF-8: {error}") from error


def _progress_writer(stream: TextIO) -> Callable[[WaitProgress], None]:
    """Build a JSON-lines progress callback that writes only to stderr."""
    def report(progress: WaitProgress) -> None:
        payload = {
            "progress": {
                "elapsed_seconds": progress.elapsed_seconds,
                "remaining_seconds": progress.remaining_seconds,
                "state": progress.state.value,
            },
        }
        stream.write(f"{json.dumps(payload, sort_keys=True)}\n")
        stream.flush()

    return report


def _require_activation(runtime: Runtime) -> OperationResult | None:
    """Return a disabled stop or validate the fixed transient path set."""
    if not runtime.configuration.enabled:
        return OperationResult("disabled", exit_code=3)
    validate_activation(runtime.project_root, runtime.paths)
    return None


def _dispatch_simple(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Handle operations that need no caller-owned Markdown."""
    if args.operation == "activate":
        return OperationResult("activated")
    if args.operation == "status":
        return OperationResult("observed")
    if args.operation == "start":
        runtime.core.start()
        return OperationResult("started")
    if args.operation == "continue":
        runtime.core.continue_round()
        return OperationResult("continued")
    if args.operation == "reclaim":
        return _dispatch_reclaim(args, runtime)
    return _dispatch_complete(args, runtime)


def _dispatch_pickup(
    _args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Reissue one capability to a session that lost the plaintext token.

    A wait mints its capability in the process that observes the counterpart and
    keeps the plaintext only in memory, since coordination stores just the
    digest. A session acting after that process has exited holds nothing to
    present, and every fenced transition then reports `ownership-missing`. This
    advances the generation and hands the caller a replacement, which is the
    displacement the ownership service is built to answer. Human convergence
    remains a decision gate, but the requestor needs the replacement capability
    to record that decision and continue its authorized owning workflow.
    """
    observation = runtime.core.classify()
    record = observation.record
    if record is None:
        raise ReviewExchangeError("ownership pickup requires durable coordination")
    pickup_actor = (
        Actor.REQUESTOR
        if observation.state
        in {ArtifactState.CONVERGENCE_GATE, ArtifactState.OWNING_ACTION_PENDING}
        else record.expected_next_actor
    )
    runtime.core.pickup_ownership(pickup_actor)
    return OperationResult("ownership-picked-up")


def _dispatch_reclaim(args: argparse.Namespace, runtime: Runtime) -> OperationResult:
    """Renew one abandoned lease or perform one authorized forced resume."""
    summary_file: str | None = args.summary_file
    if args.force and summary_file is None:
        raise ReviewExchangeError("forced reclaim requires --summary-file")
    if summary_file is not None and not args.force:
        raise ReviewExchangeError("reclaim accepts --summary-file only with --force")
    if summary_file is None:
        runtime.core.reclaim()
        return OperationResult("reclaimed")
    summary = _read_input_file(runtime.project_root, summary_file, "summary")
    runtime.core.force_reclaim(summary)
    return OperationResult("force-reclaimed")


def _dispatch_complete(args: argparse.Namespace, runtime: Runtime) -> OperationResult:
    """Finish normal authorization or one human-closed abandoned round."""
    summary_file: str | None = args.summary_file
    if args.force and summary_file is None:
        raise ReviewExchangeError("forced completion requires --summary-file")
    if summary_file is not None and not args.force:
        raise ReviewExchangeError("complete accepts --summary-file only with --force")
    if summary_file is None:
        return OperationResult(
            "completed",
            extra={"removed": runtime.core.complete()},
        )
    summary = _read_input_file(runtime.project_root, summary_file, "summary")
    return OperationResult(
        "force-completed",
        extra={"removed": runtime.core.force_complete(summary)},
    )


def _dispatch_publication(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Read and delegate one request or answer publication."""
    content = _read_input_file(runtime.project_root, args.content_file, "content")
    summary = _read_input_file(runtime.project_root, args.summary_file, "summary")
    if args.operation == "publish-request":
        runtime.core.publish_request(content, summary)
    else:
        runtime.core.publish_answer(content, summary)
    return OperationResult("published")


def _dispatch_request_transcript_repair(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Repair the final pending legacy request entry through the core."""
    summary = _read_input_file(runtime.project_root, args.summary_file, "summary")
    runtime.core.repair_current_request_transcript(summary)
    return OperationResult("repaired")


def _dispatch_wait(
    args: argparse.Namespace,
    runtime: Runtime,
    stderr: TextIO,
) -> OperationResult:
    """Run one bounded request or answer wait."""
    expected = (
        ArtifactState.REQUEST_PENDING
        if args.operation == "wait-request"
        else ArtifactState.ANSWER_PENDING
    )
    result = runtime.core.wait_for_exact(
        expected,
        timeout_seconds=args.timeout_seconds,
        poll_interval=args.poll_interval,
        progress_interval=args.progress_interval,
        progress_callback=_progress_writer(stderr),
    )
    code = 0 if result.outcome is WaitOutcome.FOUND else 3
    return OperationResult(result.outcome.value, result.observation, code)


def _dispatch_consume(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Delegate one intermediate-answer assessment."""
    runtime.core.consume_answer(
        reviewed_work_changed=args.reviewed_work_changed == "true",
        disagreement=args.disagreement,
    )
    return OperationResult("consumed")


def _dispatch_recovery(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Delegate escalation, cancellation, or clear-or-archive recovery."""
    summary = _read_input_file(runtime.project_root, args.summary_file, "summary")
    if args.operation == "escalate":
        runtime.core.escalate(summary)
        return OperationResult("escalated")
    if args.operation == "cancel":
        runtime.core.cancel(summary)
        return OperationResult("cancelled")
    resolution = runtime.core.resolve_escalation(
        summary,
        archive=args.operation == "archive",
    )
    return OperationResult(
        "archived" if args.operation == "archive" else "resolved",
        extra={"archived_paths": [path.as_posix() for path in resolution.archived_paths]},
    )


def _dispatch_confirm(
    args: argparse.Namespace,
    runtime: Runtime,
    _stderr: TextIO,
) -> OperationResult:
    """Read optional guidance and delegate a human confirmation."""
    guidance = (
        None
        if args.guidance_file is None
        else _read_input_file(runtime.project_root, args.guidance_file, "guidance")
    )
    decision = runtime.core.confirm(args.choice_label, guidance=guidance)
    return OperationResult(
        decision.outcome.value,
        extra={"owning_action_authorized": decision.owning_action_authorized},
    )


OperationHandler = Callable[[argparse.Namespace, Runtime, TextIO], OperationResult]
_SIMPLE_HANDLER: OperationHandler = _dispatch_simple
_HANDLERS: dict[str, OperationHandler] = {
    "activate": _SIMPLE_HANDLER,
    "status": _SIMPLE_HANDLER,
    "start": _SIMPLE_HANDLER,
    "continue": _SIMPLE_HANDLER,
    "reclaim": _SIMPLE_HANDLER,
    "pickup": _dispatch_pickup,
    "complete": _SIMPLE_HANDLER,
    "publish-request": _dispatch_publication,
    "publish-answer": _dispatch_publication,
    "repair-request-transcript": _dispatch_request_transcript_repair,
    "wait-request": _dispatch_wait,
    "wait-answer": _dispatch_wait,
    "consume-answer": _dispatch_consume,
    "escalate": _dispatch_recovery,
    "cancel": _dispatch_recovery,
    "resolve": _dispatch_recovery,
    "archive": _dispatch_recovery,
    "confirm": _dispatch_confirm,
}


def _dispatch(
    args: argparse.Namespace,
    runtime: Runtime,
    stderr: TextIO,
) -> OperationResult:
    """Validate activation and delegate through one operation handler."""
    if args.operation == "status" and not runtime.configuration.enabled:
        return OperationResult("disabled", exit_code=3)
    if args.operation != "status":
        activation = _require_activation(runtime)
        if activation is not None:
            return activation
    handler = _HANDLERS.get(args.operation)
    if handler is None:
        raise ReviewExchangeError(f"unsupported operation: {args.operation}")
    runtime.core.present_ownership(capability_from_args(args))
    try:
        return handler(args, runtime, stderr)
    except OwnershipRejectedError as error:
        return OperationResult(
            error.failure.code,
            exit_code=3,
            extra=failure_payload(error.failure),
        )


def _paths_payload(paths: ArtifactPaths) -> dict[str, str]:
    """Render every applicable fixed path with stable keys."""
    return {
        "answer": paths.answer.as_posix(),
        "coordination": paths.coordination.as_posix(),
        "request": paths.request.as_posix(),
        "tombstone": paths.tombstone.as_posix(),
        "transcript": paths.transcript.as_posix(),
        "transition_lock": paths.transition_lock.as_posix(),
    }


def _success_payload(runtime: Runtime, operation: str, result: OperationResult) -> dict[str, Any]:
    """Build the mandatory final result from the delegated state."""
    if result.outcome == "disabled":
        state = "disabled"
        record = None
        diagnostic = "review mode is disabled"
    else:
        observation = result.observation or runtime.core.classify()
        state = observation.state.value
        record = observation.record
        diagnostic = observation.diagnostic
    payload: dict[str, Any] = {
        "diagnostic": diagnostic,
        "identity": runtime.context.identity.to_dict(),
        "operation": operation,
        "outcome": result.outcome,
        "paths": _paths_payload(runtime.paths),
        "round": record.round_number if record is not None else None,
        "state": state,
    }
    if state == ArtifactState.REQUEST_PENDING.value and record is not None:
        payload["exchange_occurrence"] = current_request_occurrence(
            ReviewExchangeStore(runtime.paths),
            runtime.context,
            record.round_number,
        )
    payload.update(result.extra)
    add_issued_capability(payload, runtime.core, operation, result.exit_code)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    """Run one operation and emit exactly one final UTF-8 JSON object."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    operation = _operation_name(arguments)
    try:
        args = _parser().parse_args(arguments)
        operation = args.operation
        project_root = find_project_root(Path.cwd()).resolve()
        if is_resume_operation(operation):
            payload, code = execute_resume_operation(args, project_root)
            sys.stdout.write(f"{json.dumps(payload, ensure_ascii=False, sort_keys=True)}\n")
            return code
        runtime = _build_runtime(args, project_root)
        result = _dispatch(args, runtime, sys.stderr)
        payload = _success_payload(runtime, operation, result)
        if result.exit_code is not None:
            code = result.exit_code
        else:
            code = 3 if payload["state"] in {state.value for state in _STOP_STATES} else 0
    except ReviewExchangeError as error:
        payload = _fatal_payload(operation, str(error))
        code = 2
    except Exception as error:
        payload = _fatal_payload(operation, str(error))
        code = 2
    sys.stdout.write(f"{json.dumps(payload, ensure_ascii=False, sort_keys=True)}\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())


# eof
