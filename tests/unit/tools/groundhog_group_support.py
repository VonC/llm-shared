"""Group projects and real coverage data at the injected process boundary."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from coverage import CoverageData

from tests.unit.tools.groundhog_acceptance_support import Spawns, passing_transcript

if TYPE_CHECKING:
    import subprocess


def group_project(root: Path) -> Path:
    """Create two disjoint groups with executable source and test files."""
    (root / "pyproject.toml").write_text(
        '[tool.coverage.run]\nsource = ["src"]\n[tool.coverage.report]\nfail_under = 10\n',
        encoding="utf-8",
    )
    declarations: list[str] = []
    for name in ("sentinel", "other"):
        for folder, file, content in (
            ("tests", "test_core.py", "def test_ok():\n    assert True\n"),
            ("src", "core.py", "value = 1\n"),
        ):
            path = root / folder / name / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        declarations.append(f"[{name}]\ntests = tests/{name}/**\nsources = src/{name}/**\n")
    (root / ".ghog-groups").write_text("\n".join(declarations), encoding="utf-8")
    return root


class CoverageSpawns(Spawns):
    """Write actual coverage evidence only while the child sees its override."""

    def __init__(self, root: Path, *, data: str = "good") -> None:
        """Default to passing tests with a deliberately untrustworthy TOTAL."""
        super().__init__(passing_transcript(1, "TOTAL 1 0 100%"), 0)
        self.root = root
        self.data = data
        self.lines = {str(root / "src" / name / "core.py"): [1] for name in ("sentinel", "other")}
        self.arcs: dict[str, list[tuple[int, int]]] | None = None
        self.observed: list[str | None] = []

    def __call__(self, command: list[str], cwd: Path) -> subprocess.Popen[str]:
        """Model pytest-cov persistence, leaving uncovered runs untouched."""
        target = os.environ.get("COVERAGE_FILE")
        self.observed.append(target)
        if target and "--no-cov" not in command:
            path = Path(target)
            path.parent.mkdir(parents=True, exist_ok=True)
            if self.data == "invalid":
                path.write_text("invalid database", encoding="utf-8")
            elif self.data != "missing":
                coverage = CoverageData(basename=target)
                if "--cov-append" in command:
                    coverage.read()
                if self.arcs is None:
                    coverage.add_lines(self.lines)
                else:
                    coverage.add_arcs(self.arcs)
                coverage.write()
                if self.data == "stale":
                    os.utime(path, (1, 1))
        return super().__call__(command, cwd)
