"""Judge exact group sources through real coverage data, never parsed TOTAL.

Fix (v0.13.0 full_suite_levels, Step 4): unusable evidence closes its
database connection even when coverage fails during load.
"""

import gc
import os
import warnings
from pathlib import Path

import pytest
from coverage import CoverageData

from tests.unit.tools.groundhog_group_support import group_project
from tools.groundhog import group_coverage, groups, snapshot


@pytest.mark.parametrize(("sources", "expected"), [
    (("src/a.py", "src/nested/b.py", "lib/c.py"), ("lib", "src")),
    (("a.py", "src/a.py"), (".",)),
    ((), ()),
])
def test_smallest_containing_folders(sources: tuple[str, ...], expected: tuple[str, ...]) -> None:
    """Remove redundant descendant folders without broadening sibling roots."""
    assert group_coverage.cov_folders(sources) == expected


@pytest.mark.parametrize("executed", [True, False])
def test_counts_unexecuted_sources(tmp_path: Path, *, executed: bool) -> None:
    """A source with no recorded execution still contributes all its statements."""
    group_project(tmp_path)
    scope = groups.resolve_group(tmp_path, "sentinel", snapshot.source_files(tmp_path))
    path = group_coverage.data_file(tmp_path, scope.name)
    assert path.name == "a.ghog.coverage.sentinel"
    data = CoverageData(basename=str(path))
    data.add_lines({str(tmp_path / "src" / name / "core.py"): [1]
                    for name in (("sentinel",) if executed else ("other",))})
    data.write()
    result = group_coverage.judge(tmp_path, scope, path, 0)
    assert not result.error
    assert result.percent == (100.0 if executed else 0.0)
    if not executed:
        assert "core.py" in "\n".join(result.gap_rows)
        assert "0%" in "\n".join(result.gap_rows)


@pytest.mark.parametrize("problem", ["missing", "invalid", "stale", "directory"])
def test_bad_evidence(tmp_path: Path, problem: str) -> None:
    """Invalid data names the evidence problem instead of inventing coverage."""
    group_project(tmp_path)
    scope = groups.resolve_group(tmp_path, "sentinel", snapshot.source_files(tmp_path))
    path = group_coverage.data_file(tmp_path, scope.name)
    if problem == "directory":
        path.mkdir()
    elif problem != "missing":
        path.write_text("not coverage", encoding="utf-8")
        if problem == "stale":
            os.utime(path, (1, 1))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ResourceWarning)
        result = group_coverage.judge(tmp_path, scope, path, 2)
        gc.collect()
    assert not caught
    assert result.percent is None
    assert "coverage evidence" in result.error
    assert str(path) in result.error


@pytest.mark.parametrize("config", ["none", "relative", "precedence", "missing_arcs"])
def test_project_configuration_from_another_directory(tmp_path: Path, config: str) -> None:
    """Read config and relative data in the project root; reject missing branch evidence."""
    group_project(tmp_path)
    scope = groups.resolve_group(tmp_path, "sentinel", snapshot.source_files(tmp_path))
    _configure_project(tmp_path, config)
    path = group_coverage.data_file(tmp_path, scope.name)
    data = CoverageData(basename=str(path))
    filename = scope.source_files[0] if config == "relative" else str(tmp_path / scope.source_files[0])
    if config == "precedence":
        data.add_arcs({filename: [(-1, 1), (1, -1)]})
    else:
        data.add_lines({filename: [1]})
    data.write()
    before = Path.cwd()
    result = group_coverage.judge(tmp_path, scope, path, 0)
    assert Path.cwd() == before
    if config == "missing_arcs":
        assert "branch" in result.error
    else:
        assert not result.error
        expected = 100.0
        assert result.percent == expected


def _configure_project(root: Path, config: str) -> None:
    """Supply realistic absent, relative and fallback project configurations."""
    project_config = root / "pyproject.toml"
    project_config.unlink()
    if config == "relative":
        project_config.write_text("[tool.coverage.run]\nrelative_files = true\n", encoding="utf-8")
    elif config in ("precedence", "missing_arcs"):
        (root / "setup.cfg").write_text("[metadata]\nname = example\n", encoding="utf-8")
        project_config.write_text("[tool.coverage.run]\nbranch = true\n", encoding="utf-8")


def test_report_cannot_ignore_an_unusable_group_source(tmp_path: Path) -> None:
    """A project report preference must not silently remove a bound source."""
    group_project(tmp_path)
    (tmp_path / "src/sentinel/broken.py").write_text("def invalid syntax\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[tool.coverage.report]\nignore_errors = true\n", encoding="utf-8")
    scope = groups.resolve_group(tmp_path, "sentinel", snapshot.source_files(tmp_path))
    path = group_coverage.data_file(tmp_path, scope.name)
    data = CoverageData(basename=str(path))
    data.add_lines({str(tmp_path / "src/sentinel/core.py"): [1]})
    data.write()
    result = group_coverage.judge(tmp_path, scope, path, 0)
    assert result.percent is None
    assert "broken.py" in result.error
