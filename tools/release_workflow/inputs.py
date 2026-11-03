"""Read explicit payload channels and identify actual Windows console stdin.

GetConsoleMode distinguishes NUL, pipes and redirected files from a console;
isatty alone cannot enforce the non-interactive input policy on Windows.
"""

from __future__ import annotations

import ctypes
import io
import sys
from ctypes import wintypes
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from pathlib import Path
    from typing import BinaryIO


class _BufferedInput(Protocol):
    """Binary input exposed by real and injected text stream wrappers."""

    buffer: BinaryIO


def _kernel() -> ctypes.WinDLL:
    """Declare pointer-width-safe stdin and console-mode signatures."""
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.GetStdHandle.argtypes = [wintypes.DWORD]
    api.GetStdHandle.restype = wintypes.HANDLE
    api.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    api.GetConsoleMode.restype = wintypes.BOOL
    return api


def stdin_is_console() -> bool:
    """Treat absent/redirected handles as non-interactive, including NUL."""
    api = _kernel()
    mode = wintypes.DWORD()
    return bool(api.GetConsoleMode(api.GetStdHandle(-10), ctypes.byref(mode)))


def read_payload(path: Path | None, *, use_stdin: bool, text: str | None,  # noqa: PLR0913 - explicit transport policy
                 source: str, required: bool, non_interactive: bool) -> str | None:
    """Read once; never implicitly consume stdin or assume missing consent."""
    try:
        if path is not None:
            return path.read_bytes().decode("utf-8")
        if use_stdin:
            stream = sys.stdin
            if isinstance(stream, io.TextIOWrapper):
                buffered = cast("_BufferedInput", stream)
                return buffered.buffer.read().decode("utf-8")
            return stream.read()
        if text is not None or not required:
            return text
        if non_interactive:
            msg = "Missing required input; supply --input-file, --input-file-env, --input-stdin or native --text"
            raise ValueError(msg)
        sys.stderr.write("Release input: ")
        sys.stderr.flush()
        return input()
    except (OSError, UnicodeError, EOFError) as exc:
        channel = f"{source} ({path})" if path is not None else "stdin"
        msg = f"Cannot read {channel}: {exc}"
        raise ValueError(msg) from exc


# eof
