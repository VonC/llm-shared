"""Properties of the TOML scanner over generated spacing, comment and quote variants.

Step 5 of v0.14.0 version-sources: for generated `[project]` tables and
`uv.lock` package lists, with decoy `version` keys in other tables and
sub-tables, comments, arrays and multi-line strings, the scanner locates a
span whose text equals the value `tomllib` parses, and replacing that span
changes only that value while every other character stays the same. Each
example draws an integer triple and one bit field that the test decodes into
the layout, so the properties keep their example budget inside the lifecycle
limit; each text is parsed once.
"""

from __future__ import annotations

import tomllib

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.sources import toml_scan
from tools.release_workflow.sources.model import Span

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


# eof
