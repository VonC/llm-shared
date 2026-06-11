"""Unit tests for the ghog day source snapshot (Q28).

Cover the digest stability and sensitivity (touch, add, remove,
excluded folders, gate configuration files), the marker round-trip, and
the safe directions of ``is_unchanged`` (no marker, mismatch,
unreadable marker).
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
    assert path == tmp_path / snapshot.MARKER_FILE_NAME
    assert snapshot.is_unchanged(tmp_path) is True
    _touch(source, 3_000_000_000)
    assert snapshot.is_unchanged(tmp_path) is False


def test_unreadable_marker_means_walk_again(tmp_path: Path) -> None:
    """A non-UTF-8 marker reads as changed, the safe direction."""
    _seed_project(tmp_path)
    snapshot.marker_path(tmp_path).write_bytes(b"\xff\xfe")
    assert snapshot.is_unchanged(tmp_path) is False


# eof
