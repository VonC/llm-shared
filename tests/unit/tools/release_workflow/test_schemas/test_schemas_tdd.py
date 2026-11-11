"""Prove complete explicit registration and conflict-free fixed/family owners.

Step 3 of v0.14.0 version-sources ships the version domain after tooling: its
`source:` and `component:` families are owned, and a configuration without
them never imports the version source package, whatever earlier tests loaded.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    project_identity,
    write_release_ini,
)
from tools.release_workflow.configuration import load_configuration
from tools.release_workflow.schemas import (
    SHIPPED_SCHEMAS,
    TOOLING_SCHEMA,
    VERSION_SCHEMA,
    DomainSchema,
    SchemaError,
    SchemaRegistry,
    SectionSchema,
    ValueRule,
)
from tools.release_workflow.sources import settings

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.schemas import ConfigSections

_SOURCES = "tools.release_workflow.sources"


def _source_modules() -> list[str]:
    """Name the loaded modules of the version source package."""
    return [name for name in sys.modules if name == _SOURCES or name.startswith(_SOURCES + ".")]


def _unload_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove the source modules for this test only; teardown restores them."""
    for name in _source_modules():
        monkeypatch.delitem(sys.modules, name)


def test_foundation_ships_tooling_then_version() -> None:
    """The shipped tuple is exactly tooling then version; version owns two families."""
    registry = SchemaRegistry()
    assert SHIPPED_SCHEMAS == (TOOLING_SCHEMA, VERSION_SCHEMA)
    assert registry.schemas == SHIPPED_SCHEMAS
    assert registry.section("tooling") is not None
    assert registry.section("version") is None
    owners = (registry.section("source:npm"), registry.section("component:frontend"))
    assert [owner.domain if owner else None for owner in owners] == ["version", "version"]


@pytest.mark.parametrize("text", ["", "[tooling]\n"])
def test_configuration_without_version_sections_imports_no_source_module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """The version validator returns before its deferred import when no version section exists."""
    _unload_sources(monkeypatch)
    if text:
        write_release_ini(tmp_path, text)
    load_configuration(project_identity(tmp_path))
    assert _source_modules() == []


def test_version_section_runs_the_deferred_validator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A declared version section is handed, once, to the source settings validator.

    The module is replaced in place rather than unloaded: reloading it would
    leave classes that differ from the ones other tests imported.
    """
    calls: list[ConfigSections] = []
    monkeypatch.setattr(settings, "validate_settings", calls.append)
    write_release_ini(tmp_path, "[component:app]\nroot = app\n")
    configuration = load_configuration(project_identity(tmp_path))
    assert calls == [configuration.sections]
    assert configuration.sections["component:app"]["root"].value == tmp_path / "app"


def test_missing_or_substituted_shipped_owner_is_rejected() -> None:
    """Completeness is checked against explicit source declarations, not names."""
    for schemas in ((), (DomainSchema("tooling", ()),)):
        with pytest.raises(SchemaError, match="shipped"):
            SchemaRegistry(schemas)


def test_unshipped_owner_is_rejected() -> None:
    """Registry injection cannot silently extend the production declaration set."""
    with pytest.raises(SchemaError, match="shipped"):
        SchemaRegistry((TOOLING_SCHEMA, DomainSchema("extra", ())))


@pytest.mark.parametrize("names", [("sample", "sample"), ("source:", "source:a"), ("source:a", "source:"), ("source:", "source:sub:"), ("source:sub:", "source:")])
def test_overlapping_section_ownership_is_rejected(names: tuple[str, str]) -> None:
    """Both insertion orders reject exact and nested prefix claims."""
    sections = tuple(SectionSchema(name, (), family=name.endswith(":")) for name in names)
    schema = DomainSchema("sample", sections)
    with pytest.raises(SchemaError, match="ownership"):
        SchemaRegistry((schema,), shipped=(schema,))


def test_fixed_prefixes_can_coexist_without_family_ownership() -> None:
    """Fixed sections do not claim extensions; families require an instance."""
    schema = DomainSchema("sample", (SectionSchema("a", ()), SectionSchema("ab", ()), SectionSchema("source:", (), family=True)))
    registry = SchemaRegistry((schema,), shipped=(schema,))
    assert registry.section("a") is not None
    assert registry.section("ab") is not None
    assert registry.section("abc") is None
    assert registry.section("source:") is None
    assert registry.section("source:a") is not None


def test_duplicate_keys_and_domain_owners_are_rejected() -> None:
    """Key and domain ownership are unambiguous even before configuration exists."""
    schema = DomainSchema("sample", (SectionSchema("a", (ValueRule("key"), ValueRule("key"))),))
    with pytest.raises(SchemaError, match="key"):
        SchemaRegistry((schema,), shipped=(schema,))
    with pytest.raises(SchemaError, match="domain"):
        SchemaRegistry((TOOLING_SCHEMA, TOOLING_SCHEMA))


@pytest.mark.parametrize("name", ["", " a", "a ", "DEFAULT", "[a]", "a\nb", "a\rb"])
def test_invalid_section_names(name: str) -> None:
    """Source mistakes cannot register ambiguous or inherited INI declarations."""
    schema = DomainSchema("sample", (SectionSchema(name, ()),))
    with pytest.raises(SchemaError, match="section"):
        SchemaRegistry((schema,), shipped=(schema,))


@pytest.mark.parametrize("key", ["", "Key", "with space", "a:b", "a=b"])
def test_invalid_keys(key: str) -> None:
    """Shipped keys use the parser's canonical lowercase spelling."""
    schema = DomainSchema("sample", (SectionSchema("sample", (ValueRule(key),)),))
    with pytest.raises(SchemaError, match="key"):
        SchemaRegistry((schema,), shipped=(schema,))


def test_managed_paths_cannot_replace_containment_with_converter() -> None:
    """Managed-path declarations must use the common resolver exclusively."""
    schema = DomainSchema("sample", (SectionSchema("sample", (ValueRule("file", parse=int, path_role="managed"),)),))
    with pytest.raises(SchemaError, match="path role"):
        SchemaRegistry((schema,), shipped=(schema,))


# eof
