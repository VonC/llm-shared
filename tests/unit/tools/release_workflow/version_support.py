"""Byte builders for version sources and helpers for read-once file views.

Step 2 of v0.14.0 version-sources starts this module with `version.txt`
documents in LF, CRLF and byte-order-mark variants, settings naming the
project root and a load-count helper; later steps add the ecosystem files.
Nothing here starts a process or interprets a version.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.sources.model import FileView

BOM = b"\xef\xbb\xbf"


@dataclass(frozen=True)
class RootSettings:
    """Adapter settings that only name the project root."""

    project_root: Path


def version_txt(first_line: str = "0.14.0", notes: str = "", *, newline: str = "\n", bom: bool = False) -> bytes:
    """Build a `version.txt` document; `notes` uses LF, converted to `newline`."""
    text = first_line + newline + notes.replace("\n", newline)
    return (BOM if bom else b"") + text.encode("utf-8")


def write_version_txt(root: Path, content: bytes) -> Path:
    """Write the anchor document at a project root and return its path."""
    root.mkdir(parents=True, exist_ok=True)
    path = root / "version.txt"
    path.write_bytes(content)
    return path


def load_counts(view: FileView, *paths: Path) -> tuple[int, ...]:
    """Return how many times the view loaded each path."""
    return tuple(view.loads(path) for path in paths)


# eof
