"""Read-only group validation and strict exclusion evidence commands.

These commands never start a run lifecycle or modify proof and duration
files. Setup and evidence errors consistently return groundhog's exit 5.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tools.groundhog import commands, exclusions, groups, snapshot
from tools.groundhog.models import EXIT_OBJECTIVE_MET, EXIT_SETUP_ERROR

if TYPE_CHECKING:
    from tools.groundhog.context import Invocation


def run_groups(invocation: Invocation) -> int:
    """List all groups or validate the exact requested group.

    Args:
        invocation: The read-only listing invocation.

    Returns:
        Zero for valid groups, five with the resolver's diagnostic otherwise.
    """
    try:
        files = snapshot.source_files(invocation.root)
        scopes = ([groups.resolve_group(invocation.root, invocation.name, files)]
                  if invocation.name is not None else groups.list_groups(invocation.root, files))
    except (OSError, ValueError) as error:
        commands.emit_summary([f"ghog: {error}"])
        return EXIT_SETUP_ERROR
    for scope in scopes:
        commands.emit_summary([
            f"group={scope.name} tests={len(scope.test_files)} sources={len(scope.source_files)}",
            "tests:", *(f"  {pattern}" for pattern in scope.test_patterns),
            "sources:", *(f"  {pattern}" for pattern in scope.source_patterns),
        ])
    return EXIT_OBJECTIVE_MET


def run_exclude_list(invocation: Invocation) -> int:
    """Print a trustworthy exclusion listing or compare one with saved evidence.

    Args:
        invocation: Listing options, optionally naming the saved listing.

    Returns:
        Zero for a verified result; five for unreadable or unverified evidence.
    """
    try:
        current = exclusions.read_exclusions_strict(invocation.root)
        if invocation.since is None:
            lines = exclusions.listing_lines(current)
        else:
            saved = exclusions.parse_listing(Path(invocation.since).read_text(encoding="utf-8"))
            changed = exclusions.compare_listings(saved, current)
            lines = [*exclusions.listing_lines(changed)[:-1],
                     f"exclusions={'changed' if changed else 'unchanged'}"]
    except (OSError, ValueError):
        commands.emit_summary([f"exclusions={'unreadable' if invocation.since is None else 'unverified'}"])
        return EXIT_SETUP_ERROR
    commands.emit_summary(lines)
    return EXIT_OBJECTIVE_MET


# eof
