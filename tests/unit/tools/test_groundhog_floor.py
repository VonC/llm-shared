"""Unit tests for the two-line groundhog floor file (Step 3, Q38, Q40).

Cover the override read (line 2 only, line 1 never read for gating, Q48), the
active-floor resolution (override first, else the freshly computed auto, Q48),
the atomic two-line round-trip, the ``-1`` no-override sentinel, and the safe
fallbacks of a missing, partial, malformed or binary file -- none of which may
crash the run (Q45).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.groundhog import floor

if TYPE_CHECKING:
    from pathlib import Path

# This run's freshly computed auto floor, the k * median of Q46.
_AUTO = 2.5
# A stale line-1 auto from a previous run: it must never be read for gating.
_STALE_AUTO = 9.9
# A positive user override that replaces the auto floor (Q43).
_OVERRIDE = 5.0


def test_missing_file_has_no_override(tmp_path: Path) -> None:
    """No file means no override, so the active floor is this run's auto."""
    assert floor.read_floor(tmp_path) is None
    assert floor.active_floor(None, _AUTO) == _AUTO


def test_minus_one_resolves_to_the_fresh_auto(tmp_path: Path) -> None:
    """Override -1 gates on this run's auto, never the stale line 1 (Q48)."""
    floor.write_floor(tmp_path, auto=_STALE_AUTO, override=floor.NO_OVERRIDE)
    override = floor.read_floor(tmp_path)
    # Arrange / Act above; the stale line 1 must not leak into the resolution.
    assert override is None
    assert floor.active_floor(override, _AUTO) == _AUTO


def test_positive_override_replaces_the_auto(tmp_path: Path) -> None:
    """A positive line 2 is the active floor, over the auto value (Q43)."""
    floor.write_floor(tmp_path, auto=_AUTO, override=_OVERRIDE)
    override = floor.read_floor(tmp_path)
    assert override == _OVERRIDE
    assert floor.active_floor(override, _AUTO) == _OVERRIDE


def test_write_floor_round_trips_both_lines(tmp_path: Path) -> None:
    """The atomic write lands both lines and leaves no side file behind."""
    floor.write_floor(tmp_path, auto=_AUTO, override=_OVERRIDE)
    side = floor.floor_path(tmp_path).with_name(f"{floor.FLOOR_FILE}.tmp")
    # The side-file replace must leave nothing half-written behind.
    assert not side.exists()
    text = floor.floor_path(tmp_path).read_text(encoding="utf-8")
    assert text.splitlines() == [str(_AUTO), str(_OVERRIDE)]
    assert floor.read_floor(tmp_path) == _OVERRIDE


def test_partial_file_falls_back_to_auto(tmp_path: Path) -> None:
    """A one-line file has no override line, so the auto floor is used."""
    floor.floor_path(tmp_path).write_text(f"{_AUTO}\n", encoding="utf-8")
    assert floor.read_floor(tmp_path) is None
    assert floor.active_floor(floor.read_floor(tmp_path), _AUTO) == _AUTO


def test_malformed_override_falls_back_to_auto(tmp_path: Path) -> None:
    """A non-numeric line 2 never crashes; the auto floor is used (Q45)."""
    floor.floor_path(tmp_path).write_text(f"{_AUTO}\nslow\n", encoding="utf-8")
    assert floor.read_floor(tmp_path) is None


def test_binary_file_falls_back_to_auto(tmp_path: Path) -> None:
    """A non-UTF-8 file reads as no override, the safe direction (Q45)."""
    floor.floor_path(tmp_path).write_bytes(b"\xff\xfe")
    assert floor.read_floor(tmp_path) is None


def test_active_floor_ignores_a_negative_override() -> None:
    """A negative override resolves to the auto floor, defensively (Q48)."""
    assert floor.active_floor(floor.NO_OVERRIDE, _AUTO) == _AUTO


def test_write_failure_is_logged_not_raised(tmp_path: Path) -> None:
    """A write onto a non-directory root is logged, never raised (Q45)."""
    not_a_dir = tmp_path / "blocker"
    not_a_dir.write_text("x\n", encoding="utf-8")
    # A file standing where the root should be makes the side write fail.
    floor.write_floor(not_a_dir, auto=_AUTO, override=floor.NO_OVERRIDE)
    assert floor.floor_path(not_a_dir).exists() is False


# eof
