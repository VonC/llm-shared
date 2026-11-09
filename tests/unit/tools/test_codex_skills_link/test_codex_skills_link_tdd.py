"""Tests for llmup, the link that shows the llm-shared skills to Codex.

``tools/codex_skills_link.py`` validates the skill package read-only, checks
that ``<home>/.agents/skills`` links to the clone's package skills, creates
that link only with ``--create`` when the folder is absent or empty, refuses
anything else unchanged, and warns when the Codex configuration still enables
an ``llm-shared@`` plugin. Every scenario runs in the virtual scratch tree:
no real profile, Codex configuration or junction is touched, and a junction
is declared without calling the kernel.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from tests.script_entry import run_main
from tests.unit.tools.codex_skill_clone import (
    CANONICAL_FILES,
    PACKAGE_FILES,
    write_clone,
)
from tools import codex_skills_link as tool

_SKILLS = Path(".agents") / "llm-shared" / "skills"
_ENABLED = (
    '[plugins."github@openai-curated"]\nenabled = true\n\n'
    '[plugins."llm-shared@personal"]\nenabled = true\n'
)
_ON_WINDOWS = pytest.mark.skipif(os.name != "nt", reason="junctions exist on Windows only")


def _layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Return a valid clone, an empty home, and the user skills folder path."""
    clone = write_clone(tmp_path / "clone")
    home = tmp_path / "home"
    home.mkdir()
    return clone, home, home / ".agents" / "skills"


def _run(clone: Path, home: Path, *extra: str) -> int:
    """Run llmup for the clone with an explicit home and Codex home."""
    return tool.main(["--home", str(home), "--codex-home", str(home / ".codex"), *extra], clone=clone)


def _clone_state(clone: Path) -> tuple[dict[str, bytes], list[str], list[str]]:
    """Observe the clone's files and folders, to prove llmup never writes there."""
    files = {relative: (clone / relative).read_bytes() for relative in (*CANONICAL_FILES, *PACKAGE_FILES)}
    agents = sorted(path.name for path in (clone / ".agents").iterdir())
    return files, agents, sorted(path.name for path in (clone / _SKILLS).iterdir())


def test_absent_link_is_reported_with_the_create_command(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without --create, a missing folder exits 2, names the command and creates nothing."""
    clone, home, link = _layout(tmp_path)

    assert _run(clone, home) == tool.EXIT_NO_LINK

    out, err = capsys.readouterr()
    assert f"OK: 1 skills and their clone-relative redirects are valid in {clone / '.agents' / 'llm-shared'}" in out
    assert f"MISSING: {link} is absent, not a link to {clone / _SKILLS}." in err
    assert f'"{clone / "bin" / "codex_skills_link.bat"}" --create (llmup --create)' in err
    assert not (home / ".agents").exists()


def test_create_links_the_folder_and_never_writes_in_the_clone(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--create makes the folder link, reads it back, and a second run only checks it."""
    clone, home, link = _layout(tmp_path)
    before = _clone_state(clone)

    assert _run(clone, home, "--create") == tool.EXIT_READY

    assert link.is_junction() if os.name == "nt" else link.is_symlink()
    assert tool.link_state(link, clone / _SKILLS) is tool.LinkState.LINKED
    assert (link / "sample" / "SKILL.md").is_file()
    assert f"CREATED: {link} links to {clone / _SKILLS}\n{tool.NEW_THREAD}" in capsys.readouterr().out
    assert _clone_state(clone) == before

    assert _run(clone, home, "--create") == tool.EXIT_READY
    assert f"OK: {link} links to {clone / _SKILLS}" in capsys.readouterr().out


@pytest.mark.parametrize("windows", [pytest.param(True, marks=_ON_WINDOWS, id="junction"),
                                     pytest.param(False, id="symlink")])
def test_existing_link_to_the_clone_is_accepted(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    *,
    windows: bool,
) -> None:
    """A junction or a symbolic link to the package skills both pass without --create."""
    clone, home, link = _layout(tmp_path)
    tool.create_link(link, clone / _SKILLS, windows=windows)

    assert link.is_junction() is windows
    assert _run(clone, home) == tool.EXIT_READY
    assert f"OK: {link} links to {clone / _SKILLS}" in capsys.readouterr().out


def test_empty_folder_waits_for_create_then_becomes_the_link(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An empty folder is not a link yet: only --create replaces it."""
    clone, home, link = _layout(tmp_path)
    link.mkdir(parents=True)

    assert _run(clone, home) == tool.EXIT_NO_LINK
    assert f"MISSING: {link} is an empty folder" in capsys.readouterr().err
    assert link.is_dir()
    assert not link.is_junction()

    assert _run(clone, home, "--create") == tool.EXIT_READY
    assert tool.link_state(link, clone / _SKILLS) is tool.LinkState.LINKED


def _refused(clone: Path, home: Path, capsys: pytest.CaptureFixture[str], *, create: bool) -> str:
    """Run llmup, check it refused without change, and return its stderr."""
    assert _run(clone, home, *(("--create",) if create else ())) == tool.EXIT_REFUSED
    err = capsys.readouterr().err
    assert f"REFUSED: {home / '.agents' / 'skills'} " in err
    assert "Nothing changed." in err
    return err


@pytest.mark.parametrize("create", [False, True])
def test_a_folder_with_content_is_refused_and_kept(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    *,
    create: bool,
) -> None:
    """A user skills folder holding its own skills is never replaced."""
    clone, home, link = _layout(tmp_path)
    (link / "own-skill").mkdir(parents=True)

    assert "is a folder or file with other content" in _refused(clone, home, capsys, create=create)
    assert (link / "own-skill").is_dir()


@pytest.mark.parametrize("create", [False, True])
def test_a_file_in_place_of_the_folder_is_refused_and_kept(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    *,
    create: bool,
) -> None:
    """A file named like the user skills folder is never replaced."""
    clone, home, link = _layout(tmp_path)
    link.parent.mkdir()
    link.write_text("not a folder\n", encoding="utf-8")

    _refused(clone, home, capsys, create=create)
    assert link.read_text(encoding="utf-8") == "not a folder\n"


@pytest.mark.parametrize("create", [False, True])
def test_a_link_to_another_folder_is_refused_and_kept(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    *,
    create: bool,
) -> None:
    """A link to another folder, such as another clone, is reported and never replaced."""
    clone, home, link = _layout(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    tool.create_link(link, other)

    err = _refused(clone, home, capsys, create=create)
    assert f"links to {other.resolve()}, not to {clone / _SKILLS}" in err
    assert link.resolve() == other.resolve()


def test_a_link_inside_the_clone_is_refused(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A home inside the clone would put the link there: llmup refuses to write it."""
    clone = write_clone(tmp_path / "clone")
    before = _clone_state(clone)

    exit_code = tool.main(
        ["--home", str(clone), "--codex-home", str(tmp_path / "codex"), "--create"],
        clone=clone,
    )

    assert exit_code == tool.EXIT_REFUSED
    assert f"REFUSED: {clone / '.agents' / 'skills'} is inside the clone" in capsys.readouterr().err
    assert _clone_state(clone) == before


@pytest.mark.parametrize("damaged", ["skills/sample/SKILL.md", "rules/docs_layout.md"])
def test_invalid_package_stops_before_the_link(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    damaged: str,
) -> None:
    """A broken wrapper or redirect exits 1 even with --create, and no link appears."""
    clone, home, _ = _layout(tmp_path)
    (clone / ".agents" / "llm-shared" / damaged).write_text("wrong\n", encoding="utf-8")

    assert _run(clone, home, "--create") == tool.EXIT_INVALID_PACKAGE

    out, err = capsys.readouterr()
    assert out == ""
    assert f"ERROR: wrong clone-relative redirect: {clone / '.agents' / 'llm-shared' / damaged}" in err
    assert "The link was not checked." in err
    assert not (home / ".agents").exists()


@pytest.mark.parametrize(
    ("config", "removals"),
    [
        (None, ()),
        ("model = 'gpt'\n", ()),
        ("plugins = 3\n", ()),
        ('[plugins."llm-shared@personal"]\nenabled = false\n', ()),
        (_ENABLED, ("llm-shared@personal",)),
        ('plugins = { "llm-shared@team" = 1, other = 2 }\n', ("llm-shared@team",)),
        ('[plugins."llm-shared@team"]\n\n[plugins."llm-shared@personal"]\nenabled = true\n',
         ("llm-shared@personal", "llm-shared@team")),
    ],
)
def test_still_enabled_plugin_is_warned_without_changing_the_exit_code(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    config: str | None,
    removals: tuple[str, ...],
) -> None:
    """Each enabled llm-shared plugin gets its remove command; others are ignored."""
    clone, home, link = _layout(tmp_path)
    tool.create_link(link, clone / _SKILLS)
    if config is not None:
        (home / ".codex").mkdir()
        (home / ".codex" / "config.toml").write_text(config, encoding="utf-8")

    assert _run(clone, home) == tool.EXIT_READY

    err = capsys.readouterr().err
    commands = "".join(f"  codex plugin remove {name}\n" for name in removals)
    assert err == (
        f"WARNING: {home / '.codex' / 'config.toml'} still enables {', '.join(removals)}:"
        f" Codex would list every llm-shared skill twice. Remove the plugin with:\n{commands}"
        if removals
        else ""
    )


@pytest.mark.parametrize("content", [b"[plugins\n", b"model = '\xff'\n"])
def test_unreadable_codex_config_is_warned(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    content: bytes,
) -> None:
    """Invalid TOML or bytes ask for a manual check and keep the link verdict."""
    clone, home, _ = _layout(tmp_path)
    (home / ".codex").mkdir()
    (home / ".codex" / "config.toml").write_bytes(content)

    assert _run(clone, home) == tool.EXIT_NO_LINK

    err = capsys.readouterr().err
    assert f"WARNING: cannot read {home / '.codex' / 'config.toml'} (" in err
    assert '[plugins."llm-shared@<marketplace>"] entry is enabled there.' in err


@pytest.mark.parametrize("variable", [False, True])
def test_default_locations_follow_the_user_home_and_codex_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    variable: bool,
) -> None:
    """Without options the home is the user's and the config is CODEX_HOME's, else <home>/.codex."""
    clone, home, link = _layout(tmp_path)
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("HOME", str(home))
    codex = tmp_path / "codex" if variable else home / ".codex"
    if variable:
        monkeypatch.setenv("CODEX_HOME", str(codex))
    else:
        monkeypatch.delenv("CODEX_HOME", raising=False)
    codex.mkdir()
    (codex / "config.toml").write_text(_ENABLED, encoding="utf-8")

    assert tool.main([], clone=clone) == tool.EXIT_NO_LINK

    err = capsys.readouterr().err
    assert f"MISSING: {link} is absent" in err
    assert f"WARNING: {codex / 'config.toml'} still enables llm-shared@personal" in err


def test_failed_or_unverified_creation_exits_4(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An operating-system refusal and a link that does not read back both fail."""
    clone, home, link = _layout(tmp_path)

    def refuse(target_link: Path, skills: Path) -> None:
        message = f"cannot link {target_link} to {skills}"
        raise PermissionError(message)

    def do_nothing(target_link: Path, skills: Path) -> None:
        del target_link, skills

    monkeypatch.setattr(tool, "create_link", refuse)
    assert _run(clone, home, "--create") == tool.EXIT_LINK_FAILED
    assert f"FAILED: cannot create {link}: cannot link" in capsys.readouterr().err

    monkeypatch.setattr(tool, "create_link", do_nothing)
    assert _run(clone, home, "--create") == tool.EXIT_LINK_FAILED
    assert f"FAILED: {link} was created but does not link to {clone / _SKILLS}" in capsys.readouterr().err


def test_unknown_option_exits_with_the_usage_code(capsys: pytest.CaptureFixture[str]) -> None:
    """A usage error exits 5, never 2, which means a missing link."""
    with pytest.raises(SystemExit) as raised:
        tool.main(["--bogus"])

    assert raised.value.code == tool.EXIT_USAGE
    assert "unrecognized arguments: --bogus" in capsys.readouterr().err


def test_script_guard_runs_the_same_command_line(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Direct execution, as the launcher runs it, reaches the same parser.

    Asking for help keeps this test off the repository's 42-skill package,
    which the package and structure tests already validate.
    """
    monkeypatch.setattr(sys, "argv", ["codex_skills_link.py", "--help"])

    with pytest.raises(SystemExit) as raised:
        run_main(tool.__file__)

    assert raised.value.code == 0
    out = capsys.readouterr().out
    assert "--create" in out
    assert "Never writes inside the clone." in " ".join(out.split())


# eof
