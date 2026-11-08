"""Render release outcomes on separate UTF-8/LF streams with public statuses.

Domain data stays distinct from diagnostics. Unexpected native statuses retain
their original value in diagnostics while becoming public execution failure.
Step 1 of v0.14.0 version-sources makes 3 (an incomplete restoration) public
beside 0, 1 and 2, as in ``bootstrap.main`` and both batch launchers.
"""

from __future__ import annotations

import io
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TextIO


@dataclass(frozen=True)
class OperationResult:
    """Immutable domain data, diagnostics and original operation status."""

    status: int = 0
    data: str = ""
    diagnostics: tuple[str, ...] = ()


def configure_stream(stream: TextIO) -> None:
    """Use UTF-8/LF for real streams, leaving injected text sinks intact."""
    if isinstance(stream, io.TextIOWrapper):
        stream.reconfigure(encoding="utf-8", errors="backslashreplace", newline="\n")


def render(result: OperationResult, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    """Write command data and diagnostics independently without hiding failures."""
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    configure_stream(out)
    configure_stream(err)
    out.write(result.data.replace("\r\n", "\n").replace("\r", "\n"))
    for message in result.diagnostics:
        err.write(message.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n")
    status = result.status
    if status not in {0, 1, 2, 3}:
        err.write(f"Release operation exited with native status {status}; returning 1.\n")
        status = 1
    out.flush()
    err.flush()
    return status


# eof
