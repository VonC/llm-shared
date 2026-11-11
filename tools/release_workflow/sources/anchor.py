"""The project root's `version.txt`: the anchor every other source follows.

Step 2 of v0.14.0 version-sources. The document is strict UTF-8 with an
optional byte-order mark that is kept. Its first line holds the version token,
optionally followed by whitespace, `--` and the title; anything else after the
token makes the anchor malformed. The following lines are the notes. The
document records the byte span of the token, so a transition replaces exactly
those bytes and keeps the title, the notes, the mark and every line ending.
Only the project root's `version.txt` is a source; the adapter never writes.

Step 9 adds `read_document`, the read the adapter and the `version` command
share, so both name the file and give the same remedy when it is missing or
malformed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.release_workflow.sources.model import (
    Detection,
    Form,
    LocatedSource,
    SourceError,
    Span,
    VersionError,
    VersionToken,
    decode_utf8,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.sources.model import AdapterSettings, FileView

_NAME = "version.txt"
_FIRST_LINE = re.compile(r"(?P<token>\S+)(?:[ \t]+--(?P<title>.*))?")
_EXAMPLE = "0.14.0 -- Title"


@dataclass(frozen=True)
class VersionDocument:
    """The parsed anchor: token, title, notes, the token's byte span and the mark."""

    token: VersionToken
    title: str
    notes: str
    token_span: Span
    bom: bytes


def parse_document(content: bytes) -> VersionDocument:
    """Parse a `version.txt` document, failing with a remedy on a malformed first line."""
    text, bom = decode_utf8(content, _NAME)
    first, newline, notes = text.partition("\n")
    line = first.removesuffix("\r") if newline else first
    match = _FIRST_LINE.fullmatch(line)
    if match is None:
        msg = (f"{_NAME} first line {line!r} is malformed: expected the version token, optionally followed by "
               f"whitespace, '--' and a title, such as {_EXAMPLE!r}")
        raise SourceError(msg)
    token = VersionToken.parse(match["token"])
    title = (match["title"] or "").strip()
    start = len(bom)
    return VersionDocument(token, title, notes, Span(start, start + len(match["token"])), bom)


def read_document(root: Path, view: FileView) -> VersionDocument:
    """Read and parse the root's `version.txt`, naming the file and the remedy when it is missing or malformed."""
    path = root / _NAME
    content = view.read(path)
    if content is None:
        msg = f"{path} does not exist: create it with the version token on its first line, such as {_EXAMPLE!r}"
        raise SourceError(msg)
    try:
        return parse_document(content)
    except (SourceError, VersionError) as exc:
        msg = f"{path}: {exc}"
        raise SourceError(msg) from exc


@dataclass(frozen=True)
class AnchorAdapter:
    """Locate the project root's `version.txt` and render its raw token."""

    name: str = "anchor"
    default_form: Form | None = Form.SNAPSHOT
    forms: frozenset[Form] = frozenset()
    manifest_names: frozenset[str] = frozenset()

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Return the anchor source at the project root; other roots have none."""
        if root != settings.project_root:
            return Detection()
        document = read_document(root, view)
        source = LocatedSource(root / _NAME, "version", self.name, Form.SNAPSHOT, str(document.token), (document.token_span,), root)
        return Detection((source,))

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the raw token bytes; the anchor's syntax is the token itself."""
        del source
        return value.encode("utf-8")

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Report no candidate: a nested `version.txt` is never an undeclared project."""
        del name, content
        return False


ADAPTER = AnchorAdapter()


# eof
