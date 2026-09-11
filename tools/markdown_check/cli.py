"""Platform-neutral command-line and stream boundary for markdown-check."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tools.markdown_check.runner import CheckerRunner

if TYPE_CHECKING:
    from collections.abc import Sequence


def _parser() -> argparse.ArgumentParser:
    """Build the non-interactive direct checker interface."""
    parser = argparse.ArgumentParser(prog="markdown-check")
    parser.add_argument("--root", default=".")
    parser.add_argument("--config")
    parser.add_argument("--baseline")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the checker once and write its stable output streams."""
    args = _parser().parse_args(argv)
    root = Path(args.root).resolve()
    policy_path = None if args.config is None else Path(args.config).resolve()
    baseline_path = None if args.baseline is None else Path(args.baseline).resolve()
    result = CheckerRunner(root).run(
        policy_path=policy_path,
        baseline_path=baseline_path,
    )
    for line in result.stdout:
        sys.stdout.write(f"{line}\n")
    for line in result.stderr:
        sys.stderr.write(f"{line}\n")
    return result.exit_code


if __name__ == "__main__":  # pragma: no cover - thin module boundary
    raise SystemExit(main())


# eof
