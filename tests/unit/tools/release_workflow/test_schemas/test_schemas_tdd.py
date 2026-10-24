"""Prove complete explicit registration and conflict-free fixed/family owners."""

from __future__ import annotations

import pytest

from tools.release_workflow.schemas import (
    TOOLING_SCHEMA,
    DomainSchema,
    SchemaError,
    SchemaRegistry,
    SectionSchema,
    ValueRule,
)


def test_foundation_ships_only_tooling() -> None:
    """Future release-domain settings remain unavailable until their owner ships."""
    registry = SchemaRegistry()
    assert registry.schemas == (TOOLING_SCHEMA,)
    assert registry.section("tooling") is not None
    assert registry.section("version") is None


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
