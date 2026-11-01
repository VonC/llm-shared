"""Package imports preserve public identities without unrelated startup work."""

from __future__ import annotations

import sys
from importlib import import_module

import pytest

import tools


@pytest.fixture
def fresh_release_import() -> tuple[str, ...]:
    """Load a fresh tools namespace in this interpreter, then restore collection's objects."""
    saved = {name: module for name, module in sys.modules.items()
             if name == "tools" or name.startswith("tools.")}
    for name in saved:
        del sys.modules[name]
    try:
        import_module("tools.release_workflow.cli")
        return tuple(name for name in sys.modules if name.startswith("tools."))
    finally:
        for name in list(sys.modules):
            if name == "tools" or name.startswith("tools."):
                del sys.modules[name]
        sys.modules.update(saved)


def test_release_import_omits_unrelated_review_graph(fresh_release_import: tuple[str, ...]) -> None:
    """A fresh module namespace imports the release CLI without unrelated tools."""
    imported = fresh_release_import
    assert "tools.release_workflow.cli" in imported
    assert "tools.review_exchange_publication" not in imported
    assert not any(name.startswith(("tools.spec_review", "tools.markdown_check")) for name in imported)


@pytest.mark.parametrize("name", tools.__all__)
def test_public_exports_retain_original_identity(name: str) -> None:
    """Every declared export resolves to its defining object and remains cached."""
    resolved = tools.__getattr__(name)
    module = "tools._models" if name == "project_name" else resolved.__module__
    assert resolved is getattr(import_module(module), name)
    assert getattr(tools, name) is resolved
    assert tools.__getattr__(name) is resolved


def test_unknown_attribute_and_submodule_import() -> None:
    """Missing attributes still fail while Python can import a real submodule."""
    with pytest.raises(AttributeError, match="has no attribute 'missing_export'"):
        tools.__getattr__("missing_export")
    from tools import release_workflow  # noqa: PLC0415 - exercise from-package fallback

    assert release_workflow is import_module("tools.release_workflow")


# eof
