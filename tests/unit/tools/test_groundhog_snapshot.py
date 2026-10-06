"""Unit tests for the ghog day source snapshot (Q28).

Cover the digest stability and sensitivity (touch, add, remove,
excluded folders, gate configuration files), the marker round-trip, and
the safe directions of the saved-proof read (no marker, mismatch,
unreadable marker).

Fix: the marker lives in the artifact home (``.reviews`` by default), not at
the project root; a root marker left by an older walk is moved there on first
use, and a home that cannot be prepared reads as changed.

Fix (v0.13.0 full_suite_levels, Step 2): the one-line ``write_marker`` and
``is_unchanged`` are gone; their round-trip and safe-direction cases now drive
``save_proof`` and ``effective_proof``: a saved proof holds on unchanged
sources, falls on a touched file, is capped at ``cov`` by a timing change, is
removed when nothing is proven, and a legacy, unreadable or unpreparable
marker proves nothing. A saved proof moves to the digest a walk's test steps
run on only when that digest did not change.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from tools.groundhog import exclusions, snapshot
from tools.groundhog.levels import FullLevel

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _touch(path: Path, mtime_ns: int) -> None:
    """Set a deterministic mtime on a file.

    Args:
        path: The file to stamp.
        mtime_ns: The mtime, in nanoseconds.
    """
    os.utime(path, ns=(mtime_ns, mtime_ns))


def _seed_project(root: Path) -> Path:
    """Create a small project tree with stable mtimes.

    Args:
        root: The project root directory.

    Returns:
        The seeded source file.
    """
    src = root / "src"
    src.mkdir()
    source = src / "mod.py"
    source.write_text("print('hi')\n", encoding="utf-8")
    _touch(source, 1_000_000_000)
    return source


def test_digest_is_stable_without_changes(tmp_path: Path) -> None:
    """The digest does not move when nothing changed."""
    _seed_project(tmp_path)
    assert snapshot.source_digest(tmp_path) == snapshot.source_digest(tmp_path)


def test_digest_moves_on_touch_add_and_remove(tmp_path: Path) -> None:
    """A touched, added or removed Python file moves the digest."""
    source = _seed_project(tmp_path)
    before = snapshot.source_digest(tmp_path)
    _touch(source, 2_000_000_000)
    touched = snapshot.source_digest(tmp_path)
    assert touched != before
    extra = tmp_path / "src" / "new.py"
    extra.write_text("pass\n", encoding="utf-8")
    added = snapshot.source_digest(tmp_path)
    assert added != touched
    extra.unlink()
    assert snapshot.source_digest(tmp_path) == touched


def test_digest_ignores_excluded_folders(tmp_path: Path) -> None:
    """Files under excluded folders never move the digest."""
    _seed_project(tmp_path)
    before = snapshot.source_digest(tmp_path)
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "mod.cpython-313.py").write_text("x\n", encoding="utf-8")
    venv = tmp_path / "venvs" / "py"
    venv.mkdir(parents=True)
    (venv / "site.py").write_text("x\n", encoding="utf-8")
    assert snapshot.source_digest(tmp_path) == before


def test_digest_ignores_the_artifact_home(tmp_path: Path) -> None:
    """Scratch scripts in the default or a declared artifact home never move the digest."""
    _seed_project(tmp_path)
    before = snapshot.source_digest(tmp_path)
    reviews = tmp_path / ".reviews"
    reviews.mkdir()
    (reviews / "a.dex.step3.tmp.probe.py").write_text("x\n", encoding="utf-8")
    assert snapshot.source_digest(tmp_path) == before

    (tmp_path / ".review-artifacts.ini").write_text(
        "[review-artifacts]\nhome = .private/work\n", encoding="utf-8",
    )
    declared = tmp_path / ".private" / "work"
    declared.mkdir(parents=True)
    (declared / "a.tmp.scan.py").write_text("x\n", encoding="utf-8")
    assert snapshot.source_digest(tmp_path) != before
    moved = snapshot.source_digest(tmp_path)
    (declared / "a.tmp.other.py").write_text("y\n", encoding="utf-8")
    assert snapshot.source_digest(tmp_path) == moved


def test_digest_falls_back_to_the_default_home(tmp_path: Path) -> None:
    """An unreadable declaration still keeps `.reviews` out of the digest."""
    _seed_project(tmp_path)
    (tmp_path / ".review-artifacts.ini").write_text("not an ini\n", encoding="utf-8")
    before = snapshot.source_digest(tmp_path)
    reviews = tmp_path / ".reviews"
    reviews.mkdir()
    (reviews / "a.tmp.probe.py").write_text("x\n", encoding="utf-8")
    assert snapshot.source_digest(tmp_path) == before


def test_digest_covers_the_gate_configuration(tmp_path: Path) -> None:
    """pyproject.toml changes move the digest (the gate may move)."""
    _seed_project(tmp_path)
    before = snapshot.source_digest(tmp_path)
    config = tmp_path / "pyproject.toml"
    config.write_text("[tool.coverage.report]\nfail_under = 90\n", encoding="utf-8")
    _touch(config, 1_000_000_000)
    assert snapshot.source_digest(tmp_path) != before


def _effective(root: Path) -> snapshot.EffectiveProof:
    """Read the whole-suite proof valid for the current sources of a root."""
    return snapshot.effective_proof(root, snapshot.WHOLE_SCOPE_KEY, snapshot.WHOLE_SCOPE_FINGERPRINT)


def _save(root: Path, proof: FullLevel | None) -> None:
    """Record a whole-suite proof on the current digest of a root."""
    digest = snapshot.source_digest(root)
    snapshot.save_proof(root, snapshot.WHOLE_SCOPE_KEY, snapshot.WHOLE_SCOPE_FINGERPRINT, digest, proof)


def test_saved_proof_round_trip_until_a_file_moves(tmp_path: Path) -> None:
    """A saved proof holds on unchanged sources and falls on a touched file."""
    source = _seed_project(tmp_path)
    assert _effective(tmp_path) == snapshot.EffectiveProof(snapshot.source_digest(tmp_path), None)
    _save(tmp_path, FullLevel.COV)
    path = snapshot.marker_path(tmp_path)
    assert path == tmp_path.resolve() / ".reviews" / snapshot.MARKER_FILE_NAME
    assert not (tmp_path / snapshot.MARKER_FILE_NAME).exists()
    assert _effective(tmp_path).proof is FullLevel.COV
    _touch(source, 3_000_000_000)
    assert _effective(tmp_path).proof is None


def test_saved_proof_moves_only_with_an_unchanged_digest() -> None:
    """A saved proof follows the sources only while their digest stays the same."""
    state = snapshot.EffectiveProof("before", FullLevel.SPEED)
    assert state.on_sources("before") is state
    assert state.on_sources("fixed") == snapshot.EffectiveProof("fixed", None)


def test_timing_change_caps_saved_speed_at_cov(tmp_path: Path) -> None:
    """A new exclusion keeps the digest but caps a saved speed proof at cov."""
    _seed_project(tmp_path)
    _save(tmp_path, FullLevel.SPEED)
    assert _effective(tmp_path).proof is FullLevel.SPEED
    exclusions.write_exclusions(tmp_path, {"tests/test_slow.py::test_freak": 2.5})
    assert _effective(tmp_path).proof is FullLevel.COV


def test_unproven_save_removes_the_marker(tmp_path: Path) -> None:
    """Recording no proof removes the marker, and a missing one is fine."""
    _seed_project(tmp_path)
    _save(tmp_path, FullLevel.PASS)
    _save(tmp_path, None)
    assert not snapshot.marker_path(tmp_path).exists()
    _save(tmp_path, None)
    assert _effective(tmp_path).proof is None


def test_legacy_root_marker_moves_into_the_home_as_no_proof(tmp_path: Path) -> None:
    """A one-line digest an older walk left at the root proves nothing now."""
    _seed_project(tmp_path)
    legacy = tmp_path / snapshot.MARKER_FILE_NAME
    legacy.write_text(f"{snapshot.source_digest(tmp_path)}\n", encoding="utf-8")
    assert _effective(tmp_path).proof is None
    assert not legacy.exists()
    assert snapshot.marker_path(tmp_path).is_file()


def test_unusable_home_means_no_proof_and_no_write(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A root whose artifact home cannot be prepared has no proof, and saving logs."""
    not_a_dir = tmp_path / "blocker"
    not_a_dir.write_text("x\n", encoding="utf-8")
    assert _effective(not_a_dir).proof is None
    with caplog.at_level(logging.INFO, logger="groundhog"):
        _save(not_a_dir, FullLevel.COV)
    assert "could not record the proof marker" in caplog.text


def test_unreadable_marker_means_no_proof(tmp_path: Path) -> None:
    """A non-UTF-8 marker reads as no proof, the safe direction."""
    _seed_project(tmp_path)
    snapshot.marker_path(tmp_path).write_bytes(b"\xff\xfe")
    assert _effective(tmp_path).proof is None


# eof
