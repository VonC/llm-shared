"""Parse release input and dispatch only source-owned handlers after preflight.

No plugin, configuration or environment mechanism registers handlers. Tests may
inject a registry in process; real callers always use the shipped source table.
Verified bootstrap data becomes the public runtime type without another read.
Invocation configuration loads only when the command is parsed and dispatched.

Step 1 of v0.14.0 version-sources: trailing operation tokens, such as
``set 0.14.0`` after ``versions``, parse around the options and reach the
handler's argument validator before any identity load, Git process or file
read. A handler without a validator still rejects every extra token.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

from tools.release_workflow.inputs import read_payload, stdin_is_console
from tools.release_workflow.results import OperationResult, configure_stream, render
from tools.release_workflow.runtime_identity import RuntimeIdentity

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from typing import NoReturn

    from tools.release_workflow.bootstrap import Identity
    from tools.release_workflow.invocation import InvocationContext, InvocationRequest


@dataclass(frozen=True)
class Handler:
    """A shipped operation, its required-input policy and its token validator.

    `validate_arguments` receives the trailing operation tokens right after
    parsing and raises `ValueError` to reject them (status 2). Without a
    validator, the operation takes no token.
    """

    execute: Callable[[InvocationContext], OperationResult]
    requires_input: bool = False
    validate_arguments: Callable[[tuple[str, ...]], None] | None = None


SHIPPED_HANDLERS: Mapping[str, Handler] = MappingProxyType({})


class _Parser(argparse.ArgumentParser):
    """Return parser failures through the public result boundary."""

    def error(self, message: str) -> NoReturn:
        """Raise input failure instead of terminating the host process."""
        raise ValueError(message)


class _Arguments(argparse.Namespace):
    """Typed parser destinations; repeated sources remain visible for rejection."""

    command: str
    operation: list[str]
    project_root: list[str] | None
    project_root_env: list[str] | None
    input_file: list[str] | None
    input_file_env: list[str] | None
    text: list[str] | None
    input_stdin: bool
    non_interactive: bool


def _single(values: list[str] | None, name: str) -> str | None:
    """Reject duplicate selectors even when their values happen to match."""
    if values is None:
        return None
    if len(values) != 1:
        msg = f"Conflicting repeated {name}: {values!r}"
        raise ValueError(msg)
    return values[0]


def _parse(argv: Sequence[str]) -> tuple[str, InvocationRequest]:
    """Keep parsing separate from identity, input reads and domain dispatch."""
    # Parsing loads configuration types only when an invocation needs them.
    from tools.release_workflow.invocation import InvocationRequest  # noqa: PLC0415

    parser = _Parser(prog="release", allow_abbrev=False, add_help=False)
    parser.add_argument("command")
    parser.add_argument("operation", nargs="*")
    for option in ("project-root", "project-root-env", "input-file", "input-file-env", "text"):
        parser.add_argument(f"--{option}", action="append")
    parser.add_argument("--input-stdin", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    # Options may sit before, between or after the operation tokens.
    parsed = parser.parse_intermixed_args(argv, namespace=_Arguments())
    return parsed.command, InvocationRequest(
        _single(parsed.project_root, "project root"), _single(parsed.project_root_env, "project root selector"),
        _single(parsed.input_file, "input file"), _single(parsed.input_file_env, "input file selector"),
        _single(parsed.text, "text"), parsed.input_stdin, parsed.non_interactive, tuple(parsed.operation),
    )


def _dispatch(context: InvocationContext, handler: Handler) -> OperationResult:
    """Execution exceptions never masquerade as invalid-input success paths."""
    try:
        result = handler.execute(context)
    except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001 - public operation boundary
        detail = "interrupted" if isinstance(exc, KeyboardInterrupt) else str(exc)
        return OperationResult(1, diagnostics=(*context.diagnostics, f"Release execution failed: {detail}"))
    return replace(result, diagnostics=(*context.diagnostics, *result.diagnostics))


def _select(command: str, request: InvocationRequest, entry_kind: str, registry: Mapping[str, Handler]) -> Handler:
    """Reject unshipped operations, free text and invalid tokens before reads."""
    handler = registry.get(command)
    if handler is None:
        msg = f"Release operation {command!r} is unavailable in this tooling checkout"
        raise ValueError(msg)
    if request.text is not None and entry_kind != "explicit-native":
        msg = "Batch free text requires UTF-8 file/stdin input"
        raise ValueError(msg)
    if handler.validate_arguments is not None:
        handler.validate_arguments(request.operation)
    elif request.operation:
        msg = f"Release operation {command!r} takes no arguments: {' '.join(request.operation)}"
        raise ValueError(msg)
    return handler


def main(argv: list[str], *, entry_kind: str, original_cwd: Path,  # noqa: PLR0913 - bootstrap facts and in-process seams
         tooling_root: Path | None = None, runtime: Identity | None = None,
         environment: Mapping[str, str] | None = None, handlers: Mapping[str, Handler] | None = None) -> int:
    """Normalize verified identity, freeze input, dispatch and render one outcome."""
    # Keep the import-only public surface independent of preflight dependencies.
    from tools.release_workflow.invocation import create_context  # noqa: PLC0415

    configure_stream(sys.stdout)
    configure_stream(sys.stderr)
    try:
        command, request = _parse(argv)
        registry = SHIPPED_HANDLERS if handlers is None else handlers
        handler = _select(command, request, entry_kind, registry)
        if runtime is None:
            identity = RuntimeIdentity.load(Path(__file__).resolve().parents[2] if tooling_root is None else tooling_root)
        else:
            identity = RuntimeIdentity(runtime.root, runtime.environment)
        context = create_context(
            request, runtime=identity, entry_kind=entry_kind, original_argv=tuple(argv),
            original_cwd=original_cwd, environment=dict(os.environ if environment is None else environment),
            stdin_console=stdin_is_console(),
        )
        payload = read_payload(
            context.input_file, use_stdin=request.input_stdin, text=request.text,
            source=context.input_source, required=handler.requires_input, non_interactive=context.non_interactive,
        )
        context = replace(context, payload=payload)
    except (OSError, ValueError) as exc:
        return render(OperationResult(2, diagnostics=(f"Release preflight failed: {exc}",)))
    except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001 - public operation boundary
        detail = "interrupted" if isinstance(exc, KeyboardInterrupt) else str(exc)
        return render(OperationResult(1, diagnostics=(f"Release execution failed: {detail}",)))
    return render(_dispatch(context, handler))


# eof
