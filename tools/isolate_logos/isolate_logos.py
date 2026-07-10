"""Isolate individual logos from a generated logo sheet.

Splits a sheet image (a uniform grid of logos on a near-white background)
into cells, auto-crops each logo to its content, pads it to a square
canvas, and writes two files per logo: an opaque version on white and a
transparent version where the background is flood-filled to alpha 0 from
the borders (white areas inside the artwork are preserved).

Usage:
  uv run --with pillow python isolate_logos.py SHEET.png \
      --out-dir wiki/assets --cols 3 \
      --names download,bridge,forge,-,ship,combined=logo-cplx \
      --prefix logo-cplx

Names are given in reading order (row-major), one per grid cell:
  - "name"          -> <prefix>-<name>.png and <prefix>-<name>-transparent.png
  - "name=basename" -> basename.png and basename-transparent.png
  - "-"             -> skip that cell (duplicate or empty)
"""

from __future__ import annotations

import argparse
import logging
import math
import sys
from collections import deque
from pathlib import Path

from PIL import Image

LOGGER = logging.getLogger("isolate_logos")

# A border-touching component smaller than this fraction of the largest
# component is bleed from a neighboring logo, not part of this cell's logo.
BLEED_FRACTION = 0.25


class IsolateLogosError(ValueError):
    """Raised when the sheet, the names spec, or a cell cannot be processed."""


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the isolate_logos command line into a namespace."""
    parser = argparse.ArgumentParser(
        description="Isolate logos from a grid sheet into per-logo PNG files.",
    )
    parser.add_argument("sheet", help="path of the sheet image (grid of logos)")
    parser.add_argument("--out-dir", required=True, help="output folder for the PNG files")
    parser.add_argument("--cols", type=int, required=True, help="number of grid columns")
    parser.add_argument(
        "--names",
        required=True,
        help="comma-separated cell names in reading order; '-' skips a cell; "
        "'name=basename' overrides the output base name",
    )
    parser.add_argument("--prefix", default="logo", help="output filename prefix (default: logo)")
    parser.add_argument(
        "--margin",
        type=float,
        default=0.06,
        help="square-canvas margin as a fraction of the logo size (default: 0.06)",
    )
    parser.add_argument(
        "--white-threshold",
        type=int,
        default=242,
        help="channel value from which a pixel counts as background white (default: 242)",
    )
    parser.add_argument(
        "--col-splits",
        default="",
        help="comma-separated interior column split positions as width fractions "
        "(cols-1 values, e.g. 0.31,0.70) when the grid columns are not uniform",
    )
    parser.add_argument(
        "--row-splits",
        default="",
        help="comma-separated interior row split positions as height fractions "
        "(rows-1 values) when the grid rows are not uniform",
    )
    return parser.parse_args(argv)


def grid_edges(size: int, count: int, splits: str) -> list[int]:
    """Pixel edges of grid bands: uniform, or from interior split fractions."""
    if not splits:
        return [int(i * size / count) for i in range(count + 1)]
    fractions = [float(f) for f in splits.split(",")]
    if len(fractions) != count - 1:
        msg = f"expected {count - 1} split fractions, got {len(fractions)}"
        raise IsolateLogosError(msg)
    return [0, *(int(f * size) for f in fractions), size]


def _rgb_at(img: Image.Image, x: int, y: int) -> tuple[int, ...]:
    """Channel tuple of one pixel; rejects single-band images."""
    pixel = img.getpixel((x, y))
    if not isinstance(pixel, tuple):
        msg = f"expected a multi-band image, got pixel {pixel!r} at ({x}, {y})"
        raise IsolateLogosError(msg)
    return pixel


def _is_content(img: Image.Image, x: int, y: int, white_threshold: int) -> bool:
    """Whether the pixel belongs to the artwork, not the near-white background."""
    return any(channel < white_threshold for channel in _rgb_at(img, x, y)[:3])


def _flood_component(
    img: Image.Image,
    start: tuple[int, int],
    labeled: list[list[bool]],
    white_threshold: int,
) -> tuple[int, tuple[int, int, int, int], bool]:
    """Grow one connected content component from `start` (4-connectivity).

    Returns its pixel count, its bounding box, and whether it touches the
    cell border. `labeled` marks visited pixels across calls.
    """
    w, h = img.size
    sx, sy = start
    count, touches = 0, False
    minx, miny, maxx, maxy = sx, sy, sx, sy
    queue = deque([start])
    labeled[sy][sx] = True
    while queue:
        x, y = queue.popleft()
        count += 1
        if x in (0, w - 1) or y in (0, h - 1):
            touches = True
        minx, maxx = min(minx, x), max(maxx, x)
        miny, maxy = min(miny, y), max(maxy, y)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (
                0 <= nx < w
                and 0 <= ny < h
                and not labeled[ny][nx]
                and _is_content(img, nx, ny, white_threshold)
            ):
                labeled[ny][nx] = True
                queue.append((nx, ny))
    return count, (minx, miny, maxx + 1, maxy + 1), touches


def _kept_union_bbox(
    components: list[tuple[int, tuple[int, int, int, int], bool]],
) -> tuple[int, int, int, int]:
    """Union bbox of the components once border-touching bleed is dropped.

    The largest component is always kept, so the union is never empty.
    """
    largest = max(count for count, _, _ in components)
    kept = [
        bbox
        for count, bbox, touches in components
        if not (touches and count < BLEED_FRACTION * largest)
    ]
    return (
        min(b[0] for b in kept),
        min(b[1] for b in kept),
        max(b[2] for b in kept),
        max(b[3] for b in kept),
    )


def content_bbox(img: Image.Image, white_threshold: int) -> tuple[int, int, int, int]:
    """Bounding box of the logo pixels of an RGB cell image.

    Non-background pixels are grouped into connected components. A small
    component touching the cell border is bleed from a neighboring logo
    (the grid cut fell inside the neighbor) and is ignored; everything
    else is part of the logo, whose union bbox is returned.
    """
    w, h = img.size
    labeled = [[False] * w for _ in range(h)]
    # Each component is (pixel_count, bbox, touches_border); the comprehension
    # runs row-major, so `labeled` marks flooded pixels before later seeds.
    components = [
        _flood_component(img, (sx, sy), labeled, white_threshold)
        for sy in range(h)
        for sx in range(w)
        if not labeled[sy][sx] and _is_content(img, sx, sy, white_threshold)
    ]
    if not components:
        msg = "cell contains only background pixels"
        raise IsolateLogosError(msg)
    return _kept_union_bbox(components)


def pad_square(img: Image.Image, margin: float, bg: tuple[int, int, int, int]) -> Image.Image:
    """Center the image on a square canvas with a relative margin."""
    w, h = img.size
    side = int(max(w, h) * (1 + 2 * margin))
    canvas = Image.new("RGBA", (side, side), bg)
    canvas.paste(img, ((side - w) // 2, (side - h) // 2), img)
    return canvas


def _border_seeds(w: int, h: int) -> deque[tuple[int, int]]:
    """Flood-fill queue seeded with every border pixel position."""
    queue: deque[tuple[int, int]] = deque()
    for x in range(w):
        queue.append((x, 0))
        queue.append((x, h - 1))
    for y in range(h):
        queue.append((0, y))
        queue.append((w - 1, y))
    return queue


def make_transparent(img_rgb: Image.Image, white_threshold: int) -> Image.Image:
    """Flood-fill near-white background to alpha 0, seeded from every border pixel.

    Only background connected to the borders becomes transparent, so white
    used inside the artwork survives.
    """
    img = img_rgb.convert("RGBA")
    w, h = img.size
    seen = [[False] * w for _ in range(h)]
    queue = _border_seeds(w, h)
    while queue:
        x, y = queue.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y][x]:
            continue
        seen[y][x] = True
        pixel = _rgb_at(img, x, y)
        if all(channel >= white_threshold for channel in pixel[:3]):
            img.putpixel((x, y), (pixel[0], pixel[1], pixel[2], 0))
            queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return img


def cell_names(spec: str, prefix: str) -> list[tuple[str, str] | None]:
    """Parse the --names spec into (name, output base) pairs; None skips a cell."""
    cells: list[tuple[str, str] | None] = []
    for raw in spec.split(","):
        entry = raw.strip()
        if entry == "-":
            cells.append(None)
        elif "=" in entry:
            name, base = entry.split("=", 1)
            cells.append((name.strip(), base.strip()))
        elif entry:
            cells.append((entry, f"{prefix}-{entry}"))
        else:
            msg = f"empty cell name in --names: {spec!r}"
            raise IsolateLogosError(msg)
    return cells


def main(argv: list[str]) -> int:
    """Split the sheet and write both PNG versions of every kept cell."""
    args = parse_args(argv)
    cols = int(args.cols)
    margin = float(args.margin)
    white_threshold = int(args.white_threshold)
    cells = cell_names(args.names, args.prefix)
    rows = math.ceil(len(cells) / cols)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sheet = Image.open(args.sheet).convert("RGB")
    width, height = sheet.size
    col_edges = grid_edges(width, cols, args.col_splits)
    row_edges = grid_edges(height, rows, args.row_splits)

    for index, cell in enumerate(cells):
        if cell is None:
            continue
        name, base = cell
        col, row = index % cols, index // cols
        box = (col_edges[col], row_edges[row], col_edges[col + 1], row_edges[row + 1])
        logo = sheet.crop(box)
        logo = logo.crop(content_bbox(logo, white_threshold))
        LOGGER.info(
            "%s: cell %s,%s -> content %sx%s -> %s",
            name,
            row,
            col,
            logo.size[0],
            logo.size[1],
            base,
        )

        opaque = pad_square(logo.convert("RGBA"), margin, (255, 255, 255, 255))
        opaque.convert("RGB").save(out_dir / f"{base}.png")

        transparent = pad_square(
            make_transparent(logo, white_threshold), margin, (255, 255, 255, 0),
        )
        transparent.save(out_dir / f"{base}-transparent.png")

    return 0


def _configure_logging() -> None:
    """Configure stdout logging with message-only formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(main(sys.argv[1:]))


# eof
