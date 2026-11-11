"""The `version.txt` anchor: its first line, its notes and its token span.

Step 2 of v0.14.0 version-sources: the token, optionally followed by
whitespace, `--` and a title, is the whole first line; anything else is
malformed. A missing file, invalid UTF-8 or a malformed first line fails with
status 2 and a remedy and creates nothing. Replacing the token bytes keeps the
title, the notes, the byte-order mark and every line ending.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    BOM,
    RootSettings,
    load_counts,
    version_txt,
    write_version_txt,
)
from tools.release_workflow.sources import anchor
from tools.release_workflow.sources.model import (
    Detection,
    FileView,
    Form,
    SourceError,
    Span,
    VersionError,
    compose,
)

if TYPE_CHECKING:
    from pathlib import Path

_PREFLIGHT = 2


@pytest.mark.parametrize(("first_line", "title"), [
    ("0.14.0", ""), ("0.14.0 -- Title", "Title"), ("0.14.0   --   Title", "Title"), ("0.14.0 --", ""),
    ("0.14.0-SNAPSHOT\t--\tÉté 2026", "Été 2026"),
])
def test_first_line_token_and_title(first_line: str, title: str) -> None:
    """The token comes first; whitespace, `--` and the title are optional together."""
    document = anchor.parse_document(version_txt(first_line, "Notes\n"))
    assert (str(document.token), document.title, document.notes) == (first_line.split(maxsplit=1)[0], title, "Notes\n")


@pytest.mark.parametrize("first_line", ["0.14.0 Title", "0.14.0 -SNAPSHOT", "", "0.14.0 ", "-- Title"])
def test_malformed_first_line(first_line: str) -> None:
    """Text after the token that is not `--` and a title makes the anchor malformed."""
    with pytest.raises(SourceError, match="malformed") as caught:
        anchor.parse_document(version_txt(first_line))
    assert caught.value.exit_code == _PREFLIGHT
    assert "0.14.0 -- Title" in str(caught.value)


def test_invalid_token_names_the_grammar() -> None:
    """A first line whose token breaks the grammar fails with the token remedy."""
    with pytest.raises(VersionError, match=r"MAJOR\.MINOR\.PATCH"):
        anchor.parse_document(version_txt("v0.14.0 -- Title"))


def test_notes_are_returned_unchanged() -> None:
    """Everything after the first line terminator is the notes, byte for byte."""
    notes = "Key changes:\n\n- one\n  - nested\n\ttab\n"
    assert anchor.parse_document(version_txt("0.14.0 -- T", notes)).notes == notes
    assert anchor.parse_document(b"0.14.0").notes == ""


@pytest.mark.parametrize(("newline", "bom"), [("\n", False), ("\r\n", False), ("\n", True), ("\r\n", True)])
def test_token_replacement_keeps_every_other_byte(newline: str, *, bom: bool) -> None:
    """LF, CRLF and byte-order-mark documents change only in the token bytes."""
    content = version_txt("0.14.0-SNAPSHOT -- Titre", "Notes é\n\nfin\n", newline=newline, bom=bom)
    document = anchor.parse_document(content)
    start = len(BOM) if bom else 0
    assert (document.token_span, document.bom) == (Span(start, start + len("0.14.0-SNAPSHOT")), BOM if bom else b"")
    replaced = compose(content, [(document.token_span, b"0.14.0")])
    assert replaced == content.replace(b"0.14.0-SNAPSHOT", b"0.14.0", 1)
    reread = anchor.parse_document(replaced)
    assert (str(reread.token), reread.title, reread.notes, reread.bom) == ("0.14.0", document.title, document.notes, document.bom)


def test_detect_locates_the_project_root_anchor(tmp_path: Path) -> None:
    """The anchor source carries its value, token span, form and root, read once."""
    path = write_version_txt(tmp_path, version_txt("0.14.0-SNAPSHOT -- Title"))
    view = FileView()
    detection = anchor.ADAPTER.detect(tmp_path, view, RootSettings(tmp_path))
    source, = detection.sources
    assert (source.path, source.field, source.adapter, source.form, source.value) == (path, "version", "anchor", Form.SNAPSHOT, "0.14.0-SNAPSHOT")
    assert (source.spans, source.root, source.manifest, detection.visible) == ((Span(0, 15),), tmp_path, None, ())
    assert load_counts(view, path) == (1,)
    assert anchor.ADAPTER.render(source, "0.14.0") == b"0.14.0"


def test_detect_ignores_other_roots(tmp_path: Path) -> None:
    """A `version.txt` below the project root is not a source."""
    component = tmp_path / "component"
    write_version_txt(component, version_txt())
    assert anchor.ADAPTER.detect(component, FileView(), RootSettings(tmp_path)) == Detection()


@pytest.mark.parametrize(("content", "message"), [
    (None, r"version\.txt does not exist.*0\.14\.0 -- Title"),
    (b"0.14.0 -- \xff\n", r"version\.txt.*UTF-8"),
    (b"0.14.0 Title\n", r"version\.txt.*malformed"),
    (b"0.14 -- Title\n", r"version\.txt.*MAJOR\.MINOR\.PATCH"),
])
def test_detect_failures_name_the_file_and_create_nothing(content: bytes | None, message: str, tmp_path: Path) -> None:
    """Missing, undecodable and malformed anchors fail with status 2 and leave the root as it was."""
    if content is not None:
        write_version_txt(tmp_path, content)
    before = sorted(tmp_path.iterdir())
    with pytest.raises(SourceError, match=message) as caught:
        anchor.ADAPTER.detect(tmp_path, FileView(), RootSettings(tmp_path))
    assert caught.value.exit_code == _PREFLIGHT
    assert sorted(tmp_path.iterdir()) == before


def test_anchor_adapter_surface() -> None:
    """The anchor accepts no configured form and reports no undeclared candidate."""
    adapter = anchor.ADAPTER
    assert (adapter.name, adapter.default_form, adapter.forms, adapter.manifest_names) == ("anchor", Form.SNAPSHOT, frozenset(), frozenset())
    assert not adapter.has_project_version("version.txt", b"0.14.0\n")


# eof
