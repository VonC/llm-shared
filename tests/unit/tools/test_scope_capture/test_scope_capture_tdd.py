"""Scope captures round-trip and reject incomplete, tampered or stale evidence."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.scope_capture import (
    WHOLE_SCOPE,
    CaptureError,
    ResolvedScope,
    ScopeKind,
    from_json,
    scope_fingerprint,
    validate_capture,
    write_capture,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


def group_scope() -> ResolvedScope:
    """Return a minimal resolved group for serialization tests."""
    patterns = ("tests/**",)
    sources = ("tools/**",)
    tests = ("tests/test_x.py",)
    files = ("tools/x.py",)
    return ResolvedScope(ScopeKind.GROUP, "demo", patterns, sources, tests, files,
                         scope_fingerprint("demo", patterns, sources, tests, files),
                         {"declaration": ".ghog-groups", "requirement": "docs/feature.md"})


def test_group_round_trip_and_atomic_write(tmp_path: Path) -> None:
    """A capture retains resolution and provenance without reading a declaration."""
    scope = group_scope()
    for name in (*scope.test_files, *scope.source_files):
        path = tmp_path / name
        path.parent.mkdir(exist_ok=True)
        path.touch()
    output = tmp_path / "scope.json"
    write_capture(output, scope)
    assert validate_capture(tmp_path, output.read_text(encoding="utf-8")) == scope
    assert list(tmp_path.glob("*.tmp")) == []
    assert scope.key() == "group:demo"
    assert scope.label() == "group demo"
    assert scope.selector() == "--group=demo"


def test_whole_scope_has_fixed_identity(tmp_path: Path) -> None:
    """The whole suite has neither group membership nor declaration dependency."""
    assert validate_capture(tmp_path, WHOLE_SCOPE.to_json()) == WHOLE_SCOPE
    assert WHOLE_SCOPE.key() == "whole"
    assert WHOLE_SCOPE.selector() == "--whole-suite"
    assert WHOLE_SCOPE.label() == "the whole suite"
    assert WHOLE_SCOPE.fingerprint == hashlib.sha256(b"scope=whole").hexdigest()


@pytest.mark.parametrize("text", ["{", "[]", "{}", '{"kind":"other"}'])
def test_incomplete_capture(text: str) -> None:
    """Malformed JSON and missing schema fields fail with the bound-scope diagnostic."""
    with pytest.raises(CaptureError, match="bound scope unusable"):
        from_json(text)


@pytest.mark.parametrize(("key", "value"), [
    ("name", "Other"), ("kind", "other"), ("fingerprint", "0" * 64),
    ("fingerprint", 123),
    ("test_patterns", []), ("test_files", []), ("source_files", ["../outside.py"]),
    ("source_files", ["C:/outside.py"]), ("source_files", ["/outside.py"]),
    ("source_files", ["tools\\x.py"]), ("source_files", ["tools/./x.py"]),
    ("source_files", ["tools/x.py", "tools/x.py"]),
    ("test_files", "tests/test_x.py"), ("provenance", []), ("provenance", {"x": 1}),
])
def test_tampered_capture(key: str, value: object) -> None:
    """Wrong types, noncanonical paths and inconsistent fingerprints are rejected."""
    payload: dict[str, object] = json.loads(group_scope().to_json())
    payload[key] = value
    with pytest.raises(CaptureError, match="bound scope unusable"):
        from_json(json.dumps(payload))


def test_deleted_file_is_not_reresolved(tmp_path: Path) -> None:
    """A formerly valid capture fails before the caller can run tests."""
    with pytest.raises(CaptureError, match=r"bound scope unusable:.*tests/test_x.py"):
        validate_capture(tmp_path, group_scope().to_json())


def test_whole_capture_cannot_hide_group_files() -> None:
    """The fixed whole fingerprint cannot legitimize group-shaped content."""
    with pytest.raises(CaptureError, match="bound scope unusable"):
        from_json(replace(WHOLE_SCOPE, test_files=("tests/test_x.py",)).to_json())


def test_write_error_does_not_replace_previous_capture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed replace preserves the previous published capture."""
    target = tmp_path / "scope.json"
    target.write_text("previous", encoding="utf-8")

    def fail_replace(_path: Path, _target: Path) -> None:
        """Simulate a locked destination."""
        reason = "locked"
        raise OSError(reason)

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(CaptureError, match="bound scope unusable"):
        write_capture(target, WHOLE_SCOPE)
    assert target.read_text(encoding="utf-8") == "previous"
    assert not target.with_suffix(".json.tmp").exists()


def test_provenance_does_not_change_scope_identity() -> None:
    """Scope identity describes selected files, not the caller writing the capture."""
    provenance: Mapping[str, str] = {"requirement": "docs/another.md"}
    scope = replace(group_scope(), provenance=provenance)
    assert from_json(scope.to_json()).fingerprint == group_scope().fingerprint
