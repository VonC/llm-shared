"""Unit tests for the ghog day source snapshot (Q28).

Cover the digest stability and sensitivity (touch, add, remove,
excluded folders, gate configuration files), the marker round-trip, and
the safe directions of ``is_unchanged`` (no marker, mismatch,
unreadable marker).

Fix: the marker lives in the artifact home (``.reviews`` by default), not at
the project root; a root marker left by an older walk is moved there on first
use, and a home that cannot be prepared reads as changed.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tools.groundhog import snapshot

if TYPE_CHECKING:
    from pathlib import Path


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


def test_marker_round_trip(tmp_path: Path) -> None:
    """A written marker reads back as unchanged until a file moves."""
    source = _seed_project(tmp_path)
    assert snapshot.is_unchanged(tmp_path) is False
    path = snapshot.write_marker(tmp_path)
    assert path == tmp_path.resolve() / ".reviews" / snapshot.MARKER_FILE_NAME
    assert not (tmp_path / snapshot.MARKER_FILE_NAME).exists()
    assert snapshot.is_unchanged(tmp_path) is True
    _touch(source, 3_000_000_000)
    assert snapshot.is_unchanged(tmp_path) is False


def test_legacy_root_marker_moves_into_the_home(tmp_path: Path) -> None:
    """A marker an older walk left at the root still proves the noop."""
    _seed_project(tmp_path)
    legacy = tmp_path / snapshot.MARKER_FILE_NAME
    legacy.write_text(f"{snapshot.source_digest(tmp_path)}\n", encoding="utf-8")
    assert snapshot.is_unchanged(tmp_path) is True
    assert not legacy.exists()
    assert snapshot.marker_path(tmp_path).is_file()


def test_unusable_home_means_walk_again(tmp_path: Path) -> None:
    """A root whose artifact home cannot be prepared reads as changed."""
    not_a_dir = tmp_path / "blocker"
    not_a_dir.write_text("x\n", encoding="utf-8")
    assert snapshot.is_unchanged(not_a_dir) is False


def test_unreadable_marker_means_walk_again(tmp_path: Path) -> None:
    """A non-UTF-8 marker reads as changed, the safe direction."""
    _seed_project(tmp_path)
    snapshot.marker_path(tmp_path).write_bytes(b"\xff\xfe")
    assert snapshot.is_unchanged(tmp_path) is False


# eof
