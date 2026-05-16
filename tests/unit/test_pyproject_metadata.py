"""Tests for packaging metadata declared in pyproject.toml.

Fix: Prevent the published package metadata from exporting the development
lockfile as runtime dependencies.

Fix: Constrain package discovery so setuptools does not treat every top-level
folder in the repository as an installable package.
"""

from __future__ import annotations

from pathlib import Path
import tomllib


def test_pyproject_does_not_export_dev_lockfile_as_runtime_dependencies() -> None:
    """The package metadata should not treat the dev lockfile as install deps."""
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    dynamic_fields = pyproject["project"].get("dynamic", [])
    assert "dependencies" not in dynamic_fields

    setuptools_dynamic = (
        pyproject.get("tool", {})
        .get("setuptools", {})
        .get(
            "dynamic",
            {},
        )
    )
    assert "dependencies" not in setuptools_dynamic


def test_pyproject_limits_setuptools_package_discovery_to_tools() -> None:
    """The package build should only include the real Python package surface."""
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    setuptools_config = pyproject.get("tool", {}).get("setuptools", {})
    assert setuptools_config.get("packages") == ["tools"]


# eof
