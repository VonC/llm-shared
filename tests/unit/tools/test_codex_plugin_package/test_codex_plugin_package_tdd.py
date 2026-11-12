"""Tests for the read-only validation of the llm-shared Codex skill package.

``tools/codex_plugin_package.py`` validates the manifest and every wrapper
with the standard library, so ``llmup`` needs neither the Codex plugin-creator
scripts nor PyYAML.

Fix: typed JSON access keeps strict pyright clean.

Fix: Codex reads the package through the user skills folder link, so no
cachebuster is written any more: the ``bump-version`` and
``marketplace-name`` commands are gone, the shipped manifest keeps a plain
version, and ``validate`` is the only command left.

Locate the shipped package through its own module, so this repository contract
does not collect unrelated prompt-workflow dependency fingerprints.
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from tools import codex_plugin_package

_VERSION = "0.1.0"
_DEFAULT_HEADER = 'name: sample\ndescription: "Run the sample workflow."\n'


def _write_skill(root: Path, folder: str, header: str = _DEFAULT_HEADER) -> Path:
    """Write one wrapper with the given front matter body."""
    skill = root / "skills" / folder / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_bytes(
        f"---\n{header}---\n\nRead and follow [the canonical instruction](x.md)\n".encode(),
    )
    return skill


def _package(tmp_path: Path, **overrides: object) -> Path:
    """Create a valid one-skill package; a None override drops that manifest key."""
    root = tmp_path / "llm-shared"
    (root / ".codex-plugin").mkdir(parents=True)
    manifest = {"version": _VERSION, "name": "llm-shared", "skills": "./skills/"} | overrides
    data = {key: value for key, value in manifest.items() if value is not None}
    (root / ".codex-plugin" / "plugin.json").write_bytes(
        (json.dumps(data, indent=2) + "\n").encode(),
    )
    _write_skill(root, "sample")
    return root


def test_repository_package_is_valid_with_a_plain_version() -> None:
    """The shipped package passes the checks llmup runs, with no cachebuster suffix."""
    root = Path(codex_plugin_package.__file__).resolve().parent.parent / ".agents" / "llm-shared"

    errors, count = codex_plugin_package.validate_package(root)
    manifest = json.loads((root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    assert errors == []
    assert count == len([path for path in (root / "skills").iterdir() if path.is_dir()])
    assert manifest["version"] == _VERSION


def test_main_validate_reports_the_skill_count(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A valid package prints how many wrappers it checked."""
    root = _package(tmp_path)

    assert codex_plugin_package.main(["validate", str(root)]) == 0
    assert "Validated 1 skills in plugin package:" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("name: sample\n", "description must be a non-empty string"),
        ("name: Sample\ndescription: x\n", "name must be hyphen-case"),
        ("name: other\ndescription: x\n", "name 'other' differs from its folder 'sample'"),
        ('name: sample\ndescription: "a <b> c"\n', "without < or >"),
        (f"name: sample\ndescription: {'x' * 1025}\n", "at most 1024 characters"),
        ("name: sample\ndescription: x\nextra: y\n", "unexpected front matter key 'extra'"),
        ("name: sample\ndescription: x\nmetadata: flat\n", "metadata must be a mapping"),
        ("name: sample\ndescription: x\nllm_nature: claude\n", "llm_nature must be codex"),
        ("name: sample\nname: sample\ndescription: x\n", "duplicate front matter key 'name'"),
        ("name sample\ndescription: x\n", "unsupported front matter line"),
        ("  indented: x\nname: sample\ndescription: x\n", "unsupported front matter line"),
        ("metadata:\n  a: x\nname: sample\n  b: y\ndescription: x\n", "unsupported front matter line"),
        ("name: sample\ndescription: x\nmetadata:\n    deep: x\n", "unsupported front matter line"),
        ("name: sample\ndescription: x\nmetadata:\n  deep:\n", "unsupported front matter line"),
        ("name: sample\ndescription: x\nmetadata:\n  a: x\n  a: y\n", "duplicate front matter key 'a'"),
        ('name: sample\ndescription: "bad \\q escape"\n', "invalid double-quoted value"),
    ],
)
def test_front_matter_problems_name_the_wrapper(
    tmp_path: Path,
    header: str,
    expected: str,
) -> None:
    """Each rejected front matter reports one problem with the wrapper path."""
    root = _package(tmp_path)
    skill = _write_skill(root, "sample", header)

    errors, _ = codex_plugin_package.validate_package(root)

    assert len(errors) == 1
    assert expected in errors[0]
    assert str(skill) in errors[0]


def test_supported_front_matter_forms_are_accepted(tmp_path: Path) -> None:
    """Plain, quoted, metadata and adapter-hint forms all parse to their values."""
    header = (
        "name: sample\n"
        "description: 'It''s the sample workflow.'\n"
        "llm_nature: codex\n"
        "metadata:\n"
        '  owner: "VonC"\n'
        "  tier: core\n"
    )
    root = _package(tmp_path)
    skill = _write_skill(root, "sample", header)

    errors, _ = codex_plugin_package.validate_package(root)
    fields = codex_plugin_package._frontmatter(skill.read_text(encoding="utf-8"))

    assert errors == []
    assert fields["description"] == "It's the sample workflow."
    assert fields["metadata"] == {"owner": "VonC", "tier": "core"}


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (b"\xef\xbb\xbf---\nname: sample\ndescription: x\n---\n", "UTF-8 BOM"),
        (b"name: sample\ndescription: x\n", "closed --- front matter"),
        (b"---\nname: sample\ndescription: x\n", "closed --- front matter"),
        (b"---\nname: sample\ndescription: \xff\n---\n", "not UTF-8"),
    ],
)
def test_wrapper_file_problems_are_reported(
    tmp_path: Path,
    content: bytes,
    expected: str,
) -> None:
    """A BOM, a missing or unclosed header, or non-UTF-8 bytes stop the wrapper check."""
    root = _package(tmp_path)
    skill = root / "skills" / "sample" / "SKILL.md"
    skill.write_bytes(content)

    errors, _ = codex_plugin_package.validate_package(root)

    assert errors == [f"{expected}: {skill}"]


def test_skill_folders_without_wrapper_or_any_folder_are_reported(tmp_path: Path) -> None:
    """A folder needs SKILL.md, plain files are ignored, and an empty root is an error."""
    root = _package(tmp_path)
    (root / "skills" / "notes.txt").write_text("not a skill\n", encoding="utf-8")
    (root / "skills" / "empty").mkdir()

    errors, count = codex_plugin_package.validate_package(root)

    assert count == 2  # noqa: PLR2004 - the sample and empty folders
    assert errors == [f"missing SKILL.md: {root / 'skills' / 'empty' / 'SKILL.md'}"]

    for folder in ("empty", "sample"):
        for path in (root / "skills" / folder).glob("*"):
            path.unlink()
        (root / "skills" / folder).rmdir()
    errors, count = codex_plugin_package.validate_package(root)

    assert count == 0
    assert errors == [f"no skill folder under {root / 'skills'}"]


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({"name": "LLM"}, "manifest name must be hyphen-case"),
        ({"name": "other"}, "manifest name 'other' differs from its folder 'llm-shared'"),
        ({"version": "1.0"}, "manifest version must be a semantic version"),
        ({"version": None}, "manifest version must be a semantic version"),
    ],
)
def test_manifest_field_problems_still_check_the_skills(
    tmp_path: Path,
    overrides: dict[str, object],
    expected: str,
) -> None:
    """Name and version problems are reported alongside the skill checks."""
    root = _package(tmp_path, **overrides)

    errors, count = codex_plugin_package.validate_package(root)

    assert count == 1
    assert len(errors) == 1
    assert expected in errors[0]


@pytest.mark.parametrize(
    ("overrides", "manifest_text", "expected"),
    [
        ({}, "", "unreadable manifest"),
        ({}, "{not json", "unreadable manifest"),
        ({}, "[]", "manifest must be a JSON object"),
        ({"skills": None}, None, "skills must be a ./ relative path"),
        ({"skills": "../outside/"}, None, "skills must be a ./ relative path"),
        ({"skills": "./../outside/"}, None, "skills must stay inside the plugin root"),
        ({"skills": "./missing/"}, None, "is not a directory"),
    ],
)
def test_unusable_manifest_or_skills_path_stops_validation(
    tmp_path: Path,
    overrides: dict[str, object],
    manifest_text: str | None,
    expected: str,
) -> None:
    """Without a readable manifest and skills folder, no skill is checked."""
    root = _package(tmp_path, **overrides)
    manifest = root / ".codex-plugin" / "plugin.json"
    if manifest_text == "":
        manifest.unlink()
    elif manifest_text is not None:
        manifest.write_text(manifest_text, encoding="utf-8")

    errors, count = codex_plugin_package.validate_package(root)

    assert count == 0
    assert len(errors) == 1
    assert expected in errors[0]


@pytest.mark.parametrize("command", ["bump-version", "marketplace-name"])
def test_plugin_install_commands_are_gone(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    command: str,
) -> None:
    """Only validate remains: nothing rewrites the manifest or reads a marketplace."""
    root = _package(tmp_path)
    manifest = root / ".codex-plugin" / "plugin.json"
    before = manifest.read_bytes()

    with pytest.raises(SystemExit) as raised:
        codex_plugin_package.main([command, str(root)])

    assert raised.value.code == 2  # noqa: PLR2004 - argparse usage error
    assert "invalid choice" in capsys.readouterr().err
    assert manifest.read_bytes() == before


def test_main_validate_prints_every_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every problem is written to stderr and the command fails."""
    root = _package(tmp_path, name="other")
    _write_skill(root, "sample", "name: sample\n")

    assert codex_plugin_package.main(["validate", str(root)]) == 1

    assert capsys.readouterr().err.count("ERROR: ") == 2  # noqa: PLR2004 - manifest and wrapper


def test_script_guard_exits_with_main_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Direct execution delegates to the same command-line entry point."""
    root = _package(tmp_path)
    monkeypatch.setattr(sys, "argv", ["codex_plugin_package.py", "validate", str(root)])

    with pytest.raises(SystemExit) as raised:
        runpy.run_path(codex_plugin_package.__file__, run_name="__main__")

    assert raised.value.code == 0


# eof
