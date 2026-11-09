"""Declared pattern sources: one capture on a CRLF-to-LF view of a project file.

Step 3 of v0.14.0 version-sources. A pattern source belongs to the project,
so it is located only at the project root. Its declared file must exist and
is never created; it is decoded as strict UTF-8, keeping a byte-order mark.
The compiled expression runs with `re.MULTILINE` over a view of the text in
which each CRLF reads as LF (design decision Q09), so the umbrella's `(.+)$`
captures no carriage return on a CRLF file. It must match exactly once, with a
nonempty capture that is a version token valid for the source's form. The
capture is mapped back to the original characters, then to bytes, so a
replacement keeps every line ending. The adapter never writes.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass
from itertools import islice
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
    to_byte_spans,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.sources.model import (
        AdapterSettings,
        FileView,
        PatternDeclaration,
    )

_CRLF = "\r\n"


@dataclass(frozen=True)
class LfView:
    """Text in which each CRLF reads as LF, with the view offsets of those line feeds."""

    text: str
    collapsed: tuple[int, ...]

    def original_offset(self, offset: int) -> int:
        """Map a view offset to the original text, adding one per collapsed line feed before it.

        A view offset at a collapsed line feed maps to its carriage return, so
        a capture ending at a line end stops before the CRLF, never inside it.
        """
        return offset + bisect.bisect_left(self.collapsed, offset)


def lf_view(text: str) -> LfView:
    """Read each CRLF as LF in one pass, recording where each such line feed lands in the view."""
    collapsed: list[int] = []
    index = text.find(_CRLF)
    while index >= 0:
        collapsed.append(index - len(collapsed))
        index = text.find(_CRLF, index + len(_CRLF))
    return LfView(text.replace(_CRLF, "\n"), tuple(collapsed))


def _capture(declaration: PatternDeclaration, text: str, label: str) -> tuple[int, int, str]:
    """Return the view span and text of the one nonempty capture of the expression."""
    expression = declaration.expression.pattern
    matches = list(islice(declaration.expression.finditer(text), 2))
    if not matches:
        msg = f"{label}: pattern {expression!r} matches nothing; correct the pattern or the file"
        raise SourceError(msg)
    if len(matches) > 1:
        msg = f"{label}: pattern {expression!r} matches more than once; make it match exactly one value"
        raise SourceError(msg)
    match, = matches
    start, end = match.span(1)
    if start == end:
        msg = f"{label}: pattern {expression!r} captures an empty value; make its group capture the version"
        raise SourceError(msg)
    return start, end, match[1]


def _check_form(value: str, form: Form, label: str) -> None:
    """Require a version token, without the suffix unless the form is `snapshot`."""
    try:
        token = VersionToken.parse(value)
    except VersionError as exc:
        msg = f"{label}: captured value {value!r} is malformed: {exc}"
        raise SourceError(msg) from exc
    if token.snapshot and form is not Form.SNAPSHOT:
        msg = f"{label}: captured value {value!r} is malformed: form {form} takes a release value such as {token.core}"
        raise SourceError(msg)


@dataclass(frozen=True)
class PatternAdapter:
    """Locate each declared pattern source at the project root and render its raw text."""

    name: str = "pattern"
    default_form: Form | None = None
    forms: frozenset[Form] = frozenset(Form)
    manifest_names: frozenset[str] = frozenset()

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Return the declared pattern sources at the project root; other roots have none."""
        if root != settings.project_root:
            return Detection()
        return Detection(tuple(self._locate(declaration, root, view) for declaration in settings.patterns))

    def _locate(self, declaration: PatternDeclaration, root: Path, view: FileView) -> LocatedSource:
        """Match the declaration once on the LF view and map its capture to original bytes."""
        label = f"[source:{declaration.name}] {declaration.path}"
        content = view.read(declaration.path)
        if content is None:
            msg = f"{label} does not exist: a pattern source file is never created; create it or correct file"
            raise SourceError(msg)
        try:
            text, bom = decode_utf8(content, str(declaration.path))
        except SourceError as exc:
            msg = f"[source:{declaration.name}] {exc}"
            raise SourceError(msg) from exc
        view_text = lf_view(text)
        start, end, value = _capture(declaration, view_text.text, label)
        _check_form(value, declaration.form, label)
        spans = to_byte_spans(text, len(bom), [Span(view_text.original_offset(start), view_text.original_offset(end))])
        return LocatedSource(declaration.path, f"source:{declaration.name}", self.name, declaration.form, value, spans, root)

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the value's raw text bytes; the capture holds nothing but the value."""
        del source
        return value.encode("utf-8")

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Report no candidate: a pattern source is declared, never discovered."""
        del name, content
        return False


ADAPTER = PatternAdapter()


# eof
