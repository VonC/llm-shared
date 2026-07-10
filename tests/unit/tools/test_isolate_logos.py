"""Tests for the logo-sheet isolation tool.

Cover the grid-edge math, the --names spec parsing, the content bounding
box with its border-bleed rejection, the square padding, the border flood
fill that preserves white inside the artwork, the pixel accessor guard,
the CLI argument defaults, the logging setup, and the end-to-end main run
writing both PNG versions of every kept cell.

Coverage fix: the `__main__` guard is now exercised through
`runpy.run_path`, so the script entry (logging setup plus SystemExit with
the main() exit code) is part of the tested surface.
"""

from __future__ import annotations

import logging
import runpy
import sys
from pathlib import Path

import pytest
from PIL import Image

from tools.isolate_logos import isolate_logos

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 30, 30)

# Content pixels of a 20x20 cell holding a 10x10 blob at (5, 5).
EXPECTED_CENTER_BBOX = (5, 5, 15, 15)
# A blob covering (0, 0)-(10, 10) touches the border and is still the logo.
EXPECTED_BORDER_BBOX = (0, 0, 10, 10)
# Uniform thirds of a 90-pixel side.
EXPECTED_UNIFORM_EDGES = [0, 30, 60, 90]
# Interior fractions 0.3 and 0.7 of a 100-pixel side.
EXPECTED_SPLIT_EDGES = [0, 30, 70, 100]
# A 10-pixel-wide logo padded with a 0.1 margin lands on a 12-pixel square.
EXPECTED_PADDED_SIDE = 12
# Fully opaque and fully transparent alpha channel values.
ALPHA_OPAQUE = 255
ALPHA_CLEAR = 0
# parse_args defaults.
DEFAULT_PREFIX = "logo"
DEFAULT_MARGIN = 0.06
DEFAULT_WHITE_THRESHOLD = 242


def _paint(img: Image.Image, box: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
    """Fill the (left, top, right, bottom) exclusive box with one color."""
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            img.putpixel((x, y), color)


def _cell(size: tuple[int, int], boxes: list[tuple[tuple[int, int, int, int], tuple[int, int, int]]]) -> Image.Image:
    """White RGB canvas of `size` with each (box, color) painted on it."""
    img = Image.new("RGB", size, WHITE)
    for box, color in boxes:
        _paint(img, box, color)
    return img


class TestGridEdges:
    """Cover the uniform and fraction-driven grid edge computation."""

    def test_uniform_edges_split_the_side_evenly(self) -> None:
        """Without splits, the side divides into equal integer bands."""
        assert isolate_logos.grid_edges(90, 3, "") == EXPECTED_UNIFORM_EDGES

    def test_split_fractions_place_the_interior_edges(self) -> None:
        """Interior fractions become pixel positions between 0 and the side."""
        assert isolate_logos.grid_edges(100, 3, "0.3,0.7") == EXPECTED_SPLIT_EDGES

    def test_wrong_fraction_count_is_rejected(self) -> None:
        """A splits list not matching count-1 raises the tool error."""
        with pytest.raises(isolate_logos.IsolateLogosError, match="expected 2 split fractions"):
            isolate_logos.grid_edges(100, 3, "0.5")


class TestCellNames:
    """Cover the --names spec parsing."""

    def test_plain_name_gets_the_prefix(self) -> None:
        """A bare name maps to (name, prefix-name)."""
        assert isolate_logos.cell_names("ship", "logo-x") == [("ship", "logo-x-ship")]

    def test_dash_skips_a_cell(self) -> None:
        """A '-' entry yields None so the cell is skipped."""
        assert isolate_logos.cell_names("a,-,b", "p") == [
            ("a", "p-a"),
            None,
            ("b", "p-b"),
        ]

    def test_equals_overrides_the_output_base(self) -> None:
        """A name=basename entry keeps the name and takes the base as-is."""
        assert isolate_logos.cell_names(" combined = logo-all ", "p") == [("combined", "logo-all")]

    def test_empty_entry_is_rejected(self) -> None:
        """An empty entry in the spec raises the tool error."""
        with pytest.raises(isolate_logos.IsolateLogosError, match="empty cell name"):
            isolate_logos.cell_names("a,,b", "p")


class TestRgbAt:
    """Cover the typed pixel accessor guard."""

    def test_multi_band_pixel_is_returned(self) -> None:
        """An RGB image yields its channel tuple."""
        img = Image.new("RGB", (2, 2), RED)
        assert isolate_logos._rgb_at(img, 1, 1) == RED

    def test_single_band_image_is_rejected(self) -> None:
        """A grayscale image raises the tool error instead of misreading."""
        img = Image.new("L", (2, 2), 0)
        with pytest.raises(isolate_logos.IsolateLogosError, match="multi-band"):
            isolate_logos._rgb_at(img, 0, 0)


class TestContentBbox:
    """Cover the content bounding box and its border-bleed rejection."""

    def test_center_blob_bbox_is_found(self) -> None:
        """A single interior blob yields its exact bounding box."""
        img = _cell((20, 20), [(EXPECTED_CENTER_BBOX, BLACK)])
        assert isolate_logos.content_bbox(img, DEFAULT_WHITE_THRESHOLD) == EXPECTED_CENTER_BBOX

    def test_border_sliver_is_ignored(self) -> None:
        """A small border-touching component is bleed and stays out of the bbox."""
        img = _cell((20, 20), [(EXPECTED_CENTER_BBOX, BLACK), ((0, 8, 2, 12), RED)])
        assert isolate_logos.content_bbox(img, DEFAULT_WHITE_THRESHOLD) == EXPECTED_CENTER_BBOX

    def test_large_border_component_is_kept(self) -> None:
        """The largest component is the logo even when it touches the border."""
        img = _cell((20, 20), [(EXPECTED_BORDER_BBOX, BLACK)])
        assert isolate_logos.content_bbox(img, DEFAULT_WHITE_THRESHOLD) == EXPECTED_BORDER_BBOX

    def test_background_only_cell_is_rejected(self) -> None:
        """An all-white cell raises the tool error naming the situation."""
        img = Image.new("RGB", (8, 8), WHITE)
        with pytest.raises(isolate_logos.IsolateLogosError, match="only background"):
            isolate_logos.content_bbox(img, DEFAULT_WHITE_THRESHOLD)


class TestPadSquare:
    """Cover the square canvas padding."""

    def test_image_lands_centered_on_a_square(self) -> None:
        """A landscape image pads to a margin-scaled square, content centered."""
        img = Image.new("RGBA", (10, 4), (*BLACK, ALPHA_OPAQUE))
        padded = isolate_logos.pad_square(img, 0.1, (*WHITE, ALPHA_OPAQUE))
        assert padded.size == (EXPECTED_PADDED_SIDE, EXPECTED_PADDED_SIDE)
        assert padded.getpixel((0, 0)) == (*WHITE, ALPHA_OPAQUE)
        assert padded.getpixel((EXPECTED_PADDED_SIDE // 2, EXPECTED_PADDED_SIDE // 2)) == (
            *BLACK,
            ALPHA_OPAQUE,
        )


class TestMakeTransparent:
    """Cover the border flood fill preserving interior white."""

    def test_background_clears_and_interior_white_survives(self) -> None:
        """Border-connected white goes to alpha 0; enclosed white stays opaque."""
        img = _cell((12, 12), [((3, 3, 9, 9), RED)])
        _paint(img, (5, 5, 7, 7), WHITE)
        result = isolate_logos.make_transparent(img, DEFAULT_WHITE_THRESHOLD)

        corner = isolate_logos._rgb_at(result, 0, 0)
        assert corner[3] == ALPHA_CLEAR
        ring = isolate_logos._rgb_at(result, 3, 3)
        assert ring == (*RED, ALPHA_OPAQUE)
        hole = isolate_logos._rgb_at(result, 5, 5)
        assert hole == (*WHITE, ALPHA_OPAQUE)


class TestParseArgs:
    """Cover the CLI argument parsing and its defaults."""

    def test_defaults_are_applied(self) -> None:
        """Only the required arguments are needed; the rest have defaults."""
        args = isolate_logos.parse_args(
            ["sheet.png", "--out-dir", "out", "--cols", "3", "--names", "a,b,c"],
        )
        assert args.sheet == "sheet.png"
        assert args.prefix == DEFAULT_PREFIX
        assert args.margin == DEFAULT_MARGIN
        assert args.white_threshold == DEFAULT_WHITE_THRESHOLD
        assert args.col_splits == ""
        assert args.row_splits == ""


class TestConfigureLogging:
    """Cover the message-only stdout logging setup."""

    def test_root_logger_gets_one_stdout_handler(self) -> None:
        """The root logger ends with one INFO-level message-only handler."""
        root_logger = logging.getLogger()
        saved_handlers = list(root_logger.handlers)
        saved_level = root_logger.level
        try:
            isolate_logos._configure_logging()
            assert len(root_logger.handlers) == 1
            assert root_logger.level == logging.INFO
        finally:
            root_logger.handlers.clear()
            for handler in saved_handlers:
                root_logger.addHandler(handler)
            root_logger.setLevel(saved_level)


class TestMain:
    """Cover the end-to-end sheet split."""

    def _sheet(self) -> Image.Image:
        """A 40x20 two-cell sheet: black square left, red square right."""
        return _cell((40, 20), [((5, 5, 15, 15), BLACK), ((25, 5, 35, 15), RED)])

    def test_main_writes_both_versions_of_each_kept_cell(self, tmp_path: Path) -> None:
        """Named and renamed cells produce opaque and transparent PNG files."""
        sheet_path = tmp_path / "sheet.png"
        self._sheet().save(sheet_path)
        out_dir = tmp_path / "assets"

        exit_code = isolate_logos.main(
            [
                str(sheet_path),
                "--out-dir",
                str(out_dir),
                "--cols",
                "2",
                "--names",
                "alpha,beta=custom-beta",
                "--prefix",
                "logo-test",
            ],
        )

        assert exit_code == 0
        produced = sorted(p.name for p in out_dir.iterdir())
        assert produced == [
            "custom-beta-transparent.png",
            "custom-beta.png",
            "logo-test-alpha-transparent.png",
            "logo-test-alpha.png",
        ]
        opaque = Image.open(out_dir / "logo-test-alpha.png")
        assert opaque.mode == "RGB"
        transparent = Image.open(out_dir / "custom-beta-transparent.png")
        assert transparent.mode == "RGBA"
        # The 10px content pastes at (0, 0) of the 11px canvas, so only the
        # bottom-right corner is guaranteed to be padding background.
        side = transparent.size[0]
        corner = isolate_logos._rgb_at(transparent, side - 1, side - 1)
        assert corner[3] == ALPHA_CLEAR
        center = isolate_logos._rgb_at(transparent, side // 2, side // 2)
        assert center == (*RED, ALPHA_OPAQUE)

    def test_main_skips_dash_cells(self, tmp_path: Path) -> None:
        """A '-' cell is not processed, so an empty cell cannot fail the run."""
        sheet_path = tmp_path / "sheet.png"
        _cell((40, 20), [((5, 5, 15, 15), BLACK)]).save(sheet_path)
        out_dir = tmp_path / "assets"

        exit_code = isolate_logos.main(
            [
                str(sheet_path),
                "--out-dir",
                str(out_dir),
                "--cols",
                "2",
                "--names",
                "alpha,-",
            ],
        )

        assert exit_code == 0
        produced = sorted(p.name for p in out_dir.iterdir())
        assert produced == ["logo-alpha-transparent.png", "logo-alpha.png"]


class TestMainGuard:
    """Cover the `__main__` guard: logging setup and SystemExit code."""

    def test_script_runs_as_main(self, monkeypatch: pytest.MonkeyPatch,
                                 tmp_path: Path) -> None:
        """Running the file as a script configures logging and exits 0."""
        sheet_path = tmp_path / "sheet.png"
        _cell((20, 20), [((5, 5, 15, 15), BLACK)]).save(sheet_path)
        out_dir = tmp_path / "assets"
        monkeypatch.setattr(sys, "argv", [
            "isolate_logos.py", str(sheet_path), "--out-dir", str(out_dir),
            "--cols", "1", "--names", "solo",
        ])
        root_logger = logging.getLogger()
        saved_handlers = list(root_logger.handlers)
        saved_level = root_logger.level
        try:
            with pytest.raises(SystemExit) as excinfo:
                runpy.run_path(str(Path(isolate_logos.__file__)),
                               run_name="__main__")
            assert excinfo.value.code == 0
        finally:
            root_logger.handlers.clear()
            for handler in saved_handlers:
                root_logger.addHandler(handler)
            root_logger.setLevel(saved_level)
        produced = sorted(p.name for p in out_dir.iterdir())
        assert produced == ["logo-solo-transparent.png", "logo-solo.png"]


# eof
