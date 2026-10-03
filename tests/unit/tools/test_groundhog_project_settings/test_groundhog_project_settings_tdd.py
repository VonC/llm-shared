"""Project settings preserve defaults, explicit declarations and format precedence."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.groundhog import project_settings as settings

if TYPE_CHECKING:
    from pathlib import Path


def test_defaults_and_accessors(tmp_path: Path) -> None:
    """Absent optional configuration supplies pytest defaults and no coverage filters."""
    assert settings.python_files(tmp_path) == ("test_*.py", "*_test.py")
    assert settings.coverage_omit(tmp_path) == ()
    assert settings.coverage_sources(tmp_path) == ()
    assert settings.coverage_branch(tmp_path) is False
    assert settings.dict_get("not a table", "key") is None


@pytest.mark.parametrize(("file", "body"), [
    ("pyproject.toml", '[tool.pytest.ini_options]\npython_files=["check_*.py"]\n[tool.coverage.run]\nomit=["*/skip.py"]\nsource=["src"]\nbranch=true\n'),
    ("setup.cfg", "[tool:pytest]\npython_files=check_*.py\n[coverage:run]\nomit=\n    */skip.py\nsource=src\nbranch=yes\n"),
    ("tox.ini", "[pytest]\npython_files=check_*.py\n[coverage:run]\nomit=\n    */skip.py\nsource=src\nbranch=1\n"),
])
def test_settings_formats(tmp_path: Path, file: str, body: str) -> None:
    """Each supported project format exposes collection and coverage settings."""
    (tmp_path / file).write_text(body, encoding="utf-8")
    assert settings.Settings.load(tmp_path) == settings.Settings(("check_*.py",), ("*/skip.py",), ("src",), branch=True)


def test_ini_overrides_pytest_toml_and_coveragerc_supplies_coverage(tmp_path: Path) -> None:
    """Pytest INI wins collection and coverage falls back per option."""
    (tmp_path / "pytest.ini").write_text("[pytest]\npython_files=custom_*.py\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[tool.pytest.ini_options]\npython_files=["ignored.py"]\n', encoding="utf-8")
    (tmp_path / ".coveragerc").write_text("[run]\nomit=skip.py\nsource=src\nbranch=on\n", encoding="utf-8")
    assert settings.Settings.load(tmp_path) == settings.Settings(("custom_*.py",), ("skip.py",), ("src",), branch=True)


@pytest.mark.parametrize("body", ["[broken", "[tool.pytest.ini_options]\npython_files=42\n",
                                       '[tool.pytest.ini_options]\npython_files="broken \\" quote"\n'])
def test_malformed_settings(tmp_path: Path, body: str) -> None:
    """Malformed optional values never crash the resolver."""
    (tmp_path / "pyproject.toml").write_text(body, encoding="utf-8")
    (tmp_path / ".coveragerc").write_text("not ini", encoding="utf-8")
    assert isinstance(settings.Settings.load(tmp_path), settings.Settings)


def test_coverage_lists_preserve_path_syntax(tmp_path: Path) -> None:
    """Coverage lists use commas or newlines, preserving spaces and Windows separators."""
    (tmp_path / ".coveragerc").write_text(
        "[run]\nomit=\n    generated files/*.py, other/*.py\n    tools\\skip.py\nsource=src, extra src\n", encoding="utf-8",
    )
    options = settings.Settings.load(tmp_path)
    assert options.omit == ("generated files/*.py", "other/*.py", "tools\\skip.py")
    assert options.sources == ("src", "extra src")
