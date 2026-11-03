"""Readiness rejects incomplete metadata, unsupported markers and missing packages."""

from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.test_support import ENV, metadata, package
from tools.release_workflow.markers import evaluate, satisfies
from tools.release_workflow.readiness import (
    Closure,
    normalized,
    sequence,
    source_kind,
    string,
    table,
    validate,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@pytest.mark.parametrize(("validator", "value"), [
    (table, []), (sequence, {}), (string, ""), (string, 1),
])
def test_wrong_input_types(validator: Callable[[object, str], object], value: object) -> None:
    """Typed boundaries do not silently coerce malformed lock values."""
    with pytest.raises(ValueError, match="Expected"):
        validator(value, "fixture")


def test_source_and_normalization() -> None:
    """Name equivalence and source identity do not depend on registry URLs."""
    assert normalized("A_B.c--D") == "a-b-c-d"
    for value in ({}, {"registry": "one", "git": "two"}, {"registry": ""}):
        with pytest.raises(ValueError, match="source"):
            source_kind(value)


@pytest.mark.parametrize(("filename", "old", "new"), [
    ("pyproject.toml", ">=3.13, <3.14", ">=3.14"),
    ("pyproject.toml", '{include-group = "release"}', '"unrelated"'),
    ("pyproject.toml", 'release = ["alpha"]', 'other = ["alpha"]'),
    ("uv.lock", 'name = "sample-tooling"', 'name = "other"'),
    ("uv.lock", 'source = {virtual = "."}', 'source = {virtual = "other"}'),
    ("uv.lock", 'release = [{name="alpha"}]', 'other = [{name="alpha"}]'),
    ("uv.lock", "[package.metadata.requires-dev]", "[package.metadata.other]"),
    ("uv.lock", 'release = ["alpha"]', 'other = ["alpha"]'),
])
def test_invalid_project_or_root(tmp_path: Path, filename: str, old: str, new: str) -> None:
    """Interpreter, group inclusion and root lock completeness are mandatory."""
    metadata(tmp_path, package("alpha"), '{name="alpha"}')
    path = tmp_path / filename
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    with pytest.raises(ValueError, match=r"interpreter|dependencies|root|release"):
        validate(tmp_path, ENV, {"alpha": "1.0"}.__getitem__, evaluate, satisfies)


def test_installed_closure_failures(tmp_path: Path) -> None:
    """Missing and mismatched transitive distributions both fail readiness."""
    metadata(tmp_path, package("alpha", edges='{name="beta"}') + package("beta"), '{name="alpha"}')

    def missing(name: str) -> str:
        if name == "beta":
            raise importlib.metadata.PackageNotFoundError(name)
        return "1.0"

    with pytest.raises(importlib.metadata.PackageNotFoundError):
        validate(tmp_path, ENV, missing, evaluate, satisfies)
    with pytest.raises(ValueError, match=r"beta.*expected"):
        validate(tmp_path, ENV, {"alpha": "1.0", "beta": "2.0"}.__getitem__, evaluate, satisfies)


def test_source_disambiguation_and_empty_extras() -> None:
    """Explicit source kind distinguishes a registry package from a git package."""
    packages: list[object] = [
        {"name": "alpha", "version": "1.0", "source": {"registry": "first"}},
        {"name": "alpha", "version": "1.0", "source": {"git": "second"}},
    ]
    closure = Closure(packages, ENV, evaluate)
    assert closure.walk([{"name": "alpha", "source": {"registry": "rewritten"}, "extra": []}],
                        {"alpha": "1.0"}.__getitem__) == ("alpha",)
    with pytest.raises(ValueError, match="ambiguous"):
        Closure([packages[0], packages[0]], ENV, evaluate).walk([{"name": "alpha"}], {"alpha": "1.0"}.__getitem__)


# eof
