"""The JSON scanner locates owned values by key path, with their spans.

Step 6 of v0.14.0 version-sources: `json_scan.locate` returns the span of each
owned path's value (a string's content between its quotes, any other value's
whole text) among nested objects and arrays, in one pass with a key-path
stack. A duplicate key on an owned path fails as ambiguous, since `json` keeps
the last one silently, while duplicates elsewhere are ignored; keys are
compared after decoding their escapes. A non-object root, or a text that is
not one JSON object, fails. `byte_spans` requires each located string to read
as its parsed value, so an escape inside an owned value fails, and maps every
span to bytes in one walk: accented and non-BMP text before the top-level
`version`, and before both lock fields, shifts each byte span correctly, and
both lock edits compose from one original.
"""

from __future__ import annotations

import json
import re

import pytest

from tests.unit.tools.release_workflow.version_support import BOM
from tools.release_workflow.sources import json_scan
from tools.release_workflow.sources.model import SourceError, Span, compose

_VERSION: json_scan.JsonPath = ("version",)
_ROOT: json_scan.JsonPath = ("packages", "", "version")
_FORMAT: json_scan.JsonPath = ("lockfileVersion",)
_LOCK = (_VERSION, _ROOT, _FORMAT)
_NESTED = """{
  "name": "demo-app",
  "version": "0.13.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "node_modules/left-pad": {"version": "1.3.0", "dev": true},
    "": {"name": "demo-app", "version": "0.13.1", "keywords": ["version", {"version": "9"}]},
    "node_modules/a": {"dependencies": {"version": "^2"}}
  },
  "dependencies": {"version": {"version": "4.0.0"}}
}
"""


def _texts(text: str, spans: dict[json_scan.JsonPath, Span]) -> dict[json_scan.JsonPath, str]:
    """Return the text each located span holds."""
    return {path: text[span.start:span.end] for path, span in spans.items()}


def test_owned_paths_are_located_among_nested_objects_and_arrays() -> None:
    """Only the owned key paths count; decoy `version` keys at other paths are ignored."""
    assert _texts(_NESTED, json_scan.locate(_NESTED, _LOCK)) == {_VERSION: "0.13.0", _ROOT: "0.13.1", _FORMAT: "3"}
    assert json_scan.locate('{"name": "tool"}', _LOCK) == {}


def test_any_value_at_an_owned_path_is_spanned() -> None:
    """A container or a number at an owned path spans its whole text; the caller checks the type."""
    text = '{"version": {"a": [1, "}"]}, "lockfileVersion": -1.5e3}'
    assert _texts(text, json_scan.locate(text, _LOCK)) == {_VERSION: '{"a": [1, "}"]}', _FORMAT: "-1.5e3"}


@pytest.mark.parametrize(("text", "spelled"), [
    ('{"version": "1.0.0", "version": "2.0.0"}', "version"),
    ('{"version": "1.0.0", "vers\\u0069on": "2.0.0"}', "version"),
    ('{"version": {}, "version": []}', "version"),
    ('{"packages": {"": {"version": "1"}}, "packages": {"": {"version": "1"}}}', 'packages[""].version'),
    ('{"packages": {"": {"version": "1"}, "": {"version": "2"}}}', 'packages[""].version'),
    ('{"lockfileVersion": 1, "lockfileVersion": 3}', "lockfileVersion"),
])
def test_a_duplicate_key_on_an_owned_path_is_ambiguous(text: str, spelled: str) -> None:
    """`json` keeps the last duplicate silently, so the scanner refuses to choose."""
    with pytest.raises(SourceError, match=rf"^{re.escape(spelled)} is ambiguous: the key appears more than once"):
        json_scan.locate(text, _LOCK)


def test_duplicates_elsewhere_are_ignored() -> None:
    """Repeated keys outside the owned paths do not matter."""
    text = '{"name": "a", "name": "b", "packages": {"x": {"version": "1"}, "x": {"version": "2"}, "": {"version": "3"}}, "version": "4"}'
    assert _texts(text, json_scan.locate(text, _LOCK)) == {_ROOT: "3", _VERSION: "4"}


@pytest.mark.parametrize("text", ['[{"version": "1"}]', '"1.0.0"', "3", "", "  \n", "{} {}", '{"a": 1} x', '{"version": "1"', '{"version": "1}'])
def test_text_that_is_not_one_json_object_fails(text: str) -> None:
    """A non-object root, trailing text, an unterminated object or string fails."""
    with pytest.raises(SourceError, match=r"is not one JSON object"):
        json_scan.locate(text, _LOCK)


@pytest.mark.parametrize(("text", "located"), [('{"version": "0.13\\u002e0"}', r"'0\.13\\\\u002e0'"), ('{"name": "x"}', "None")])
def test_a_located_string_must_read_as_its_parsed_value(text: str, located: str) -> None:
    """An escape inside an owned value, or a value the text does not hold, fails before any edit."""
    with pytest.raises(SourceError, match=rf"the version value reads {located} but means '0\.13\.0': escape sequences are unsupported"):
        json_scan.byte_spans(text, b"", (_VERSION,), {_VERSION: "0.13.0"})


@pytest.mark.parametrize("bom", [b"", BOM])
def test_accented_and_non_bmp_text_shifts_each_byte_span(bom: bytes) -> None:
    """Multi-byte text before each owned value moves its byte span; both lock edits compose from one original."""
    manifest = '{\n  "description": "Café 🎉 ü",\n  "version": "0.13.0"\n}\n'
    lock = ('{\n  "name": "démo",\n  "notes": "😀😀",\n  "version": "0.13.0",\n  "lockfileVersion": 3,\n'
            '  "packages": {\n    "": {"name": "démo", "description": "naïve 🎉", "version": "0.13.0"}\n  }\n}\n')
    for text, values in ((manifest, {_VERSION: "0.13.0"}), (lock, {_VERSION: "0.13.0", _ROOT: "0.13.0"})):
        content = bom + text.encode("utf-8")
        spans = json_scan.byte_spans(text, bom, _LOCK, values)
        assert list(spans) == list(values)
        assert [content[span.start:span.end] for span in spans.values()] == [b"0.13.0"] * len(values)
        edited = compose(content, [(span, b"0.14.0") for span in spans.values()])
        assert edited == bom + text.replace('"0.13.0"', '"0.14.0"').encode("utf-8")
        assert json.loads(edited[len(bom):])["version"] == "0.14.0"


def test_paths_are_spelled_as_in_diagnostics() -> None:
    """A path reads like the JSON it names."""
    assert [json_scan.spell(path) for path in (_VERSION, _ROOT, ("a b", "c"))] == ["version", 'packages[""].version', '["a b"].c']


# eof
