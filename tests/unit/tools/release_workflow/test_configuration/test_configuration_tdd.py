"""Prove strict, read-only parsing, domain defaults and managed path validation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from tools.release_workflow.configuration import ConfigurationError, load_configuration
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.schemas import (
    TOOLING_SCHEMA,
    DomainSchema,
    SchemaRegistry,
    SectionSchema,
    ValueRule,
)

if TYPE_CHECKING:
    from tools.release_workflow.schemas import ConfigSections, ConfigValue

INVALID_INPUT = 2


def project(root: Path) -> ProjectIdentity:
    """Supply the previously validated identity without reproving Git discovery."""
    return ProjectIdentity(root, root / ".git", root / ".git", str(root))


def registry(*schemas: DomainSchema) -> SchemaRegistry:
    """Compose test-only shipped owners explicitly, including foundation tooling."""
    shipped = (TOOLING_SCHEMA, *schemas)
    return SchemaRegistry(shipped, shipped=shipped)


def write(root: Path, text: str) -> Path:
    """Write exactly one project declaration using real UTF-8 bytes."""
    path = root / ".release.ini"
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_file_and_partial_override_use_owned_defaults(tmp_path: Path) -> None:
    """Defaults apply both without a file and to omitted keys in a declaration."""
    schema = DomainSchema("sample", (SectionSchema("sample", (ValueRule("mode", default="safe"), ValueRule("count", parse=int, default="2"))),))
    configured = registry(schema)
    absent = load_configuration(project(tmp_path), configured)
    assert absent.sections["sample"]["mode"].value == "safe"
    default_count = 2
    assert absent.sections["sample"]["count"].value == default_count
    assert absent.sections["sample"]["count"].defaulted
    assert list(tmp_path.iterdir()) == []
    write(tmp_path, "[sample]\ncount=3\n")
    present = load_configuration(project(tmp_path), configured)
    assert present.sections["sample"]["mode"].value == "safe"
    value = present.sections["sample"]["count"]
    declared_count = 3
    assert value.value == declared_count
    assert value.raw == "3"
    assert value.source == tmp_path / ".release.ini"
    assert (value.section, value.key, value.defaulted) == ("sample", "count", False)


@pytest.mark.parametrize("bom", ["", "\ufeff"])
def test_literal_values_and_bom_are_preserved(tmp_path: Path, bom: str) -> None:
    """Regex, percent, dollar, quotes and inline comments are data, not code."""
    raw = '^APP_SERVICE_VERSION=(.+)$ %PATH% ${root} "text" # ;'
    write(tmp_path, bom + "[sample]\npattern=" + raw + "\n")
    configured = registry(DomainSchema("sample", (SectionSchema("sample", (ValueRule("pattern"),)),)))
    assert load_configuration(project(tmp_path), configured).sections["sample"]["pattern"].value == raw


@pytest.mark.parametrize("text", ["bad", "[x\nkey=value", "[tooling]\n[tooling]\n", "[tooling]\nx=1\nx=2\n", "[tooling]\nX=1\nx=2\n", "\ufeff\ufeff[tooling]\n"])
def test_malformed_or_duplicate_input_never_defaults(tmp_path: Path, text: str) -> None:
    """Ambiguous INI and multiple BOMs fail with file context and status 2."""
    write(tmp_path, text)
    with pytest.raises(ConfigurationError) as caught:
        load_configuration(project(tmp_path))
    assert ".release.ini" in str(caught.value)
    assert caught.value.exit_code == INVALID_INPUT
    assert {path.name for path in tmp_path.iterdir()} == {".release.ini"}


@pytest.mark.parametrize("text", ["[future]\nx=1\n", "[tooling]\nunknown=1\n", "[DEFAULT]\nx=1\n", "[DEFAULT]\n", "[Tooling]\n", "[tooling]\ngit-cliff=some.exe\n"])
def test_unknown_declarations_are_rejected(tmp_path: Path, text: str) -> None:
    """Future domains and ConfigParser inheritance cannot silently become valid."""
    write(tmp_path, text)
    with pytest.raises(ConfigurationError, match="Unknown"):
        load_configuration(project(tmp_path))


@pytest.mark.parametrize("minimum", ["0.0.0", "0.14.0", "99.1.2"])
def test_minimum_gate_precedes_unknown_domain_validation(tmp_path: Path, minimum: str) -> None:
    """Any valid minimum fails closed before unknown newer-domain settings."""
    write(tmp_path, f"[future]\nx=1\n[tooling]\nminimum-version={minimum}\n")
    with pytest.raises(ConfigurationError, match=r"compatibility.*unavailable") as caught:
        load_configuration(project(tmp_path))
    assert minimum in str(caught.value)
    assert "minimum-version" in str(caught.value)
    assert caught.value.exit_code == INVALID_INPUT


@pytest.mark.parametrize("minimum", ["", "v0.14.0", "1.2", "01.2.3", "1.2.3-SNAPSHOT", "1.2.3+build", "1.2.3.4", "\u0661.2.3", "-1.2.3"])
def test_invalid_minimum_syntax(tmp_path: Path, minimum: str) -> None:
    """Only ASCII release MAJOR.MINOR.PATCH is accepted by the interim gate."""
    write(tmp_path, f"[tooling]\nminimum-version={minimum}\n")
    with pytest.raises(ConfigurationError, match=r"MAJOR\.MINOR\.PATCH"):
        load_configuration(project(tmp_path))


def test_read_errors_and_encoding_never_become_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An existing unreadable file and invalid bytes retain useful diagnostics."""
    path = tmp_path / ".release.ini"
    path.write_bytes(b"\xff")
    with pytest.raises(ConfigurationError, match="read"):
        load_configuration(project(tmp_path))
    def denied(_path: Path, **_kwargs: object) -> str:
        msg = "denied"
        raise PermissionError(msg)
    monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(ConfigurationError, match="denied"):
        load_configuration(project(tmp_path))


@pytest.mark.parametrize("text", ["", "[sample]\ncount=bad\n", "[sample]\ncount=\n"])
def test_required_values_and_invalid_types(tmp_path: Path, text: str) -> None:
    """A missing required value and invalid overrides cannot fall back."""
    write(tmp_path, text)
    configured = registry(DomainSchema("sample", (SectionSchema("sample", (ValueRule("count", parse=int, required=True),)),)))
    with pytest.raises(ConfigurationError, match="count"):
        load_configuration(project(tmp_path), configured)


def test_families_and_every_domain_cross_section_validation(tmp_path: Path) -> None:
    """Validate every shipped owner once, including owners with no declarations."""
    calls: list[ConfigSections] = []
    schema = DomainSchema("sources", (SectionSchema("source:", (ValueRule("name", required=True),), family=True),), validate=calls.append)
    other = DomainSchema("other", (), validate=calls.append)
    write(tmp_path, "[source:a]\nname=alpha\n[source:b]\nname=beta\n")
    result = load_configuration(project(tmp_path), registry(schema, other))
    expected_calls = 2
    assert len(calls) == expected_calls
    assert calls[0] is calls[1]
    assert calls[0]["source:a"]["name"].value == "alpha"
    assert result.sections["source:b"]["name"].value == "beta"
    with pytest.raises(TypeError):
        cast("dict[str, ConfigValue]", result.sections["source:a"])["name"] = result.sections["source:b"]["name"]


@pytest.mark.parametrize("instance", ["", " ", "\t", " npm", "npm ", "\tnpm", "npm\t"])
@pytest.mark.parametrize("existing", ["", "[source:npm]\nname=first\n"])
def test_blank_or_padded_family_instances_fail_without_writes(tmp_path: Path, instance: str, existing: str) -> None:
    """Ambiguous instance names cannot stand alone or bypass duplicate checks."""
    section = "source:" + instance
    declaration = existing + f"[{section}]\nname=second\n"
    source = write(tmp_path, declaration)
    configured = registry(DomainSchema("sources", (SectionSchema("source:", (ValueRule("name"),), family=True),)))
    with pytest.raises(ConfigurationError) as caught:
        load_configuration(project(tmp_path), configured)
    assert caught.value.exit_code == INVALID_INPUT
    assert str(source) in str(caught.value)
    assert f"[{section}]" in str(caught.value)
    assert list(tmp_path.iterdir()) == [source]
    assert source.read_text(encoding="utf-8") == declaration


@pytest.mark.parametrize("family", [False, True])
def test_internal_whitespace_and_exact_fixed_names_are_preserved(tmp_path: Path, *, family: bool) -> None:
    """Family instances retain internal spaces; fixed names use exact ownership."""
    section = "source:npm public" if family else "source: npm"
    definition = "source:" if family else section
    configured = registry(DomainSchema("sources", (SectionSchema(definition, (ValueRule("name"),), family=family),)))
    write(tmp_path, f"[{section}]\nname=literal\n")
    result = load_configuration(project(tmp_path), configured)
    assert result.sections[section]["name"].value == "literal"
    assert {path.name for path in tmp_path.iterdir()} == {".release.ini"}


def test_domain_conflict_reports_owner_and_file(tmp_path: Path) -> None:
    """A cross-section domain failure blocks the whole load without writes."""
    def conflict(_sections: ConfigSections) -> None:
        msg = "overlapping ranges in [archive:a] and [archive:b]"
        raise ValueError(msg)
    configured = registry(DomainSchema("archives", (), validate=conflict))
    with pytest.raises(ConfigurationError, match=r"archives.*overlapping") as caught:
        load_configuration(project(tmp_path), configured)
    assert ".release.ini" in str(caught.value)
    assert list(tmp_path.iterdir()) == []


def test_managed_paths_resolve_without_creation(tmp_path: Path) -> None:
    """Managed schema values use the physical project boundary, retaining input."""
    configured = registry(DomainSchema("sample", (SectionSchema("sample", (ValueRule("file", default="future/version.txt", path_role="managed"),)),)))
    value = load_configuration(project(tmp_path), configured).sections["sample"]["file"]
    assert value.value == tmp_path / "future" / "version.txt"
    assert value.raw == "future/version.txt"
    assert list(tmp_path.iterdir()) == []
    write(tmp_path, "[sample]\nfile=../outside.txt\n")
    with pytest.raises(ConfigurationError, match=r"file.*outside\.txt"):
        load_configuration(project(tmp_path), configured)


def test_one_file_read_for_many_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Parsing cost is one read followed by indexed per-setting lookups."""
    read = Path.read_text
    calls: list[Path] = []
    conversions: list[str] = []
    def convert(raw: str) -> int:
        conversions.append(raw)
        return int(raw)
    def counted(path: Path, *, encoding: str) -> str:
        calls.append(path)
        return read(path, encoding=encoding)
    count = 64
    rules = tuple(ValueRule(f"key{index}", parse=convert, default=str(index)) for index in range(count))
    configured = registry(DomainSchema("sample", (SectionSchema("sample", rules),)))
    write(tmp_path, "[sample]\n" + "".join(f"key{index}={index}\n" for index in range(count // 2)))
    monkeypatch.setattr(Path, "read_text", counted)
    result = load_configuration(project(tmp_path), configured)
    assert calls == [tmp_path / ".release.ini"]
    assert conversions == [str(index) for index in range(count)]
    assert len(result.sections["sample"]) == count


def test_disappearing_target_with_existing_entry_is_invalid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A dangling link or raced target is not mistaken for an absent declaration."""
    write(tmp_path, "[tooling]\n")
    def missing(_path: Path, **_kwargs: object) -> str:
        msg = "target disappeared"
        raise FileNotFoundError(msg)
    monkeypatch.setattr(Path, "read_text", missing)
    with pytest.raises(ConfigurationError, match="target disappeared"):
        load_configuration(project(tmp_path))


def test_directory_and_foreign_configuration_are_rejected(tmp_path: Path) -> None:
    """Configuration cannot be a directory or cross a repository boundary."""
    declaration = tmp_path / ".release.ini"
    declaration.mkdir()
    with pytest.raises(ConfigurationError, match="read"):
        load_configuration(project(tmp_path))
    (declaration / ".git").mkdir()
    with pytest.raises(ConfigurationError, match="nested repository"):
        load_configuration(project(tmp_path))


def test_empty_managed_path_is_not_the_project_root(tmp_path: Path) -> None:
    """Empty explicit paths are invalid even when an owned default exists."""
    configured = registry(DomainSchema("sample", (SectionSchema("sample", (ValueRule("file", default="version.txt", path_role="managed"),)),)))
    write(tmp_path, "[sample]\nfile=\n")
    with pytest.raises(ConfigurationError, match="must not be empty"):
        load_configuration(project(tmp_path), configured)


# eof
