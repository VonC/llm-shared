"""Version tokens, forms, the read-once file view and the shared source model.

Step 2 of v0.14.0 version-sources: one token grammar with numeric ordering of
cores, the three forms and the release-only guard, a file view that loads each
path once per phase, span composition from one original, the one
character-to-byte span mapping, and the shared input, capture, edit and plan
types every later step uses (plan decision Q16). Step 6 adds the view's
per-phase derived values, computed once per key and view.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from tests.unit.tools.release_workflow.version_support import BOM, load_counts
from tools.release_workflow.sources import model
from tools.release_workflow.sources.model import (
    Claim,
    Detection,
    FileCapture,
    FileEdit,
    FileView,
    Form,
    Inventory,
    LocatedSource,
    Plan,
    SourceChange,
    SourceError,
    Span,
    VersionError,
    VersionInputs,
    VersionToken,
    VisibleRecord,
    check_release_only,
    compose,
    to_byte_spans,
)

if TYPE_CHECKING:
    from tools.release_workflow.invocation import InvocationContext

_PREFLIGHT = 2


@pytest.mark.parametrize(("text", "fields"), [
    ("0.0.0", (0, 0, 0, False)), ("0.14.0", (0, 14, 0, False)), ("10.0.0-SNAPSHOT", (10, 0, 0, True)),
])
def test_accepted_tokens(text: str, fields: tuple[int, int, int, bool]) -> None:
    """Decimal triples without leading zeros, with an optional uppercase suffix."""
    token = VersionToken.parse(text)
    assert (token.major, token.minor, token.patch, token.snapshot) == fields
    assert str(token) == text


@pytest.mark.parametrize("text", [
    "v0.14.0", "0.14.0-snapshot", "0.014.0", "01.0.0", "1.0", "1.0.0.0", "", " 0.14.0", "0.14.0 ", "0.14.0-RC1",
])
def test_rejected_tokens_name_the_grammar(text: str) -> None:
    """Every rejection is an input failure whose remedy states the expected grammar."""
    with pytest.raises(VersionError, match=r"MAJOR\.MINOR\.PATCH") as caught:
        VersionToken.parse(text)
    assert caught.value.exit_code == _PREFLIGHT
    assert repr(text) in str(caught.value)


def test_cores_order_numerically_and_ignore_the_suffix() -> None:
    """`0.10.0` is above `0.9.0`; the snapshot suffix plays no part in the order."""
    assert VersionToken.parse("0.10.0").key > VersionToken.parse("0.9.0").key
    assert VersionToken.parse("1.0.0-SNAPSHOT").key == VersionToken.parse("1.0.0").key
    assert VersionToken.parse("1.0.0-SNAPSHOT").core == VersionToken.parse("1.0.0")


@pytest.mark.parametrize(("form", "anchor", "expected"), [
    (Form.SNAPSHOT, "0.14.0-SNAPSHOT", "0.14.0-SNAPSHOT"), (Form.CORE, "0.14.0-SNAPSHOT", "0.14.0"),
    (Form.RELEASE_ONLY, "0.14.0-SNAPSHOT", "0.14.0"), (Form.SNAPSHOT, "0.14.0", "0.14.0"),
    (Form.CORE, "0.14.0", "0.14.0"), (Form.RELEASE_ONLY, "0.14.0", "0.14.0"),
])
def test_expected_value_by_form(form: Form, anchor: str, expected: str) -> None:
    """`snapshot` takes the whole anchor token; `core` and `release-only` its core."""
    assert form.expected(VersionToken.parse(anchor)) == expected


def test_form_names() -> None:
    """Configuration spells forms in lowercase; anything else is rejected with the choices."""
    assert [Form.parse(name) for name in ("snapshot", "core", "release-only")] == [Form.SNAPSHOT, Form.CORE, Form.RELEASE_ONLY]
    with pytest.raises(SourceError, match="snapshot, core, release-only"):
        Form.parse("Core")


def _source(value: str, form: Form = Form.RELEASE_ONLY) -> LocatedSource:
    """Locate one npm-like value without reading a file."""
    root = Path("C:/project")
    return LocatedSource(root / "package.json", "version", "npm", form, value, (Span(14, 14 + len(value)),), root)


@pytest.mark.parametrize("value", ["0.14.0", "0.13.9"])
def test_release_only_accepts_a_value_not_above_the_target(value: str) -> None:
    """A release-only value at or below the expected core does not stop the plan."""
    check_release_only(_source(value), VersionToken.parse("0.14.0-SNAPSHOT"))


def test_release_only_refuses_a_value_above_the_target() -> None:
    """The refusal names the source, its value and the target."""
    with pytest.raises(SourceError) as caught:
        check_release_only(_source("0.15.0"), VersionToken.parse("0.14.0-SNAPSHOT"))
    message = str(caught.value)
    assert all(part in message for part in ("package.json", "version", "0.15.0", "0.14.0"))
    assert caught.value.exit_code == _PREFLIGHT


@pytest.mark.parametrize("value", ["0.15.0-SNAPSHOT", "next", ""])
def test_release_only_malformed_value(value: str) -> None:
    """A release-only value that is not a release token is malformed."""
    with pytest.raises(SourceError, match="malformed"):
        check_release_only(_source(value), VersionToken.parse("0.14.0"))


def test_release_only_guard_ignores_other_forms() -> None:
    """Only release-only sources are guarded; a core source above the target is drift elsewhere."""
    check_release_only(_source("9.0.0", Form.CORE), VersionToken.parse("0.14.0"))


def test_file_view_loads_each_path_once(tmp_path: Path) -> None:
    """Reads, text decoding and absence each cost at most one load per view."""
    present, absent = tmp_path / "version.txt", tmp_path / "missing.txt"
    present.write_bytes(BOM + "0.14.0 -- Été\n".encode())
    view = FileView()
    assert view.read(present) == view.read(present) == BOM + "0.14.0 -- Été\n".encode()
    assert view.text(present) == ("0.14.0 -- Été\n", BOM)
    assert view.read(absent) is None
    assert view.read(absent) is None
    assert load_counts(view, present, absent) == (1, 1)
    fresh = FileView()
    fresh.read(present)
    assert load_counts(fresh, present, absent) == (1, 0)


def test_file_view_text_failures_name_the_path(tmp_path: Path) -> None:
    """Strict UTF-8 and absence fail as source errors naming the file."""
    broken = tmp_path / "broken.json"
    broken.write_bytes(b'{"version": "\xff"}')
    view = FileView()
    with pytest.raises(SourceError, match=r"broken\.json.*UTF-8"):
        view.text(broken)
    with pytest.raises(SourceError, match=r"missing\.json.*does not exist"):
        view.text(tmp_path / "missing.json")


def test_file_view_derives_each_value_once_per_view() -> None:
    """A value computed from a view's files, such as an index across roots, is computed once per key and view."""
    calls: list[str] = []

    def compute(name: str) -> dict[str, int]:
        calls.append(name)
        return {name: len(calls)}

    view = FileView()
    first = view.derived("index", lambda: compute("first"))
    assert view.derived("index", lambda: compute("second")) is first == {"first": 1}
    assert view.derived("other", lambda: compute("other")) == {"other": 2}
    assert FileView().derived("index", lambda: compute("fresh")) == {"fresh": 3}
    assert calls == ["first", "other", "fresh"]


def test_compose_disjoint_spans_from_one_original() -> None:
    """Several spans, adjacent ones included, build one content from the same original."""
    original = b'{"version": "0.13.0", "lock": "0.13.0"}'
    edits = [(Span(31, 37), b"0.14.0"), (Span(13, 19), b"0.14.0"), (Span(0, 0), b"")]
    assert compose(original, edits) == b'{"version": "0.14.0", "lock": "0.14.0"}'
    assert compose(b"abcd", [(Span(0, 2), b"XY"), (Span(2, 4), b"Z")]) == b"XYZ"


@pytest.mark.parametrize("spans", [(Span(2, 9),), (Span(0, 3), Span(2, 4))])
def test_compose_rejects_outside_and_overlapping_spans(spans: tuple[Span, ...]) -> None:
    """A span past the end, or two overlapping spans, cannot be composed."""
    with pytest.raises(SourceError, match="span"):
        compose(b"abcdef", [(span, b"x") for span in spans])


def test_span_bounds() -> None:
    """A span starts at a non-negative offset and never ends before it starts."""
    for start, end in ((-1, 2), (3, 2)):
        with pytest.raises(ValueError, match="span"):
            Span(start, end)


@pytest.mark.parametrize("bom", [b"", BOM])
def test_to_byte_spans_maps_characters_to_bytes(bom: bytes, monkeypatch: pytest.MonkeyPatch) -> None:
    """Accented and non-BMP characters before and between fields shift each byte span correctly."""
    text = 'é="0.13.0" 😀 ü="0.13.0-SNAPSHOT" fin'
    first, second = text.index("0.13.0"), text.index("0.13.0-SNAPSHOT")
    char_spans = [Span(first, first + len("0.13.0")), Span(second, second + len("0.13.0-SNAPSHOT"))]
    encoded: list[str] = []
    measure = model._utf8_length

    def counting(segment: str) -> int:
        encoded.append(segment)
        return measure(segment)

    monkeypatch.setattr(model, "_utf8_length", counting)
    byte_spans = to_byte_spans(text, len(bom), char_spans)
    content = bom + text.encode("utf-8")
    assert [content[span.start:span.end] for span in byte_spans] == [b"0.13.0", b"0.13.0-SNAPSHOT"]
    assert sum(len(segment) for segment in encoded) == max(span.end for span in char_spans)
    replaced = compose(content, [(byte_spans[0], b"0.14.0"), (byte_spans[1], b"0.14.0-SNAPSHOT")])
    assert replaced == bom + text.replace("0.13.0", "0.14.0").encode("utf-8")


def test_to_byte_spans_rejects_a_span_past_the_text() -> None:
    """A character span beyond the decoded text cannot be mapped."""
    with pytest.raises(SourceError, match="span"):
        to_byte_spans("abc", 0, [Span(1, 4)])


def test_version_inputs_from_context() -> None:
    """The shared inputs copy project, configuration, artifacts and Git from the context."""
    context = SimpleNamespace(project="project", configuration="configuration", artifacts="artifacts", git="git", payload="ignored")
    inputs = VersionInputs.from_context(cast("InvocationContext", context))
    assert (inputs.project, inputs.configuration, inputs.artifacts, inputs.git) == ("project", "configuration", "artifacts", "git")


def test_file_capture_and_edit(tmp_path: Path) -> None:
    """A capture records absence as `None`, present bytes with their SHA-256; an edit must change bytes."""
    path = tmp_path / "package.json"
    assert FileCapture.of(path, None) == FileCapture(path, None, None)
    captured = FileCapture.of(path, b'"0.13.0"')
    assert captured.sha256 == hashlib.sha256(b'"0.13.0"').hexdigest()
    change = SourceChange(path, "version", "npm", "0.13.0", "0.14.0")
    edit = FileEdit(captured, b'"0.14.0"', (change,))
    assert edit.changes == (change,)
    with pytest.raises(SourceError, match="unchanged"):
        FileEdit(captured, b'"0.13.0"', (change,))


def test_inventory_and_plan_hold_the_planned_state(tmp_path: Path) -> None:
    """The inventory and plan carry detection results, claims, captures and edits unchanged."""
    source = _source("0.13.0")
    record = VisibleRecord(tmp_path / "tool/pyproject.toml", "project.version", "python", "not-participating tool-only")
    detection = Detection((source,), (record,))
    claim = Claim(source.path, source.field, source.adapter, source.spans)
    capture = FileCapture.of(source.path, b'{"version": "0.13.0"}')
    inventory = Inventory(detection.sources, detection.visible, (claim,), (capture,))
    plan = Plan(VersionToken.parse("0.14.0"), inventory, ())
    assert (plan.inventory.sources, plan.inventory.visible, plan.inventory.claims) == ((source,), (record,), (claim,))
    assert Detection() == Detection((), ())


# eof
