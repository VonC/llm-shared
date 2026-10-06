"""Unit tests for the groundhog proof marker (v0.13.0 full_suite_levels).

Step 1: a round trip of the five keys for the whole suite and for a group;
any missing key, unknown value, extra or reordered line, undecodable,
unreadable or legacy one-line marker reads as no proof; the write goes
through a temporary file and ``replace`` and logs its failures; the remover
tolerates a missing marker and logs its failures; ``marker_path_for`` names
``a.ghog.day.ok`` and ``a.ghog.day.<group>.ok`` and refuses unknown keys;
``source_digest`` reuses a walk from the public ``source_files``; and
``timing_fingerprint`` changes with line 2 or an exclusion entry while
ignoring line 1. A read marker feeds the pure effective-proof rule directly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.groundhog import floor, proof, snapshot
from tools.groundhog.levels import FullLevel
from tools.groundhog.snapshot import ProofMarker

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_DIGEST = "d" * 64
_TIMING = "a" * 64
_GROUP_KEY = "group:sentinel"
_MARKER = ProofMarker(
    scope=snapshot.WHOLE_SCOPE_KEY,
    fingerprint=snapshot.WHOLE_SCOPE_FINGERPRINT,
    timing=_TIMING,
    digest=_DIGEST,
    proof=FullLevel.COV,
)
_VALID_LINES = (
    "scope=whole",
    f"fingerprint={snapshot.WHOLE_SCOPE_FINGERPRINT}",
    f"timing={_TIMING}",
    f"digest={_DIGEST}",
    "proof=cov",
)


def _text(lines: Sequence[str]) -> str:
    """Join marker lines with their trailing newlines.

    Args:
        lines: The marker lines.

    Returns:
        The marker text.
    """
    return "".join(f"{line}\n" for line in lines)


def _replace_line(index: int, line: str) -> str:
    """Return the valid marker with one line replaced.

    Args:
        index: The line to replace.
        line: The replacement line.

    Returns:
        The marker text.
    """
    lines = list(_VALID_LINES)
    lines[index] = line
    return _text(lines)


def _seed_project(root: Path) -> None:
    """Write two Python files of a tiny project.

    Args:
        root: The project root.
    """
    package = root / "pkg"
    package.mkdir()
    (package / "a.py").write_text("A = 1\n", encoding="utf-8")
    (package / "b.py").write_text("B = 2\n", encoding="utf-8")


def test_marker_round_trip_of_the_five_keys(tmp_path: Path) -> None:
    """A written whole-suite marker reads back equal, one key per line."""
    path = snapshot.marker_path_for(tmp_path, snapshot.WHOLE_SCOPE_KEY)
    snapshot.write_proof_marker(path, _MARKER)
    assert path.read_text(encoding="utf-8") == _text(_VALID_LINES)
    assert snapshot.read_proof_marker(path) == _MARKER


def test_group_marker_round_trip(tmp_path: Path) -> None:
    """A group scope round-trips through its own marker file."""
    marker = ProofMarker(
        scope=_GROUP_KEY,
        fingerprint="f" * 64,
        timing=_TIMING,
        digest=_DIGEST,
        proof=FullLevel.NONE,
    )
    path = snapshot.marker_path_for(tmp_path, _GROUP_KEY)
    snapshot.write_proof_marker(path, marker)
    assert snapshot.read_proof_marker(path) == marker


@pytest.mark.parametrize(
    "text",
    [
        pytest.param(f"{_DIGEST}\n", id="legacy-one-line"),
        pytest.param("", id="empty"),
        pytest.param(_text(_VALID_LINES[:-1]), id="missing-key"),
        pytest.param(_text([*_VALID_LINES, "junk"]), id="extra-line"),
        pytest.param(_text([*_VALID_LINES, ""]), id="extra-blank-line"),
        pytest.param(_text([_VALID_LINES[1], _VALID_LINES[0], *_VALID_LINES[2:]]), id="reordered"),
        pytest.param(_replace_line(0, "scope"), id="no-separator"),
        pytest.param(_replace_line(0, "scope=other"), id="unknown-scope"),
        pytest.param(_replace_line(0, "scope=group:"), id="empty-group"),
        pytest.param(_replace_line(0, "scope=group:Bad"), id="invalid-group"),
        pytest.param(_replace_line(3, "digest=xyz"), id="non-hex-digest"),
        pytest.param(_replace_line(2, f"timing={_TIMING.upper()}"), id="uppercase-timing"),
        pytest.param(_replace_line(4, "proof=unproven"), id="unproven-proof"),
        pytest.param(_replace_line(4, "proof=fast"), id="unknown-proof"),
        pytest.param(_replace_line(4, "proof"), id="proof-without-value"),
    ],
)
def test_malformed_marker_reads_as_no_proof(tmp_path: Path, text: str) -> None:
    """Anything but the exact five known keys with known values is no proof."""
    path = tmp_path / snapshot.MARKER_FILE_NAME
    path.write_text(text, encoding="utf-8")
    assert snapshot.read_proof_marker(path) is None


def test_unreadable_marker_reads_as_no_proof(tmp_path: Path) -> None:
    """A missing, undecodable or unreadable marker is no proof."""
    assert snapshot.read_proof_marker(tmp_path / "absent.ok") is None
    binary = tmp_path / "binary.ok"
    binary.write_bytes(b"\xff\xfe\x00scope")
    assert snapshot.read_proof_marker(binary) is None
    assert snapshot.read_proof_marker(tmp_path) is None


def test_write_goes_through_a_temporary_file_and_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The marker is replaced atomically from its side file, never rewritten in place."""
    original: Callable[[Path, Path], Path] = Path.replace
    calls: list[tuple[str, str]] = []

    def _recording_replace(self: Path, target: Path) -> Path:
        calls.append((self.name, Path(target).name))
        return original(self, target)

    monkeypatch.setattr(Path, "replace", _recording_replace)
    path = tmp_path / snapshot.MARKER_FILE_NAME
    snapshot.write_proof_marker(path, _MARKER)
    assert calls == [(f"{snapshot.MARKER_FILE_NAME}.tmp", snapshot.MARKER_FILE_NAME)]
    assert sorted(child.name for child in tmp_path.iterdir()) == [snapshot.MARKER_FILE_NAME]


def test_write_failure_is_logged_not_raised(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A marker that cannot be written leaves a log line, never an exception."""
    caplog.set_level(logging.INFO, logger="groundhog")
    path = tmp_path / "missing" / snapshot.MARKER_FILE_NAME
    snapshot.write_proof_marker(path, _MARKER)
    assert not path.exists()
    assert any("could not write" in message for message in caplog.messages)


def test_remove_tolerates_a_missing_marker(tmp_path: Path) -> None:
    """An unproven walk removes its marker; a second removal is harmless."""
    path = tmp_path / snapshot.MARKER_FILE_NAME
    snapshot.write_proof_marker(path, _MARKER)
    snapshot.remove_proof_marker(path)
    assert not path.exists()
    snapshot.remove_proof_marker(path)
    assert not path.exists()


def test_remove_failure_is_logged_not_raised(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A locked marker leaves a log line, never an exception."""

    def _locked_unlink(self: Path, *, missing_ok: bool = False) -> None:
        del self, missing_ok
        message = "locked"
        raise PermissionError(message)

    caplog.set_level(logging.INFO, logger="groundhog")
    monkeypatch.setattr(Path, "unlink", _locked_unlink)
    snapshot.remove_proof_marker(tmp_path / snapshot.MARKER_FILE_NAME)
    assert any("could not remove" in message for message in caplog.messages)


def test_marker_path_for_names_one_file_per_scope(tmp_path: Path) -> None:
    """The whole suite keeps a.ghog.day.ok; a group gets a.ghog.day.<group>.ok."""
    whole = snapshot.marker_path_for(tmp_path, snapshot.WHOLE_SCOPE_KEY)
    group = snapshot.marker_path_for(tmp_path, _GROUP_KEY)
    home = tmp_path.resolve() / ".reviews"
    assert whole == home / "a.ghog.day.ok"
    assert whole == snapshot.marker_path(tmp_path)
    assert group == home / "a.ghog.day.sentinel.ok"


@pytest.mark.parametrize("scope_key", ["", "other", "group:", "group:Bad", "group:1x", "groups:x"])
def test_marker_path_for_refuses_an_unknown_scope(tmp_path: Path, scope_key: str) -> None:
    """An unknown key or an invalid group name names no marker file."""
    with pytest.raises(ValueError, match="unknown proof scope"):
        snapshot.marker_path_for(tmp_path, scope_key)


def test_source_digest_reuses_a_given_walk(tmp_path: Path) -> None:
    """The digest of the public walk equals the digest that walks itself."""
    _seed_project(tmp_path)
    files = snapshot.source_files(tmp_path)
    assert [path.name for path in files] == ["a.py", "b.py"]
    assert snapshot.source_digest(tmp_path, files) == snapshot.source_digest(tmp_path)
    assert snapshot.source_digest(tmp_path, files[:1]) != snapshot.source_digest(tmp_path)


def test_timing_fingerprint_follows_line_2_and_the_exclusions(tmp_path: Path) -> None:
    """Line 2 and every exclusion entry move the fingerprint; line 1 does not."""
    unset = snapshot.timing_fingerprint(tmp_path)
    floor_file = floor.floor_path(tmp_path)
    floor_file.write_text(f"0.0\n{floor.DEFAULT_FLOOR}\n", encoding="utf-8")
    default = snapshot.timing_fingerprint(tmp_path)
    floor_file.write_text(f"3.5\n{floor.DEFAULT_FLOOR}\n", encoding="utf-8")
    line_1 = snapshot.timing_fingerprint(tmp_path)
    floor_file.write_text("3.5\n2.0\n", encoding="utf-8")
    line_2 = snapshot.timing_fingerprint(tmp_path)
    floor_file.write_text("3.5\n2.0\n[exclusion]\ntests/test_a.py::test_slow = 4.0\n", encoding="utf-8")
    excluded = snapshot.timing_fingerprint(tmp_path)
    floor_file.write_text("3.5\n2.0\n[exclusion]\ntests/test_a.py::test_slow = 3.0\n", encoding="utf-8")
    lowered = snapshot.timing_fingerprint(tmp_path)
    assert unset == default == line_1
    assert len({default, line_2, excluded, lowered}) == len((default, line_2, excluded, lowered))


def test_whole_scope_fingerprint_is_a_sha256() -> None:
    """The fixed whole-suite fingerprint has the marker's sha256 shape."""
    assert len(snapshot.WHOLE_SCOPE_FINGERPRINT) == len(_DIGEST)
    assert set(snapshot.WHOLE_SCOPE_FINGERPRINT) <= set("0123456789abcdef")


def test_read_marker_feeds_the_effective_proof_rule(tmp_path: Path) -> None:
    """A read marker is the port of the pure effective-saved rule."""
    path = snapshot.marker_path_for(tmp_path, snapshot.WHOLE_SCOPE_KEY)
    snapshot.write_proof_marker(path, _MARKER)
    effective = proof.effective_saved(
        snapshot.read_proof_marker(path),
        scope_key=snapshot.WHOLE_SCOPE_KEY,
        fingerprint=snapshot.WHOLE_SCOPE_FINGERPRINT,
        digest=_DIGEST,
        timing=_TIMING,
    )
    assert effective is FullLevel.COV


# eof
