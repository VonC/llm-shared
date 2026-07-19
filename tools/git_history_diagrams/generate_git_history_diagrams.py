#!/usr/bin/env python3
"""Generate or verify the canonical prepare-release SVG diagrams."""

from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if __name__ == "__main__":  # pragma: no cover - script bootstrap
    with contextlib.suppress(Exception):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from tools.git_history_diagrams.scenarios import prepare_release_scenarios
from tools.git_history_diagrams.svg_renderer import render_svg

if TYPE_CHECKING:
    from collections.abc import Sequence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).parent.parent.parent / "wiki" / "assets" / "prepare-release"
    parser.add_argument("--output-dir", type=Path, default=default)
    parser.add_argument("--check", action="store_true", help="Fail if an SVG is missing or stale.")
    parser.add_argument("--list", action="store_true", help="List scenario slugs without writing files.")
    return parser


def _check(destination: Path, expected: str) -> bool:
    return destination.is_file() and destination.read_text(encoding="utf-8") == expected


def main(argv: Sequence[str] | None = None) -> int:
    """Generate diagrams, or verify that committed diagrams are current."""
    args = _parser().parse_args(argv)
    scenarios = prepare_release_scenarios()
    if args.list:
        sys.stdout.write("\n".join(scenario.slug for scenario in scenarios) + "\n")
        return 0
    output_dir = args.output_dir.resolve()
    stale: list[str] = []
    if not args.check:
        output_dir.mkdir(parents=True, exist_ok=True)
    for scenario in scenarios:
        destination = output_dir / f"{scenario.slug}.svg"
        rendered = render_svg(scenario)
        if args.check:
            if not _check(destination, rendered):
                stale.append(destination.name)
        else:
            destination.write_text(rendered, encoding="utf-8")
            sys.stdout.write(f"Wrote {destination}\n")
    if stale:
        sys.stderr.write("Missing or stale diagrams: " + ", ".join(stale) + "\n")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())


# eof
