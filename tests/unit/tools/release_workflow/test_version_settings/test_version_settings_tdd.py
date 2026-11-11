"""Version sections of `.release.ini`, validated through `load_configuration`.

Step 3 of v0.14.0 version-sources: `[source:<name>]` overrides a built-in
adapter's form, within that adapter's forms, or declares a pattern source with
`file`, `pattern` (one capture group) and `form`; `anchor` and `pattern` are
reserved. `[component:<id>]` names one directory below the project root, never
the root itself, never under an excluded directory name and never twice. Each
failure is a `ConfigurationError` (status 2) naming the section and key, and
nothing is written. Until Steps 5 to 7 register `python`, `npm` and `maven`,
synthetic adapters with the design's forms stand in for them.
"""

from __future__ import annotations

import re
from functools import partial
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    SyntheticAdapter,
    project_identity,
    write_release_ini,
)
from tools.release_workflow.configuration import ConfigurationError, load_configuration
from tools.release_workflow.schemas import (
    TOOLING_SCHEMA,
    VERSION_SCHEMA,
    DomainSchema,
    SchemaRegistry,
)
from tools.release_workflow.sources import anchor, pattern, settings
from tools.release_workflow.sources.model import Form

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.configuration import Configuration

_PREFLIGHT = 2
_BUILT_IN = (
    anchor.ADAPTER,
    SyntheticAdapter("python", forms=frozenset({Form.CORE})),
    SyntheticAdapter("npm", forms=frozenset(Form), form=Form.RELEASE_ONLY),
    SyntheticAdapter("maven", forms=frozenset({Form.SNAPSHOT}), form=Form.SNAPSHOT),
    pattern.ADAPTER,
)
_UMBRELLA = r"^APP_SERVICE_VERSION=(.+)$"


def _registry() -> SchemaRegistry:
    """Ship the version sections with a validator that knows the synthetic built-in adapters."""
    version = DomainSchema("version", VERSION_SCHEMA.sections, validate=partial(settings.validate_settings, adapters=_BUILT_IN))
    shipped = (TOOLING_SCHEMA, version)
    return SchemaRegistry(shipped, shipped=shipped)


def _load(root: Path, text: str, *, built_in: bool = False) -> Configuration:
    """Write the declaration and load it with the shipped or the synthetic built-in registry."""
    write_release_ini(root, text)
    return load_configuration(project_identity(root), _registry() if built_in else None)


def _fails(root: Path, text: str, named: str, *, built_in: bool = False) -> None:
    """Expect a status 2 configuration failure matching `named`, with nothing written."""
    with pytest.raises(ConfigurationError, match=named) as caught:
        _load(root, text, built_in=built_in)
    assert caught.value.exit_code == _PREFLIGHT
    assert {path.name for path in root.iterdir()} == {".release.ini"}


def test_without_version_sections_the_defaults_apply(tmp_path: Path) -> None:
    """No declaration means no override, no pattern source and no component."""
    version = settings.read_settings(load_configuration(project_identity(tmp_path)))
    assert (version.project_root, dict(version.forms), version.patterns, dict(version.components)) == (tmp_path, {}, (), {})
    assert not list(tmp_path.iterdir())


def test_built_in_form_override_is_accepted(tmp_path: Path) -> None:
    """`[source:npm] form = snapshot` overrides npm; an empty built-in section overrides nothing."""
    configuration = _load(tmp_path, "[source:npm]\nform = snapshot\n[source:python]\n", built_in=True)
    assert dict(settings.read_settings(configuration, _BUILT_IN).forms) == {"npm": Form.SNAPSHOT}


def test_pattern_sources_and_components_are_read(tmp_path: Path) -> None:
    """Pattern declarations compile with `re.MULTILINE`; components keep declaration order."""
    text = (f"[source:cicd-env]\nfile = cicd/config/.env\npattern = {_UMBRELLA}\nform = snapshot\n"
            "[source:chart]\nfile = chart/Chart.yaml\npattern = ^appVersion: (?P<version>.+)$\nform = core\n"
            "[component:frontend]\nroot = frontend\n[component:api]\nroot = services/api\n")
    version = settings.read_settings(_load(tmp_path, text))
    first, second = version.patterns
    assert (first.name, first.path, first.expression.pattern, first.form) == ("cicd-env", tmp_path / "cicd/config/.env", _UMBRELLA, Form.SNAPSHOT)
    assert first.expression.flags & re.MULTILINE
    assert (second.name, second.path, second.form) == ("chart", tmp_path / "chart/Chart.yaml", Form.CORE)
    assert list(version.components.items()) == [("frontend", tmp_path / "frontend"), ("api", tmp_path / "services/api")]


@pytest.mark.parametrize(("text", "named"), [
    ("[source:python]\nform = snapshot\n", r"\[source:python\] form='snapshot'.*python allows only core"),
    ("[source:maven]\nform = core\n", r"\[source:maven\] form='core'.*maven allows only snapshot"),
    ("[source:npm]\nform = beta\n", r"\[source:npm\] form='beta'.*expected one of"),
    ("[source:npm]\nfile = x\n", r"\[source:npm\] file='x'.*accepts only form"),
    ("[source:npm]\ncolour = x\n", r"\[source:npm\] colour"),
])
def test_built_in_overrides_accept_only_their_forms(tmp_path: Path, text: str, named: str) -> None:
    """A built-in section takes only `form`, within its adapter's forms."""
    _fails(tmp_path, text, named, built_in=True)


@pytest.mark.parametrize(("text", "named"), [
    ("[source:anchor]\nform = snapshot\n", r"\[source:anchor\].*reserved"),
    (f"[source:pattern]\nfile = .env\npattern = {_UMBRELLA}\nform = snapshot\n", r"\[source:pattern\].*reserved"),
    (f"[source:env]\npattern = {_UMBRELLA}\nform = snapshot\n", r"\[source:env\] file: a pattern source requires"),
    ("[source:env]\nfile = .env\nform = snapshot\n", r"\[source:env\] pattern: a pattern source requires"),
    (f"[source:env]\nfile = .env\npattern = {_UMBRELLA}\n", r"\[source:env\] form: a pattern source requires"),
    ("[source:env]\nfile = .env\npattern = ^V=(.+$\nform = snapshot\n", r"\[source:env\] pattern='\^V=\(\.\+\$'.*compile"),
    ("[source:env]\nfile = .env\npattern = ^V=.+$\nform = snapshot\n", r"\[source:env\] pattern=.*exactly one capture group, found 0"),
    ("[source:env]\nfile = .env\npattern = ^(V)=(.+)$\nform = snapshot\n", r"\[source:env\] pattern=.*exactly one capture group, found 2"),
    (f"[source:env]\nfile = .env\npattern = {_UMBRELLA}\nform = beta\n", r"\[source:env\] form='beta'"),
])
def test_pattern_sources_need_a_complete_declaration(tmp_path: Path, text: str, named: str) -> None:
    """Reserved names, missing keys, broken patterns and unknown forms fail with the shipped adapters."""
    _fails(tmp_path, text, named)


@pytest.mark.parametrize(("text", "named"), [
    ("[component:self]\nroot = .\n", r"\[component:self\] root='\.'.*not the project root itself"),
    ("[component:deps]\nroot = node_modules/lib\n", r"\[component:deps\] root='node_modules/lib'.*excluded directory node_modules"),
    ("[component:demo]\nroot = docs/samples\n", r"\[component:demo\] root='docs/samples'.*excluded directory samples"),
    ("[component:demo]\nroot = Examples/app\n", r"\[component:demo\] root='Examples/app'.*excluded directory Examples"),
    ("[component:a]\nroot = frontend\n[component:b]\nroot = ./Frontend/\n", r"\[component:b\] root='\./Frontend/'.*same directory as \[component:a\]"),
])
def test_component_roots_are_distinct_directories_below_the_root(tmp_path: Path, text: str, named: str) -> None:
    """The project root, excluded directory names and a second declaration of one directory fail."""
    _fails(tmp_path, text, named)


# eof
