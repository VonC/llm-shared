"""Properties of the TOML and JSON scanners over generated layouts.

Step 5 of v0.14.0 version-sources: for generated `[project]` tables and
`uv.lock` package lists, with decoy `version` keys in other tables and
sub-tables, comments, arrays and multi-line strings, the scanner locates a
span whose text equals the value `tomllib` parses, and replacing that span
changes only that value while every other character stays the same. Each
example draws an integer triple and one bit field that the test decodes into
the layout, so the properties keep their example budget inside the lifecycle
limit; each text is parsed once.

Step 6 adds the JSON scanner: for generated `package-lock.json`-like objects
with decoy members (escaped quotes and braces, accented and non-BMP text,
nested `version` keys in arrays and objects), optional byte-order mark,
whitespace and member order, the byte spans of the top-level `version` (when
present) and of `packages[""].version` hold exactly the values `json` parses,
and replacing them changes only those two values.

Step 7 adds the XML scanner: for generated POMs with indentation, attributes,
whitespace inside the owned elements, decoy `version` elements at other paths,
optional byte-order mark and LF or CRLF line endings, the spans of the project,
parent and dependency versions hold exactly the generated values and the
scanned text, and replacing them changes only those values.
"""

from __future__ import annotations

import json
import re
import tomllib

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.sources import json_scan, toml_scan, xml_scan
from tools.release_workflow.sources.model import Span, compose

_NUMBERS = st.integers(min_value=0, max_value=999)
_TRIPLES = st.tuples(_NUMBERS, _NUMBERS, _NUMBERS)
_SPACES = ("", " ", "  ", "\t")
_COMMENTS = ("", " # note", "\t#", "# version = '9.9.9'")
_DECOYS = (
    'name = "demo"', "# version = '1.2.3'", 'keywords = [\n  "version",\n  [1, 2],\n]',
    'description = """\nversion = "4.5.6"\n[tool.fake]\n"""', "readme = 'version = 1'",
)
_NAMES = ("alpha", "beta", "gamma", "delta")
_LINE_BITS = 11
_TARGET = "0.14.0"
_JSON_SPACES = ("", " ", "\n  ", "\r\n\t")
_JSON_DECOYS = (
    ('"description"', '"Caf\\u00e9 é 🎉 {\\"version\\": [1]}"'),
    ('"keywords"', '["version", {"version": "9.9.9"}, []]'),
    ('"dependencies"', '{"version": "^1.0.0", "x": {"version": {}}}'),
    ('"nested"', '{"packages": {"": {"version": "7.7.7"}}}'),
)
_JSON_BITS = 13
_JSON_VERSION: json_scan.JsonPath = ("version",)
_JSON_ROOT: json_scan.JsonPath = ("packages", "", "version")
_BOM = b"\xef\xbb\xbf"
_XML_WANTED = re.compile(r"project/(?:version|parent/version|dependencies/dependency/version)")
_XML_PATHS = ("project/parent/version", "project/version", "project/dependencies/dependency/version")
_XML_SPACES = ("", " ", "\n    ", " \t\n  ")
_XML_ATTRIBUTES = ("", ' id="v"', " a='1' b=\"2\"")
_XML_BITS = 8


def _bits(layout: int, shift: int, width: int) -> int:
    """Read `width` bits of the layout from `shift`."""
    return (layout >> shift) & ((1 << width) - 1)


def _line(value: str, layout: int) -> str:
    """Decode one owned `version` line from 11 bits: four spacings, the quote and the comment."""
    left, middle, right, after = (_SPACES[_bits(layout, shift, 2)] for shift in (0, 2, 4, 6))
    quote = "\"'"[_bits(layout, 8, 1)]
    return f"{left}version{middle}={right}{quote}{value}{quote}{after}{_COMMENTS[_bits(layout, 9, 2)]}"


def _manifest(value: str, layout: int) -> str:
    """Decode a manifest: the owned line among a subset of decoys, then the line endings."""
    decoys = [decoy for index, decoy in enumerate(_DECOYS) if _bits(layout, _LINE_BITS + index, 1)]
    split = _bits(layout, 16, 3) % (len(decoys) + 1)
    lines = ["[tool.before]", 'version = "7.7.7"', "[project]", *decoys[:split], _line(value, layout), *decoys[split:],
             "[tool.after]", "version = '8.8.8'"]
    return ("\r\n" if _bits(layout, 19, 1) else "\n").join(lines) + "\n"


def _lock(triple: tuple[int, int, int], layout: int) -> tuple[str, str, dict[str, str]]:
    """Decode a lock: a nonempty subset of packages, keys in either order, and the chosen package."""
    names = [name for index, name in enumerate(_NAMES) if _bits(layout, index, 1)] or list(_NAMES)
    values = {name: f"{triple[0]}.{triple[1]}.{triple[2] + index}" for index, name in enumerate(names)}
    blocks: list[str] = []
    for index, name in enumerate(names):
        keys = [f'name = "{name}"', _line(values[name], _bits(layout, 11 + index * _LINE_BITS, _LINE_BITS))]
        if _bits(layout, 4 + index, 1):
            keys.reverse()
        blocks.append("\n".join(["[[package]]", *keys, "", "[package.metadata]", 'version = "6.6.6"', ""]))
    chosen = names[_bits(layout, 8, 2) % len(names)]
    return ("\r\n" if _bits(layout, 10, 1) else "\n").join(["version = 1", "revision = 5", "", *blocks]), chosen, values


def _replaced(text: str, start: int, end: int) -> str:
    """Write the target over one span."""
    return text[:start] + _TARGET + text[end:]


@settings(max_examples=25)
@given(triple=_TRIPLES, layout=st.integers(min_value=0, max_value=(1 << 20) - 1))
def test_manifest_span_holds_the_parsed_value(triple: tuple[int, int, int], layout: int) -> None:
    """The located text is the parsed value; replacing it keeps every other character."""
    value = ".".join(map(str, triple))
    text = _manifest(value, layout)
    span = toml_scan.locate(text, "project")
    assert text[span.start:span.end] == value == tomllib.loads(text)["project"]["version"]
    edited = _replaced(text, span.start, span.end)
    assert (edited[:span.start], edited[span.start + len(_TARGET):]) == (text[:span.start], text[span.end:])
    assert toml_scan.locate(edited, "project") == Span(span.start, span.start + len(_TARGET))


@settings(max_examples=25)
@given(triple=_TRIPLES, layout=st.integers(min_value=0, max_value=(1 << (11 + len(_NAMES) * _LINE_BITS)) - 1))
def test_lock_span_holds_the_chosen_package_value(triple: tuple[int, int, int], layout: int) -> None:
    """The chosen block's value is located; only that package's parsed version changes."""
    text, name, values = _lock(triple, layout)
    span = toml_scan.locate(text, "package", package=name)
    assert text[span.start:span.end] == values[name]
    edited = tomllib.loads(_replaced(text, span.start, span.end))["package"]
    assert {package["name"]: package["version"] for package in edited} == {**values, name: _TARGET}


def _object(members: list[tuple[str, str]], space: str, colon: str) -> str:
    """Write one JSON object from raw member texts with the chosen whitespace."""
    return "{" + ",".join(f"{space}{key}:{colon}{value}" for key, value in members) + space + "}"


def _json_lock(triple: tuple[int, int, int], layout: int) -> tuple[str, bytes]:
    """Decode a lock-like object from 13 bits: whitespace, decoys, member order, top-level version and mark."""
    space, colon = _JSON_SPACES[_bits(layout, 0, 2)], " " * _bits(layout, 2, 1)
    major, minor, patch = triple
    top, root = f'"{major}.{minor}.{patch}"', f'"{major}.{minor}.{patch + 1}"'
    entry = [('"name"', '"demo"'), ('"version"', root)]
    if _bits(layout, 3, 1):
        entry.reverse()
    packages = [('"node_modules/x"', '{"version": "8.8.8"}'), ('""', _object(entry, space, colon))]
    if _bits(layout, 4, 1):
        packages.reverse()
    members = [decoy for index, decoy in enumerate(_JSON_DECOYS) if _bits(layout, 5 + index, 1)]
    if _bits(layout, 9, 1):
        members.insert(_bits(layout, 10, 2) % (len(members) + 1), ('"version"', top))
    members.append(('"packages"', _object(packages, space, colon)))
    return _object(members, space, colon) + "\n", _BOM * _bits(layout, 12, 1)


@settings(max_examples=25)
@given(triple=_TRIPLES, layout=st.integers(min_value=0, max_value=(1 << _JSON_BITS) - 1))
def test_json_spans_hold_the_parsed_values(triple: tuple[int, int, int], layout: int) -> None:
    """Each byte span holds its parsed value; replacing both changes only those values."""
    text, bom = _json_lock(triple, layout)
    data = json.loads(text)
    values: dict[json_scan.JsonPath, str] = {_JSON_VERSION: data["version"]} if "version" in data else {}
    values[_JSON_ROOT] = data["packages"][""]["version"]
    content = bom + text.encode("utf-8")
    spans = json_scan.byte_spans(text, bom, (_JSON_VERSION, _JSON_ROOT), values)
    assert {path: content[span.start:span.end].decode("utf-8") for path, span in spans.items()} == values
    edited = json.loads(compose(content, [(span, _TARGET.encode()) for span in spans.values()])[len(bom):])
    if "version" in data:
        data["version"] = _TARGET
    data["packages"][""]["version"] = _TARGET
    assert edited == data


def _xml_pom(triple: tuple[int, int, int], layout: int) -> tuple[bytes, dict[str, str]]:
    """Decode a POM from 8 bits: inner whitespace, attributes, indentation, decoy order, line endings and mark."""
    major, minor, patch = triple
    values: dict[str, str] = dict(zip(_XML_PATHS, (f"{major}.{minor}.{patch}", f"{major}.{minor}.{patch + 1}", f"{major}.{minor + 1}.{patch}"), strict=True))
    inner, attribute = _XML_SPACES[_bits(layout, 0, 2)], _XML_ATTRIBUTES[_bits(layout, 2, 2) % len(_XML_ATTRIBUTES)]
    indent = "\t" if _bits(layout, 4, 1) else "  "

    def owned(value: str) -> str:
        return f"<version{attribute}>{inner}{value}{inner}</version>"

    decoys = [f"{indent}<description>é 😀 <version>9.9.9</version></description>",
              f"{indent}<build><plugins><plugin><version>{values['project/version']}</version></plugin></plugins></build>"]
    if _bits(layout, 5, 1):
        decoys.reverse()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<project xmlns="http://maven.apache.org/POM/4.0.0">',
             f"{indent}<parent><groupId>g</groupId>{owned(values['project/parent/version'])}</parent>", decoys[0],
             f"{indent}{owned(values['project/version'])}",
             f"{indent}<dependencies><dependency><artifactId>a</artifactId>{owned(values['project/dependencies/dependency/version'])}"
             "</dependency></dependencies>", decoys[1], "</project>", ""]
    text = ("\r\n" if _bits(layout, 6, 1) else "\n").join(lines)
    return _BOM * _bits(layout, 7, 1) + text.encode("utf-8"), values


@settings(max_examples=25)
@given(triple=_TRIPLES, layout=st.integers(min_value=0, max_value=(1 << _XML_BITS) - 1))
def test_xml_spans_hold_the_generated_values(triple: tuple[int, int, int], layout: int) -> None:
    """Each owned span holds its value and the scanned text; replacing them changes only those values."""
    content, values = _xml_pom(triple, layout)
    document = xml_scan.scan(content, "pom.xml", _XML_WANTED)
    located = {value.path: value for value in document.values}
    assert {path: (content[value.span.start:value.span.end].decode("utf-8"), value.text) for path, value in located.items()} == {
        path: (value, value) for path, value in values.items()}
    edited = xml_scan.scan(compose(content, [(value.owned("pom.xml"), _TARGET.encode()) for value in located.values()]), "pom.xml", _XML_WANTED)
    assert [value.text for value in edited.values] == [_TARGET] * len(_XML_PATHS)


# eof
