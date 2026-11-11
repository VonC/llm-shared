"""The TOML line scanner: owned `version` strings located by table, as spans.

Step 5 of v0.14.0 version-sources: basic and literal strings, comments and
spacing around `=` are located; a `version` key in another table, or in a
sub-table of a `[[package]]` block, is ignored, and the matching `[[package]]`
block is chosen by name among several. Lines inside a multi-line string, an
open array or an inline table never start a statement, and a header the
scanner cannot read ends the current table. Dotted `project.version` keys, an
inline `project` table and multi-line strings fail as unsupported layouts with
the remedy; so do a missing, unnamed or doubly named block and a doubled
assignment. A located text that differs from the parsed value (an escape)
fails, and accented and non-BMP characters before the value map to the right
byte span, so the edit keeps every other byte.
"""

from __future__ import annotations

import tomllib

import pytest

from tests.unit.tools.release_workflow.version_support import BOM
from tools.release_workflow.sources import toml_scan
from tools.release_workflow.sources.model import SourceError, compose

_LOCK = ('version = 1\nrevision = 3\n\n'
         '[[package]]\nname = "colorama"\nversion = "0.4.6"\nsource = { registry = "https://pypi.org/simple" }\n\n'
         '[[package]]\nversion = "0.13.0"\nname = "demo-app"\nsource = { virtual = "." }\n\n'
         '[package.metadata]\nversion = "1.0.0"\n\n'
         '[[package]]\nname = "zipp"\nversion = "3.0.0"\nsource = { registry = "https://pypi.org/simple" }\n')
_PACKAGES = _LOCK.split("\n\n", 1)[1]
_PREFLIGHT = 2
_LAYOUT = r"no single-line version assignment directly in \[project\].*write version = \"X\.Y\.Z\" on its own line"


def _located(text: str, table: str = "project", package: str | None = None) -> str:
    """Return the text the scanner locates."""
    span = toml_scan.locate(text, table, package=package)
    return text[span.start:span.end]


@pytest.mark.parametrize("line", [
    'version = "0.13.0"',
    "version = '0.13.0'",
    'version="0.13.0"',
    '  version \t=  "0.13.0"   # the release',
    "version = '0.13.0'# literal",
])
def test_basic_and_literal_strings_with_comments_and_spacing(line: str) -> None:
    """The string content is located whatever the quotes, spacing and trailing comment."""
    text = f'[project]\nname = "demo"\n{line}\n'
    assert _located(text) == tomllib.loads(text)["project"]["version"] == "0.13.0"


def test_version_keys_of_other_tables_are_ignored() -> None:
    """Only `version` directly in `[project]` is owned, never the root's or a sub-table's."""
    text = ('version = "9.9.9"\n[tool.demo]\nversion = "8.8.8"\n[ project ]  # the project\nname = "demo"\n'
            'version = "0.13.0"\n[project.urls]\nversion = "7.7.7"\n')
    assert _located(text) == "0.13.0"


def test_the_named_package_block_is_located_among_several() -> None:
    """The block is chosen by name, its keys in any order, its sub-tables ignored."""
    assert _located(_LOCK, "package", "demo-app") == "0.13.0"
    assert _located(_LOCK, "package", "zipp") == "3.0.0"


def test_lines_inside_strings_arrays_and_inline_tables_start_no_statement() -> None:
    """Fake headers and assignments inside values are skipped; escapes do not close strings."""
    text = ('[project]\nname = "demo"\ndescription = """\n[tool.other]\nversion = "6.6.6"\n"""\n'
            'escaped = "a \\" [b"\n'
            "classifiers = [\n  'a # not a comment',\n  [1, 2]\n]\n"
            "notes = '''\nversion = '5.5.5'\n'''\n"
            'keywords = ["x", { y = "]" }]  # a [comment\n'
            'version = "0.13.0"\n')
    assert tomllib.loads(text)["project"]["version"] == "0.13.0"
    assert _located(text) == "0.13.0"


@pytest.mark.parametrize("text", [
    'project.name = "demo"\nproject.version = "0.13.0"\n',
    'project = { name = "demo", version = "0.13.0" }\n',
    '[project]\nname = "demo"\nversion = """0.13.0"""\n',
    "[project]\nname = \"demo\"\nversion = '''\n0.13.0'''\n",
])
def test_dotted_inline_and_multi_line_layouts_are_unsupported(text: str) -> None:
    """`tomllib` reads the value, but only the plain one-line assignment is located."""
    assert tomllib.loads(text)["project"]["version"] == "0.13.0"
    with pytest.raises(SourceError, match=_LAYOUT) as caught:
        toml_scan.locate(text, "project")
    assert caught.value.exit_code == _PREFLIGHT


@pytest.mark.parametrize(("text", "table", "package", "named"), [
    ('[project]\nname = "demo"\n[ "quoted" ]\nversion = "0.13.0"\n', "project", None, _LAYOUT),
    ('[project]\nversion = "1.0.0"\nversion = "2.0.0"\n', "project", None, r"\[project\] is ambiguous: 2 single-line version assignments"),
    (_LOCK, "package", "other", r"no \[\[package\]\] block is named 'other'"),
    (_LOCK + '\n[[package]]\nname = "zipp"\nversion = "3.1.0"\n', "package", "zipp", r"2 \[\[package\]\] blocks are named 'zipp'"),
    (_LOCK.replace('version = "0.4.6"\n', ""), "package", "colorama",
     r"no single-line version assignment directly in the \[\[package\]\] block named 'colorama'"),
])
def test_missing_or_ambiguous_locations_fail(text: str, table: str, package: str | None, named: str) -> None:
    """An unread header ends the table; no or several blocks or assignments fail."""
    with pytest.raises(SourceError, match=named):
        toml_scan.locate(text, table, package=package)


def test_a_text_that_differs_from_the_parsed_value_fails() -> None:
    """An escape sequence means the value but does not spell it: unsupported."""
    text = '[project]\nversion = "0.13\\u002e0"\n'
    value = tomllib.loads(text)["project"]["version"]
    assert value == "0.13.0"
    with pytest.raises(SourceError, match=r"\[project\] reads .*0\.13\\\\u002e0.* but means '0\.13\.0': escape sequences are unsupported"):
        toml_scan.byte_span(text, b"", "project", value)


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
@pytest.mark.parametrize("bom", [b"", BOM])
def test_multi_byte_text_before_the_value_maps_to_its_byte_span(newline: str, bom: bytes) -> None:
    """A mark, accents and a non-BMP character before the value shift its byte span; the edit keeps the rest."""
    manifest = '[project]\nname = "démo"\ndescription = "Été à Noël \U0001f600"\nversion = "0.13.0"\n'
    lock = ('version = 1\nrevision = 5\n\n[[package]]\nname = "café"\nversion = "1.0.0"\n'
            f'source = {{ registry = "https://pypi.org/simple" }}\nsummary = "\U0001f600 ü"\n\n{_PACKAGES}')
    for text, table, package in ((manifest, "project", None), (lock, "package", "demo-app")):
        decoded = text.replace("\n", newline)
        content = bom + decoded.encode("utf-8")
        span = toml_scan.byte_span(decoded, bom, table, "0.13.0", package=package)
        assert content[span.start:span.end] == b"0.13.0"
        assert compose(content, [(span, b"0.14.0")]) == bom + decoded.replace('version = "0.13.0"', 'version = "0.14.0"').encode("utf-8")


# eof
