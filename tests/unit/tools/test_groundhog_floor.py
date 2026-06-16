"""Unit tests for the two-line groundhog floor file (Step 3, Q38, Q40).

Cover the line-2 read (line 1 never read for gating, Q48), the active-floor
resolution (the override when set, else the one-second default, Q48), the
atomic two-line round-trip, the one-second default seeded for a fresh or
below-zero line 2, an explicit zero that switches the gate off, and the safe
fallbacks of a missing, partial, malformed or binary file -- none of which may
crash the run (Q45).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.groundhog import floor

if TYPE_CHECKING:
    from pathlib import Path

# This run's freshly computed auto floor, the k * median of Q46, written to
# line 1 as a record only; it must never leak into the active floor (Q48).
_AUTO = 2.5
# A stale line-1 auto from a previous run: it must never be read for gating.
_STALE_AUTO = 9.9
# A positive user override that replaces the one-second default (Q43).
_OVERRIDE = 5.0
# A below-zero line 2: it reads as unset, so the default floor is used (Q48).
_BELOW_ZERO = -1.0


def test_missing_file_resolves_to_the_default_floor(tmp_path: Path) -> None:
    """No file means no override, so the gate uses the one-second default."""
    assert floor.read_floor(tmp_path) is None
    assert floor.active_floor(None) == floor.DEFAULT_FLOOR


def test_below_zero_line_two_resolves_to_the_default(tmp_path: Path) -> None:
    """A below-zero line 2 reads as unset and gates on the default (Q48)."""
    floor.write_floor(tmp_path, auto=_STALE_AUTO, override=_BELOW_ZERO)
    override = floor.read_floor(tmp_path)
    # The stale line 1 must not leak in, and below-zero must not gate.
    assert override is None
    assert floor.active_floor(override) == floor.DEFAULT_FLOOR


def test_default_floor_round_trips_as_one_second(tmp_path: Path) -> None:
    """The seeded one-second default reads back and gates at one second."""
    floor.write_floor(tmp_path, auto=_AUTO, override=floor.DEFAULT_FLOOR)
    override = floor.read_floor(tmp_path)
    assert override == floor.DEFAULT_FLOOR
    assert floor.active_floor(override) == floor.DEFAULT_FLOOR


def test_positive_override_replaces_the_default(tmp_path: Path) -> None:
    """A positive line 2 is the active floor, over the one-second default (Q43)."""
    floor.write_floor(tmp_path, auto=_AUTO, override=_OVERRIDE)
    override = floor.read_floor(tmp_path)
    assert override == _OVERRIDE
    assert floor.active_floor(override) == _OVERRIDE


def test_zero_override_switches_the_gate_off(tmp_path: Path) -> None:
    """An explicit zero line 2 is honoured, the by-hand off switch (Q41)."""
    floor.write_floor(tmp_path, auto=_AUTO, override=0.0)
    override = floor.read_floor(tmp_path)
    # Zero is a real override, not unset: it spares every call downstream.
    assert override == 0.0
    assert floor.active_floor(override) == 0.0


def test_write_floor_round_trips_both_lines(tmp_path: Path) -> None:
    """The atomic write lands both lines and leaves no side file behind."""
    floor.write_floor(tmp_path, auto=_AUTO, override=_OVERRIDE)
    side = floor.floor_path(tmp_path).with_name(f"{floor.FLOOR_FILE}.tmp")
    # The side-file replace must leave nothing half-written behind.
    assert not side.exists()
    text = floor.floor_path(tmp_path).read_text(encoding="utf-8")
    assert text.splitlines() == [str(_AUTO), str(_OVERRIDE)]
    assert floor.read_floor(tmp_path) == _OVERRIDE


def test_partial_file_resolves_to_the_default_floor(tmp_path: Path) -> None:
    """A one-line file has no override line, so the default floor is used."""
    floor.floor_path(tmp_path).write_text(f"{_AUTO}\n", encoding="utf-8")
    assert floor.read_floor(tmp_path) is None
    assert floor.active_floor(floor.read_floor(tmp_path)) == floor.DEFAULT_FLOOR


def test_malformed_override_resolves_to_the_default(tmp_path: Path) -> None:
    """A non-numeric line 2 never crashes; the default floor is used (Q45)."""
    floor.floor_path(tmp_path).write_text(f"{_AUTO}\nslow\n", encoding="utf-8")
    assert floor.read_floor(tmp_path) is None


def test_binary_file_resolves_to_the_default(tmp_path: Path) -> None:
    """A non-UTF-8 file reads as unset, the safe direction (Q45)."""
    floor.floor_path(tmp_path).write_bytes(b"\xff\xfe")
    assert floor.read_floor(tmp_path) is None


def test_active_floor_ignores_a_negative_override() -> None:
    """A negative override resolves to the default floor, defensively (Q48)."""
    assert floor.active_floor(_BELOW_ZERO) == floor.DEFAULT_FLOOR


def test_write_failure_is_logged_not_raised(tmp_path: Path) -> None:
    """A write onto a non-directory root is logged, never raised (Q45)."""
    not_a_dir = tmp_path / "blocker"
    not_a_dir.write_text("x\n", encoding="utf-8")
    # A file standing where the root should be makes the side write fail.
    floor.write_floor(not_a_dir, auto=_AUTO, override=floor.DEFAULT_FLOOR)
    assert floor.floor_path(not_a_dir).exists() is False


# eof
