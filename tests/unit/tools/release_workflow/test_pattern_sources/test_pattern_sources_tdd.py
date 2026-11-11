"""Pattern sources: one capture on the CRLF-to-LF view, mapped back to the bytes.

Step 3 of v0.14.0 version-sources: the umbrella's `^APP_SERVICE_VERSION=(.+)$`
captures no carriage return on a CRLF file, and replacing the mapped span
keeps every line ending. A byte-order mark, accented letters and a non-BMP
character before the match shift the byte span correctly. Zero or two
matches, an empty capture, a missing file, invalid UTF-8 and a value malformed
for its form fail with status 2, naming the source. Two pattern sources of one
file compose from one original. Only the project root carries pattern sources.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    BOM,
    RootSettings,
    declare_pattern,
    lines_file,
    load_counts,
    write_file,
)
from tools.release_workflow.sources import pattern
from tools.release_workflow.sources.model import (
    Detection,
    FileView,
    Form,
    SourceError,
    compose,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.sources.model import PatternDeclaration

_PREFLIGHT = 2
_SNAPSHOT = "0.14.0-SNAPSHOT"


def _detect(root: Path, *declarations: PatternDeclaration) -> Detection:
    """Detect the declared pattern sources at the project root with a fresh view."""
    return pattern.ADAPTER.detect(root, FileView(), RootSettings(root, declarations))


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_umbrella_pattern_keeps_line_endings(tmp_path: Path, newline: str) -> None:
    """The capture holds no carriage return, and replacing it changes only the value bytes."""
    content = lines_file(["A=1", f"APP_SERVICE_VERSION={_SNAPSHOT}", "B=2"], newline=newline)
    path = write_file(tmp_path, ".env", content)
    source, = _detect(tmp_path, declare_pattern(tmp_path)).sources
    assert (source.path, source.field, source.adapter, source.form, source.value, source.root) == (
        path, "source:cicd-env", "pattern", Form.SNAPSHOT, _SNAPSHOT, tmp_path)
    span, = source.spans
    assert content[span.start:span.end] == _SNAPSHOT.encode()
    assert compose(content, [(span, pattern.ADAPTER.render(source, "0.14.0"))]) == content.replace(_SNAPSHOT.encode(), b"0.14.0")


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
@pytest.mark.parametrize("bom", [False, True])
def test_bom_accents_and_non_bmp_text_shift_the_byte_span(tmp_path: Path, newline: str, *, bom: bool) -> None:
    """Multi-byte characters and the mark before the match are counted in bytes."""
    content = lines_file(["# Été à Noël \U0001f600", "  ", f"APP_SERVICE_VERSION={_SNAPSHOT}"], newline=newline, bom=bom)
    write_file(tmp_path, ".env", content)
    span, = _detect(tmp_path, declare_pattern(tmp_path)).sources[0].spans
    assert content[span.start:span.end] == _SNAPSHOT.encode()
    assert content.startswith(BOM) == bom


def test_two_pattern_sources_of_one_file_compose_from_one_original(tmp_path: Path) -> None:
    """Disjoint captures of one file are replaced together; the file is read once."""
    content = lines_file(["API=0.13.0", "WEB=0.13.0-SNAPSHOT"], newline="\r\n")
    path = write_file(tmp_path, "deploy.env", content)
    view = FileView()
    declarations = (declare_pattern(tmp_path, "api", "deploy.env", r"^API=(.+)$", Form.CORE),
                    declare_pattern(tmp_path, "web", "deploy.env", r"^WEB=(.+)$"))
    api, web = pattern.ADAPTER.detect(tmp_path, view, RootSettings(tmp_path, declarations)).sources
    assert (api.field, api.value, api.form, web.field, web.value) == ("source:api", "0.13.0", Form.CORE, "source:web", "0.13.0-SNAPSHOT")
    edits = [(api.spans[0], b"0.14.0"), (web.spans[0], b"0.14.0-SNAPSHOT")]
    assert compose(content, edits) == lines_file(["API=0.14.0", "WEB=0.14.0-SNAPSHOT"], newline="\r\n")
    assert load_counts(view, path) == (1,)


@pytest.mark.parametrize(("lines", "expression", "form", "message"), [
    (["OTHER=1"], r"^APP_SERVICE_VERSION=(.+)$", Form.SNAPSHOT, "matches nothing"),
    (["APP_SERVICE_VERSION=0.14.0", "APP_SERVICE_VERSION=0.14.0"], r"^APP_SERVICE_VERSION=(.+)$", Form.SNAPSHOT, "matches more than once"),
    (["APP_SERVICE_VERSION="], r"^APP_SERVICE_VERSION=(.+)?$", Form.SNAPSHOT, "captures an empty value"),
    (["APP_SERVICE_VERSION="], r"^APP_SERVICE_VERSION=(.*)$", Form.SNAPSHOT, "captures an empty value"),
    (["APP_SERVICE_VERSION=v0.14.0"], r"^APP_SERVICE_VERSION=(.+)$", Form.SNAPSHOT, r"'v0\.14\.0'.*MAJOR\.MINOR\.PATCH"),
    ([f"APP_SERVICE_VERSION={_SNAPSHOT}"], r"^APP_SERVICE_VERSION=(.+)$", Form.CORE, "form core takes a release value"),
])
def test_unusable_matches_fail_naming_the_source(tmp_path: Path, lines: list[str], expression: str, form: Form, message: str) -> None:
    """Zero or several matches, an empty capture and a malformed value fail with status 2."""
    write_file(tmp_path, ".env", lines_file(lines))
    with pytest.raises(SourceError, match=message) as caught:
        _detect(tmp_path, declare_pattern(tmp_path, pattern=expression, form=form))
    assert caught.value.exit_code == _PREFLIGHT
    assert r"[source:cicd-env]" in str(caught.value)


@pytest.mark.parametrize(("content", "message"), [(None, r"does not exist.*never created"), (b"V=\xff\n", "UTF-8")])
def test_missing_or_undecodable_file_fails_and_creates_nothing(tmp_path: Path, content: bytes | None, message: str) -> None:
    """A declared file is never created, and it must be UTF-8."""
    if content is not None:
        write_file(tmp_path, ".env", content)
    before = sorted(tmp_path.iterdir())
    with pytest.raises(SourceError, match=message) as caught:
        _detect(tmp_path, declare_pattern(tmp_path))
    assert caught.value.exit_code == _PREFLIGHT
    assert r"[source:cicd-env]" in str(caught.value)
    assert sorted(tmp_path.iterdir()) == before


def test_component_roots_carry_no_pattern_source(tmp_path: Path) -> None:
    """A pattern source belongs to the project, so another root yields nothing and reads nothing."""
    view = FileView()
    assert pattern.ADAPTER.detect(tmp_path / "frontend", view, RootSettings(tmp_path, (declare_pattern(tmp_path),))) == Detection()
    assert load_counts(view, tmp_path / ".env") == (0,)


def test_pattern_adapter_surface() -> None:
    """Every form is allowed, none is the default, and no file is an undeclared candidate."""
    adapter = pattern.ADAPTER
    assert (adapter.name, adapter.default_form, adapter.forms, adapter.manifest_names) == ("pattern", None, frozenset(Form), frozenset())
    assert not adapter.has_project_version("package.json", b'{"version": "1.0.0"}')


# eof
