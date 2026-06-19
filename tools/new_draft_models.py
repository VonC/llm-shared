"""Pure data models and helpers for the `new_draft` effort-scaffolding tool.

The tool asks for a slug, proposes a patch/minor/major bump of the current
version, creates a branch (and optionally a sibling worktree), bumps
`pyproject.toml`, and drops a `docs/draft.vX.Y.Z.<slug>.md` skeleton so a new
development effort starts already isolated.

This module holds the side-effect-free pieces so they stay unit-testable:
semantic-version parsing and bumping, the `pyproject.toml` version read, the
`version.txt` version read used by the `process-draft` flow, slug validation, the
worktree directory-name rule, and the draft skeleton text. Anything that touches
Git, the filesystem, or the terminal lives in the companion modules
(`new_draft_git`, `new_draft_workflow`, `new_draft_prompts`).

Fix: add `read_version_txt` so the `process-draft` instruction and the
`--from-draft` tool mode read the current version from `version.txt` through one
parser (first token of the first line, with a trailing `-SNAPSHOT` dropped),
instead of each restating the rule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime
    from pathlib import Path

# Bump kinds offered in the version menu, least-disruptive first.
BUMP_PARTS: tuple[str, ...] = ("patch", "minor", "major")

# A slug must read as both a Git branch name and a filename component: lowercase
# letters, digits, hyphen, or underscore, starting with a letter or digit.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# The `[project]` version line, anchored to the start of a line so it never
# matches a dependency pin such as `"ty>=0.0.30"`. The version is read only (to
# propose a bump and name the draft); `pyproject.toml` itself is never rewritten.
_VERSION_RE = re.compile(r'(?m)^version\s*=\s*"(?P<version>\d+\.\d+\.\d+)"')

# The trailing pre-release marker dropped from a `version.txt` token before
# parsing, matched case-insensitively so `-SNAPSHOT` and `-snapshot` both go.
_SNAPSHOT_SUFFIX_RE = re.compile(r"-snapshot$", re.IGNORECASE)


class NewDraftError(Exception):
    """Raised for any expected new_draft failure (bad slug, missing version)."""


@dataclass(frozen=True)
class SemanticVersion:
    """A `MAJOR.MINOR.PATCH` version with bump helpers."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, text: str) -> SemanticVersion:
        """Parse a `MAJOR.MINOR.PATCH` string into a SemanticVersion.

        Args:
            text: The version text, for example `0.3.0`.

        Returns:
            The parsed SemanticVersion.

        Raises:
            NewDraftError: When the text is not three dot-separated integers.
        """
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", text.strip())
        if match is None:
            msg = f"Not a MAJOR.MINOR.PATCH version: {text!r}"
            raise NewDraftError(msg)
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def bumped(self, part: str) -> SemanticVersion:
        """Return a new version with `part` incremented and lower parts reset.

        Args:
            part: One of `major`, `minor`, or `patch`.

        Returns:
            The bumped SemanticVersion.

        Raises:
            NewDraftError: When `part` is not a known bump kind.
        """
        if part == "major":
            return SemanticVersion(self.major + 1, 0, 0)
        if part == "minor":
            return SemanticVersion(self.major, self.minor + 1, 0)
        if part == "patch":
            return SemanticVersion(self.major, self.minor, self.patch + 1)
        msg = f"Unknown bump part: {part!r}"
        raise NewDraftError(msg)

    def __str__(self) -> str:
        """Return the `MAJOR.MINOR.PATCH` text form."""
        return f"{self.major}.{self.minor}.{self.patch}"


def read_pyproject_version(content: str) -> SemanticVersion:
    """Read the `[project]` version from `pyproject.toml` text.

    Args:
        content: The full `pyproject.toml` text.

    Returns:
        The parsed current SemanticVersion.

    Raises:
        NewDraftError: When no `version = "X.Y.Z"` line is present.
    """
    match = _VERSION_RE.search(content)
    if match is None:
        msg = "No 'version = \"X.Y.Z\"' line found in pyproject.toml."
        raise NewDraftError(msg)
    return SemanticVersion.parse(match.group("version"))


def read_version_txt(content: str) -> SemanticVersion:
    """Read the current version from the first line of `version.txt` text.

    The first whitespace-separated token of the first line is taken as the
    version, and a trailing `-SNAPSHOT` marker (any case) is dropped before
    parsing, so a first line of `1.2.0-SNAPSHOT -- title` yields `1.2.0`. This
    is the one parser the `process-draft` instruction and the `--from-draft`
    tool mode share, so both read the file the same way.

    Args:
        content: The full `version.txt` text.

    Returns:
        The parsed current SemanticVersion.

    Raises:
        NewDraftError: When the first line carries no token, or the token is not
            a MAJOR.MINOR.PATCH version.
    """
    lines = content.splitlines()
    tokens = lines[0].split() if lines else []
    if not tokens:
        msg = "No version token on the first line of version.txt."
        raise NewDraftError(msg)
    cleaned = _SNAPSHOT_SUFFIX_RE.sub("", tokens[0])
    return SemanticVersion.parse(cleaned)


def validate_slug(raw: str) -> str:
    """Validate and normalize a user-entered slug.

    Args:
        raw: The raw slug text from the prompt.

    Returns:
        The trimmed slug when it is valid.

    Raises:
        NewDraftError: When the slug is empty or has unsupported characters.
    """
    candidate = raw.strip()
    if not _SLUG_RE.fullmatch(candidate):
        msg = (
            f"Invalid slug {raw!r}: use lowercase letters, digits, '-' or '_', "
            "starting with a letter or digit."
        )
        raise NewDraftError(msg)
    return candidate


def draft_filename(version: SemanticVersion, slug: str) -> str:
    """Return the `draft.vX.Y.Z.<slug>.md` filename for an effort."""
    return f"draft.v{version}.{slug}.md"


def worktree_dir_name(project_root_name: str, slug: str) -> str:
    """Return the sibling worktree directory name for a slug.

    The project base is the root folder name with any trailing `_<suffix>`
    dropped (so `llm-shared_main` yields the base `llm-shared`), then the slug
    is appended: `llm-shared_<slug>`.

    Args:
        project_root_name: The current repository root folder name.
        slug: The validated effort slug.

    Returns:
        The directory name for the new worktree.
    """
    base = (
        project_root_name.rsplit("_", 1)[0]
        if "_" in project_root_name
        else project_root_name
    )
    return f"{base}_{slug}"


def compute_worktree_path(project_root: Path, slug: str) -> Path:
    """Return the proposed sibling worktree path next to the project root."""
    return project_root.parent / worktree_dir_name(project_root.name, slug)


def draft_skeleton(
    *,
    version: SemanticVersion,
    slug: str,
    branch: str,
    today: datetime.date,
) -> str:
    """Build the markdown skeleton written to the draft file.

    Args:
        version: The target version for the effort.
        slug: The effort slug (also the topic suffix of the section titles).
        branch: The branch name the effort lives on.
        today: The date stamped into the metadata list.

    Returns:
        The markdown text, with unique section titles and single-space list
        markers per the repository markdown rules.
    """
    return (
        f"# Draft v{version} for {slug}\n"
        "\n"
        f"- Version: v{version}\n"
        f"- Branch: {branch}\n"
        f"- Date: {today.isoformat()}\n"
        "\n"
        f"## Context for {slug}\n"
        "\n"
        "Describe the problem or user story that starts this effort.\n"
        "\n"
        f"## Goal for {slug}\n"
        "\n"
        "State the outcome this effort should deliver.\n"
        "\n"
        f"## Notes for {slug}\n"
        "\n"
        "Capture open questions and early decisions here.\n"
    )


# eof
