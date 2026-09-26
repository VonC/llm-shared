"""Name and locate the code writer's private notes for one plan step.

A code writer (the code-review requestor) keeps two private, git-ignored notes
per implementation step, both in the review artifact home (`.reviews` unless
`.review-artifacts.ini` declares another home):

- `a.<slug>.step<x>.journal.md`: the step's objectives, main goal, and plan
  and umbrella context, then an append-only milestone log;
- `a.<slug>.step<x>.handoff.md`: the verified state, next actions, decisions,
  record tables, and private references a new session resumes from.

Every other file the step creates (scripts, logs, captures, bundles, evidence
folders) is temporary and named `a.<slug>.step<x>.tmp.<what>[.<ext>]` in the
same home, so `prepare-release` can list and delete them per effort.

`pw step-journal <x>` prepares the home (with its `*` ignore file), then prints
whether the step is starting (no journal yet) or resuming (journal present),
with the exact paths; `pw progress` shows the journal path of the current
coding step. See `instructions/step-journal.md`.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools import prompt_workflow_git as git
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_memory as memory
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path

EXIT_OK: Final[int] = 0
EXIT_FATAL: Final[int] = 2
EXIT_NOT_APPLICABLE: Final[int] = 3
_STEP_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_LABEL_WIDTH: Final[int] = 10


class StepJournalError(ValueError):
    """Raised when a step id cannot name a private step note."""


@dataclass(frozen=True)
class StepNotes:
    """The private note paths of one implementation step.

    Attributes:
        home: The review artifact home holding every step note.
        slug: The topic slug the notes belong to.
        step: The plan step id, as written in the plan (`3`, `3b`, `4A`, `3.2`).
    """

    home: Path
    slug: str
    step: str

    @property
    def stem(self) -> str:
        """Return the shared `a.<slug>.step<x>` name stem."""
        return f"a.{self.slug}.step{self.step}"

    @property
    def journal(self) -> Path:
        """Return the step journal path."""
        return self.home / f"{self.stem}.journal.md"

    @property
    def handoff(self) -> Path:
        """Return the step handoff path."""
        return self.home / f"{self.stem}.handoff.md"

    @property
    def tmp_pattern(self) -> Path:
        """Return the glob naming the step's temporary files and folders."""
        return self.home / f"{self.stem}.tmp.*"

    @property
    def resuming(self) -> bool:
        """Return whether the journal exists, so the step is being resumed."""
        return self.journal.is_file()


def step_notes(root: Path, slug: str, step: str) -> StepNotes:
    """Return the private note paths of one step, without writing anything.

    Args:
        root: The project root.
        slug: The topic slug.
        step: The plan step id.

    Returns:
        The step's note paths inside the configured artifact home.

    Raises:
        StepJournalError: When the step id is empty or not a plain token.
        ReviewExchangeError: When the artifact-home declaration is invalid.
    """
    if not _STEP_RE.fullmatch(step):
        message = f"invalid plan step id: {step!r}"
        raise StepJournalError(message)
    return StepNotes(ReviewArtifactConfiguration.load(root).home, slug, step)


def existing_journal(root: Path, slug: str, step: str) -> Path | None:
    """Return the step journal when it exists, for the read-only `pw progress`.

    Args:
        root: The project root.
        slug: The topic slug.
        step: The plan step id.

    Returns:
        The journal path, or None when it is absent or cannot be named.
    """
    try:
        notes = step_notes(root, slug, step)
    except (StepJournalError, ReviewExchangeError):
        return None
    return notes.journal if notes.resuming else None


def render_notes(notes: StepNotes) -> str:
    """Return the aligned `state`, `journal`, `handoff`, and `tmp` report."""
    lines = (
        ("state", "resume" if notes.resuming else "start"),
        ("journal", str(notes.journal)),
        ("handoff", str(notes.handoff)),
        ("tmp", str(notes.tmp_pattern)),
    )
    return "".join(f"{label:<{_LABEL_WIDTH}}{value}\n" for label, value in lines)


def run_step_journal(root: Path, step: str) -> int:
    """Prepare the artifact home and print the current topic's step notes.

    Args:
        root: The project root.
        step: The plan step id the writer is implementing.

    Returns:
        0 with the report printed; 3 without a resolved topic; 2 when the
        step id or the artifact home is invalid.
    """
    topic = handoff.resolve_current_topic(root, git.current_branch(root), memory.read_memory(root))
    if topic is None:
        sys.stderr.write("pw step-journal: no workflow topic resolved.\n")
        return EXIT_NOT_APPLICABLE
    try:
        notes = step_notes(root, topic.slug, step)
        ReviewArtifactConfiguration.load(root).prepare_home()
    except (StepJournalError, ReviewExchangeError) as error:
        sys.stderr.write(f"pw step-journal: {error}\n")
        return EXIT_FATAL
    sys.stdout.write(render_notes(notes))
    return EXIT_OK


# eof
