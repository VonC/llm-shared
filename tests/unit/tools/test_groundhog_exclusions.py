"""Unit tests for the groundhog ``[exclusion]`` section (Step 1, Q53, Q66).

Cover the read of the tool-managed section -- the empty map for a file with no
section, the parsed map for a well-formed section, a node id with its own ``=``
and spaces kept whole, a malformed entry, a blank line and a comment skipped,
text before the header skipped, and a missing or binary file read as ``{}`` --
and the write path: adds, lowers a baseline and removes entries while
preserving the floor lines (1 and 2), seeds a default floor head when the file
has fewer than two lines, drops the header for an empty map, and survives a
write failure logged not raised (Q53, Q66). Reaches 100% of ``exclusions.py``.

Fix: the floor file lives in the artifact home (``.reviews`` by default); a
root file from an older run is moved there on first use, its recorded
exclusions kept, and a home that cannot be prepared reads as ``{}``.

Step 3 also covers strict read-only evidence: root fallback without migration,
home precedence, rejected malformed durations and encoding, stable listings,
complete saved-listing parsing and comparisons of added or raised baselines.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.groundhog import exclusions, floor

if TYPE_CHECKING:
    from pathlib import Path

# The two floor lines kept above the section: a stale auto record then the
# one-second default; the write must never disturb them (Q53).
_AUTO = "0.0"
_FLOOR = "1.0"
# A well-formed section's two accepted calls, node -> recorded seconds.
_FAST_NODE = "src/pkg/tests/test_auth_pbt.py::TestAuthPBT::test_cookie"
_SLOW_NODE = "src/pkg/tests/test_auth_setup_tdd.py::TestAuthSetup::test_init"
_RECORDED_FAST = 6.80
_RECORDED_SLOW = 11.41
# A parametrized node id carrying its own ``=`` and spaces, kept whole (Q53).
_PARAM_NODE = "tests/test_p.py::test_case[mode = on]"
_RECORDED_PARAM = 3.50


def _write_section(root: Path, *entries: str) -> None:
    """Write the floor lines, the header and given raw entry lines as the file.

    Args:
        root: The project root the floor file lives under.
        entries: Raw lines to place after the ``[exclusion]`` header.
    """
    body = "".join(f"{line}\n" for line in entries)
    text = f"{_AUTO}\n{_FLOOR}\n[exclusion]\n{body}"
    floor.floor_path(root).write_text(text, encoding="utf-8")


def test_missing_file_reads_no_exclusions(tmp_path: Path) -> None:
    """No file means no section, so the read is the empty map (Q53)."""
    assert exclusions.read_exclusions(tmp_path) == {}


def test_file_with_no_section_reads_no_exclusions(tmp_path: Path) -> None:
    """A plain two-line floor file has no header, so the read is empty (Q53)."""
    floor.floor_path(tmp_path).write_text(f"{_AUTO}\n{_FLOOR}\n", encoding="utf-8")
    assert exclusions.read_exclusions(tmp_path) == {}


def test_well_formed_section_parses_to_a_map(tmp_path: Path) -> None:
    """Each ``node = number`` line after the header reads into the map (Q53)."""
    _write_section(
        tmp_path,
        f"{_SLOW_NODE} = {_RECORDED_SLOW}",
        f"{_FAST_NODE} = {_RECORDED_FAST}",
    )
    assert exclusions.read_exclusions(tmp_path) == {
        _SLOW_NODE: _RECORDED_SLOW,
        _FAST_NODE: _RECORDED_FAST,
    }


def test_parametrized_node_with_equals_is_kept_whole(tmp_path: Path) -> None:
    """The split is on the last ``=``, so a param id's own ``=`` survives (Q53)."""
    _write_section(tmp_path, f"{_PARAM_NODE} = {_RECORDED_PARAM}")
    assert exclusions.read_exclusions(tmp_path) == {_PARAM_NODE: _RECORDED_PARAM}


def test_malformed_entry_is_skipped(tmp_path: Path) -> None:
    """A non-numeric value never crashes the read; the entry is dropped (Q53)."""
    _write_section(
        tmp_path,
        f"{_SLOW_NODE} = slow",
        f"{_FAST_NODE} = {_RECORDED_FAST}",
    )
    assert exclusions.read_exclusions(tmp_path) == {_FAST_NODE: _RECORDED_FAST}


def test_blank_comment_and_no_equals_lines_are_skipped(tmp_path: Path) -> None:
    """Blank, comment and ``=``-less lines after the header are skipped (Q53)."""
    _write_section(
        tmp_path,
        "",
        "# a hand-written note",
        "no equals here",
        f"= {_RECORDED_FAST}",
        f"{_FAST_NODE} = {_RECORDED_FAST}",
    )
    # The empty-node ``= 6.80`` line is malformed too, so only the real entry stays.
    assert exclusions.read_exclusions(tmp_path) == {_FAST_NODE: _RECORDED_FAST}


def test_text_before_the_header_is_skipped(tmp_path: Path) -> None:
    """A stray pre-header line cannot be read as an entry; only the floor is there."""
    text = f"{_AUTO}\nstray = 9.9\n{_FLOOR}\n[exclusion]\n{_FAST_NODE} = {_RECORDED_FAST}\n"
    floor.floor_path(tmp_path).write_text(text, encoding="utf-8")
    # ``stray = 9.9`` sits before the header, so it is not an exclusion entry.
    assert exclusions.read_exclusions(tmp_path) == {_FAST_NODE: _RECORDED_FAST}


def test_binary_file_reads_no_exclusions(tmp_path: Path) -> None:
    """A non-UTF-8 file reads as the empty map, the safe direction (Q53)."""
    floor.floor_path(tmp_path).write_bytes(b"\xff\xfe")
    assert exclusions.read_exclusions(tmp_path) == {}


def test_write_adds_entries_and_preserves_the_floor_lines(tmp_path: Path) -> None:
    """The write lands the section and leaves the two floor lines untouched (Q66)."""
    floor.write_floor(tmp_path, auto=float(_AUTO), override=float(_FLOOR))
    exclusions.write_exclusions(
        tmp_path,
        {_SLOW_NODE: _RECORDED_SLOW, _FAST_NODE: _RECORDED_FAST},
    )
    side = floor.floor_path(tmp_path).with_name(f"{floor.FLOOR_FILE}.tmp")
    # The atomic replace must leave no side file behind.
    assert not side.exists()
    lines = floor.floor_path(tmp_path).read_text(encoding="utf-8").splitlines()
    assert lines[:2] == [_AUTO, _FLOOR]
    assert lines[2] == "[exclusion]"
    assert exclusions.read_exclusions(tmp_path) == {
        _SLOW_NODE: _RECORDED_SLOW,
        _FAST_NODE: _RECORDED_FAST,
    }


def test_write_lowers_a_baseline_round_trip(tmp_path: Path) -> None:
    """A smaller recorded value writes back as the new, lower baseline (Q60)."""
    _write_section(tmp_path, f"{_SLOW_NODE} = {_RECORDED_SLOW}")
    lowered = 1.30
    exclusions.write_exclusions(tmp_path, {_SLOW_NODE: lowered})
    assert exclusions.read_exclusions(tmp_path) == {_SLOW_NODE: lowered}


def test_write_removes_an_entry(tmp_path: Path) -> None:
    """Omitting a node from the map removes its entry on the next write (Q61)."""
    _write_section(
        tmp_path,
        f"{_SLOW_NODE} = {_RECORDED_SLOW}",
        f"{_FAST_NODE} = {_RECORDED_FAST}",
    )
    exclusions.write_exclusions(tmp_path, {_FAST_NODE: _RECORDED_FAST})
    assert exclusions.read_exclusions(tmp_path) == {_FAST_NODE: _RECORDED_FAST}


def test_write_empty_map_drops_the_header(tmp_path: Path) -> None:
    """An empty map returns the file to a clean two-line floor file (Q66)."""
    _write_section(tmp_path, f"{_SLOW_NODE} = {_RECORDED_SLOW}")
    exclusions.write_exclusions(tmp_path, {})
    lines = floor.floor_path(tmp_path).read_text(encoding="utf-8").splitlines()
    # No header is left once the last entry is removed.
    assert lines == [_AUTO, _FLOOR]
    assert exclusions.read_exclusions(tmp_path) == {}


def test_write_seeds_a_default_head_when_no_floor_lines(tmp_path: Path) -> None:
    """A write before any full run seeds the default floor head, well-formed (Q66)."""
    # No floor file exists yet, so the head falls back to the default two lines.
    exclusions.write_exclusions(tmp_path, {_FAST_NODE: _RECORDED_FAST})
    lines = floor.floor_path(tmp_path).read_text(encoding="utf-8").splitlines()
    assert lines[:2] == ["0.0", str(floor.DEFAULT_FLOOR)]
    assert lines[2] == "[exclusion]"
    assert exclusions.read_exclusions(tmp_path) == {_FAST_NODE: _RECORDED_FAST}


def test_write_failure_is_logged_not_raised(tmp_path: Path) -> None:
    """A write onto a non-directory root is logged, never raised (Q66)."""
    not_a_dir = tmp_path / "blocker"
    not_a_dir.write_text("x\n", encoding="utf-8")
    # A file standing where the root should be leaves no artifact home to
    # prepare, so the path itself fails before any side write.
    exclusions.write_exclusions(not_a_dir, {_FAST_NODE: _RECORDED_FAST})
    assert not_a_dir.read_text(encoding="utf-8") == "x\n"
    assert exclusions.read_exclusions(not_a_dir) == {}


def test_legacy_root_exclusions_are_moved_not_lost(tmp_path: Path) -> None:
    """Exclusions recorded at the root by an older run survive the move."""
    legacy = tmp_path / floor.FLOOR_FILE
    legacy.write_text(
        f"{_AUTO}\n{_FLOOR}\n[exclusion]\n{_SLOW_NODE} = {_RECORDED_SLOW}\n",
        encoding="utf-8",
    )
    assert exclusions.read_exclusions(tmp_path) == {_SLOW_NODE: _RECORDED_SLOW}
    assert not legacy.exists()
    home_file = tmp_path.resolve() / ".reviews" / floor.FLOOR_FILE
    exclusions.write_exclusions(
        tmp_path,
        {_SLOW_NODE: _RECORDED_SLOW, _FAST_NODE: _RECORDED_FAST},
    )
    assert home_file.read_text(encoding="utf-8").splitlines()[:3] == [
        _AUTO,
        _FLOOR,
        "[exclusion]",
    ]
    assert not legacy.exists()


def test_strict_missing_file_does_not_create_home(tmp_path: Path) -> None:
    """Absent evidence is empty and the strict reader creates no directory."""
    assert exclusions.read_exclusions_strict(tmp_path) == {}
    assert not (tmp_path / ".reviews").exists()


def test_strict_legacy_read_does_not_migrate(tmp_path: Path) -> None:
    """A legacy file supplies evidence without moving it into the home."""
    legacy = tmp_path / floor.FLOOR_FILE
    legacy.write_text(f"0.0\n1.0\n[exclusion]\n{_PARAM_NODE} = 3.5\n", encoding="utf-8")
    assert exclusions.read_exclusions_strict(tmp_path) == {_PARAM_NODE: _RECORDED_PARAM}
    assert legacy.exists()
    assert not (tmp_path / ".reviews").exists()


def test_strict_home_wins_and_skips_comments(tmp_path: Path) -> None:
    """The home file wins over a legacy copy, with comments and blanks ignored."""
    legacy = tmp_path / floor.FLOOR_FILE
    legacy.write_text("invalid legacy evidence", encoding="utf-8")
    artifact_home = tmp_path / ".reviews"
    artifact_home.mkdir()
    (artifact_home / floor.FLOOR_FILE).write_text(
        f"0.0\n1.0\n[exclusion]\n\n# note\n{_FAST_NODE} = {_RECORDED_FAST}\n", encoding="utf-8",
    )
    assert exclusions.read_exclusions_strict(tmp_path) == {_FAST_NODE: _RECORDED_FAST}
    assert legacy.read_text(encoding="utf-8") == "invalid legacy evidence"


def test_strict_missing_section_is_empty(tmp_path: Path) -> None:
    """Floor-only evidence contains no accepted exceptions."""
    (tmp_path / floor.FLOOR_FILE).write_text("0.0\n1.0\n", encoding="utf-8")
    assert exclusions.read_exclusions_strict(tmp_path) == {}


@pytest.mark.parametrize("entry", ["broken", "= 1", "test = invalid", "test = nan", "test = inf", "test = -1"])
def test_strict_reader_rejects_malformed_entries(tmp_path: Path, entry: str) -> None:
    """Invalid or non-finite durations cannot become accepted evidence."""
    (tmp_path / floor.FLOOR_FILE).write_text(f"0.0\n1.0\n[exclusion]\n{entry}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="malformed exclusion entry"):
        exclusions.read_exclusions_strict(tmp_path)


def test_strict_reader_rejects_binary_file(tmp_path: Path) -> None:
    """Unreadable encoding must not silently read as no exceptions."""
    (tmp_path / floor.FLOOR_FILE).write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        exclusions.read_exclusions_strict(tmp_path)


def test_listing_order_count_and_round_trip() -> None:
    """Listings order node ids, retain parameter equals and verify their count."""
    entries = {"z_test": 1.0, _PARAM_NODE: _RECORDED_PARAM, "a_test": 0.0}
    lines = exclusions.listing_lines(entries)
    assert lines == ["a_test = 0.0", f"{_PARAM_NODE} = 3.5", "z_test = 1.0", "exclusions=3"]
    assert exclusions.parse_listing("\n".join(lines) + "\n") == entries
    assert exclusions.listing_lines({}) == ["exclusions=0"]
    assert exclusions.parse_listing("exclusions=0\n") == {}


@pytest.mark.parametrize(("text", "message"), [
    ("test = 1\ntest = 2\nexclusions=2", "duplicate exclusion entry"),
    ("", "missing or invalid exclusion count"),
    ("test = 1", "missing or invalid exclusion count"),
    ("test = 1\nexclusions=0", "missing or invalid exclusion count"),
    ("test = nan\nexclusions=1", "malformed exclusion entry"),
])
def test_listing_parser_rejects_incomplete_or_ambiguous_evidence(text: str, message: str) -> None:
    """Duplicate entries and incomplete or malformed saved output are refused."""
    with pytest.raises(ValueError, match=message):
        exclusions.parse_listing(text)


def test_listing_comparison_reports_only_added_or_raised() -> None:
    """Lowered, unchanged and removed exceptions are absent from the changes."""
    saved = {"raised": 1.0, "lowered": 2.0, "unchanged": 3.0, "removed": 4.0}
    current = {"raised": 2.0, "lowered": 1.0, "unchanged": 3.0, "added": 0.0}
    assert exclusions.compare_listings(saved, current) == {"raised": 2.0, "added": 0.0}


# eof
