"""Read real diagram documentation once outside the assertion call phase.

Setup and total duration still account for the filesystem reads.
"""

import pytest

from tools import prompt_workflow_steps as steps


@pytest.fixture(scope="session")
def diagram_file_texts() -> dict[str, str]:
    """Retain actual launcher, alias and ordered Diataxis page contents."""
    root = steps.llm_shared_dir()
    return {
        path: (root / path).read_text(encoding="utf-8")
        for path in (
            "bin/git_history_diagrams.bat",
            "senv.doskey",
            "wiki/explanation/why-git-history-diagrams-use-explicit-arrows.md",
            "wiki/tutorials/07-generate-git-history-diagrams.md",
            "wiki/how-to/update-git-history-diagrams.md",
            "wiki/reference/git-history-diagram-generator.md",
        )
    }


# eof
