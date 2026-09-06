"""Tests for cache-relative Codex plugin redirect validation."""

from __future__ import annotations

import json
import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tools import codex_plugin_redirects

if TYPE_CHECKING:
    from pathlib import Path


_VERSION = "1.2.3"
_REDIRECT_KIND_COUNT = 3


def _roots(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create canonical, plugin, and cache roots with a valid manifest."""
    canonical = tmp_path / "canonical"
    plugin = tmp_path / "plugin"
    cache_base = tmp_path / "cache"
    (canonical / "instructions").mkdir(parents=True)
    (canonical / "rules").mkdir()
    (canonical / "instructions" / "sample.md").write_text("# Sample\n", encoding="utf-8")
    (canonical / "rules" / "docs_layout.md").write_text("# Layout\n", encoding="utf-8")
    (plugin / ".codex-plugin").mkdir(parents=True)
    (plugin / ".codex-plugin" / "plugin.json").write_text(
        json.dumps({"version": _VERSION}),
        encoding="utf-8",
    )
    return canonical, plugin, cache_base


def _write_valid_redirects(adapter: Path, canonical: Path, cache_root: Path) -> None:
    """Write the exact redirect forms accepted by the validator."""
    instruction = adapter / "instructions" / "sample.md"
    skill = adapter / "skills" / "sample" / "SKILL.md"
    rule = adapter / "rules" / "docs_layout.md"
    instruction.parent.mkdir(parents=True)
    skill.parent.mkdir(parents=True)
    rule.parent.mkdir(parents=True)
    instruction_url = codex_plugin_redirects._relative_url(
        cache_root / "instructions" / "sample.md",
        canonical / "instructions" / "sample.md",
    )
    skill_url = codex_plugin_redirects._relative_url(
        cache_root / "skills" / "sample" / "SKILL.md",
        canonical / "instructions" / "sample.md",
    )
    rule_url = codex_plugin_redirects._relative_url(
        cache_root / "rules" / "docs_layout.md",
        canonical / "rules" / "docs_layout.md",
    )
    instruction.write_text(
        "Read and follow the canonical instruction at "
        f"[`instructions/sample.md`]({instruction_url}).\n",
        encoding="utf-8",
    )
    skill.write_text(
        f"Read and follow [the canonical instruction]({skill_url})\n",
        encoding="utf-8",
    )
    rule.write_text(
        "Read and follow the canonical rule at "
        f"[`rules/docs_layout.md`]({rule_url}).\n",
        encoding="utf-8",
    )


def _set_argv(
    monkeypatch: pytest.MonkeyPatch,
    plugin: Path,
    canonical: Path,
    cache_base: Path,
    *extra: str,
) -> None:
    """Set one complete validator command line."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["codex_plugin_redirects.py", str(plugin), str(canonical), str(cache_base), *extra],
    )


@pytest.mark.parametrize(
    ("installed", "location"),
    [(False, "plugin source"), (True, "installed cache")],
)
def test_main_accepts_valid_source_and_installed_redirects(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    installed: bool,
    location: str,
) -> None:
    """Both supported adapter roots use links relative to the future cache."""
    canonical, plugin, cache_base = _roots(tmp_path)
    cache_root = cache_base / _VERSION
    adapter = cache_root if installed else plugin
    _write_valid_redirects(adapter, canonical, cache_root)
    extra = ("--installed",) if installed else ()
    _set_argv(monkeypatch, plugin, canonical, cache_base, *extra)

    assert codex_plugin_redirects.main() == 0
    assert f"in {location}:" in capsys.readouterr().out


@pytest.mark.parametrize("write_wrong", [False, True])
def test_main_reports_every_missing_or_wrong_redirect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    write_wrong: bool,
) -> None:
    """Instruction, skill, and rule diagnostics are accumulated together."""
    canonical, plugin, cache_base = _roots(tmp_path)
    if write_wrong:
        for path in (
            plugin / "instructions" / "sample.md",
            plugin / "skills" / "sample" / "SKILL.md",
            plugin / "rules" / "docs_layout.md",
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("wrong\n", encoding="utf-8")
    _set_argv(monkeypatch, plugin, canonical, cache_base)

    assert codex_plugin_redirects.main() == 1
    error = capsys.readouterr().err
    expected = "wrong cache-relative redirect" if write_wrong else "missing"
    assert error.count(expected) == _REDIRECT_KIND_COUNT


@pytest.mark.parametrize("version", [None, ""])
def test_plugin_version_rejects_missing_or_empty_value(tmp_path: Path, version: object) -> None:
    """The cache directory cannot be derived without a non-empty string version."""
    manifest = tmp_path / ".codex-plugin" / "plugin.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"version": version}), encoding="utf-8")

    with pytest.raises(ValueError, match="missing plugin version"):
        codex_plugin_redirects._plugin_version(tmp_path)


def test_script_guard_exits_with_main_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Direct execution delegates to the same validated CLI entry point."""
    canonical, plugin, cache_base = _roots(tmp_path)
    _write_valid_redirects(plugin, canonical, cache_base / _VERSION)
    _set_argv(monkeypatch, plugin, canonical, cache_base)

    with pytest.raises(SystemExit) as raised:
        runpy.run_path(codex_plugin_redirects.__file__, run_name="__main__")

    assert raised.value.code == 0


# eof
