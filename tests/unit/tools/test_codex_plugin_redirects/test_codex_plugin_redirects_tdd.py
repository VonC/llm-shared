"""Tests for clone-relative Codex skill package redirect validation.

Fix: Codex reads the package through the user skills folder link, in the
clone, so every redirect is checked relative to its own file there. The cache
base, the manifest version lookup and the ``--installed`` mode are gone, and
the command line takes only the clone root.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.script_entry import run_main
from tests.unit.tools.codex_skill_clone import write_clone
from tools import codex_plugin_redirects

_REDIRECT_KIND_COUNT = 3
_PACKAGE = Path(".agents") / "llm-shared"


@pytest.mark.parametrize("frontmatter", ["", "---\nllm_nature: codex\n---\n\n"])
def test_main_accepts_clone_relative_redirects(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    frontmatter: str,
) -> None:
    """Links relative to each adapter in the clone pass, with or without metadata."""
    clone = write_clone(tmp_path / "clone", frontmatter=frontmatter)

    assert codex_plugin_redirects.main([str(clone)]) == 0
    assert "Validated clone-relative redirects in:" in capsys.readouterr().out


def test_expected_links_climb_from_the_adapter_to_the_clone_root(tmp_path: Path) -> None:
    """A wrapper climbs four levels and a compatibility redirect three."""
    clone = tmp_path / "clone"
    package = clone / _PACKAGE

    skill = codex_plugin_redirects._relative_url(
        package / "skills" / "sample" / "SKILL.md",
        clone / "instructions" / "sample.md",
    )
    redirect = codex_plugin_redirects._relative_url(
        package / "rules" / "docs_layout.md",
        clone / "rules" / "docs_layout.md",
    )

    assert skill == "../../../../instructions/sample.md"
    assert redirect == "../../../rules/docs_layout.md"


@pytest.mark.parametrize("relative_path", ["instructions/sample.md", "rules/docs_layout.md"])
@pytest.mark.parametrize("damage", ["cache-link", "extra-prose", "unclosed-frontmatter"])
def test_metadata_does_not_hide_invalid_redirects(
    tmp_path: Path,
    relative_path: str,
    damage: str,
) -> None:
    """Metadata cannot make a cache link, forked body or unclosed header valid."""
    clone = write_clone(tmp_path / "clone", frontmatter="---\nllm_nature: codex\n---\n\n")
    adapter = clone / _PACKAGE / relative_path
    content = adapter.read_text(encoding="utf-8")
    if damage == "cache-link":
        content = content.replace("](../../../", "](../../../../../../../git/llm-shared/")
    elif damage == "extra-prose":
        content += "Additional workflow instructions.\n"
    else:
        content = content.replace("\n---\n", "\n")
    adapter.write_text(content, encoding="utf-8")

    errors = codex_plugin_redirects.validate_redirects(clone)

    assert len(errors) == 1
    assert str(adapter) in errors[0]


@pytest.mark.parametrize("write_wrong", [False, True])
def test_main_reports_every_missing_or_wrong_redirect(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    *,
    write_wrong: bool,
) -> None:
    """Instruction, skill, and rule diagnostics are accumulated together."""
    clone = write_clone(tmp_path / "clone")
    for relative in ("instructions/sample.md", "skills/sample/SKILL.md", "rules/docs_layout.md"):
        path = clone / _PACKAGE / relative
        if write_wrong:
            path.write_text("wrong\n", encoding="utf-8")
        else:
            path.unlink()

    assert codex_plugin_redirects.main([str(clone)]) == 1
    error = capsys.readouterr().err
    expected = "wrong clone-relative redirect" if write_wrong else "missing"
    assert error.count(expected) == _REDIRECT_KIND_COUNT


def test_script_guard_validates_the_clone_holding_the_tool(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Direct execution without arguments checks this repository's own package."""
    monkeypatch.setattr(sys, "argv", ["codex_plugin_redirects.py"])

    with pytest.raises(SystemExit) as raised:
        run_main(codex_plugin_redirects.__file__)

    assert raised.value.code == 0
    root = Path(codex_plugin_redirects.__file__).resolve().parent.parent
    assert str(root / _PACKAGE) in capsys.readouterr().out


# eof
