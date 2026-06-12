"""Unit and acceptance tests for ghog init, the AT12 scenario (Q23).

Cover the skill pointer writing (with a relative link resolving to the
real instruction file), the AGENTS.md creation, append and
already-registered cases, the CLI exit codes, and the missing
instruction-file setup error.

Fix: the generated AGENTS.md section and Codex prompt now name the Q32
lifecycle (the ``a.ghog.status`` completion proof, the ``ghog status``
poll, the detached walk), so both creation tests assert that wording —
a consumer registered after Q32 must route the timeout case correctly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.groundhog import cli, init_files
from tools.groundhog.models import EXIT_OBJECTIVE_MET, EXIT_SETUP_ERROR

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_instruction_path_exists() -> None:
    """The single instruction source of Q13 ships with llm-shared."""
    assert init_files.instruction_path().is_file()


def test_skill_pointer_links_back_to_the_instruction(tmp_path: Path) -> None:
    """The SKILL.md relative link resolves to the real instruction file."""
    skill = init_files.write_skill_pointer(tmp_path)
    assert skill == tmp_path.joinpath(
        *init_files.SKILL_DIR_PARTS,
        init_files.SKILL_FILE_NAME,
    )
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---\nname: groundhog\n")
    link = text.rsplit("(", 1)[1].rstrip(").\n")
    resolved = (skill.parent / link).resolve()
    assert resolved == init_files.instruction_path().resolve()


def test_agents_md_is_created_with_the_section(tmp_path: Path) -> None:
    """Without an AGENTS.md, init creates one with a title and section.

    The section carries the Q32 lifecycle wording: the completion
    proof, the status poll and the detached walk.
    """
    path, added = init_files.update_agents_md(tmp_path)
    assert added is True
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Agent instructions")
    assert init_files.AGENTS_MARKER in text
    assert "instructions/groundhog.md" in text
    assert "a.ghog.status" in text
    assert "ghog status" in text
    assert "ghog day --detach" in text


def test_agents_md_is_appended_not_clobbered(tmp_path: Path) -> None:
    """An existing AGENTS.md keeps its content, the section is appended."""
    agents = tmp_path / init_files.AGENTS_FILE_NAME
    agents.write_text("# My project\n\nExisting rules.\n", encoding="utf-8")
    path, added = init_files.update_agents_md(tmp_path)
    assert added is True
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# My project\n\nExisting rules.\n")
    assert init_files.AGENTS_MARKER in text


def test_agents_md_registration_is_idempotent(tmp_path: Path) -> None:
    """A second init recognizes the section and rewrites nothing."""
    init_files.update_agents_md(tmp_path)
    before = (tmp_path / init_files.AGENTS_FILE_NAME).read_text(encoding="utf-8")
    path, added = init_files.update_agents_md(tmp_path)
    assert added is False
    assert path.read_text(encoding="utf-8") == before


def test_agents_md_mid_line_mention_is_not_a_registration(tmp_path: Path) -> None:
    """A mid-line mention of the marker does not block the section."""
    agents = tmp_path / init_files.AGENTS_FILE_NAME
    agents.write_text(
        "# My project\n\nSee the ## groundhog notes elsewhere.\n",
        encoding="utf-8",
    )
    path, added = init_files.update_agents_md(tmp_path)
    assert added is True
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# My project\n\nSee the ## groundhog notes elsewhere.\n")
    assert f"\n{init_files.AGENTS_MARKER}" in text


def test_agents_md_not_utf8_is_left_untouched(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT12: an unreadable AGENTS.md aborts with exit 5, byte-identical."""
    agents = tmp_path / init_files.AGENTS_FILE_NAME
    original = b"\xff\xfeBinary-ish content"
    agents.write_bytes(original)
    deps = cli.Deps(home=lambda: tmp_path / "home")
    code = cli.main(["init", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_SETUP_ERROR
    assert agents.read_bytes() == original
    out = capsys.readouterr().out
    assert "not UTF-8 readable" in out
    assert "exit=5" in out


def test_run_init_reports_all_files(tmp_path: Path) -> None:
    """run_init names the written files, the Codex state and the trigger."""
    home = tmp_path / "home"
    home.mkdir()
    lines = init_files.run_init(tmp_path, home)
    assert lines[0].startswith("Skill pointer written:")
    assert lines[1].startswith("AGENTS.md section added:")
    assert lines[2].startswith("Codex not detected")
    assert "run groundhog" in lines[3]
    again = init_files.run_init(tmp_path, home)
    assert again[1].startswith("AGENTS.md already references groundhog:")


def test_codex_prompt_written_when_codex_is_set_up(tmp_path: Path) -> None:
    """With ~/.codex present, init writes the /groundhog prompt (Q25)."""
    home = tmp_path / "home"
    (home / init_files.CODEX_DIR_NAME).mkdir(parents=True)
    lines = init_files.run_init(tmp_path, home)
    assert lines[2].startswith("Codex /groundhog prompt written:")
    prompt = (
        home
        / init_files.CODEX_DIR_NAME
        / init_files.CODEX_PROMPTS_DIR
        / init_files.CODEX_PROMPT_FILE
    )
    assert prompt.is_file()
    text = prompt.read_text(encoding="utf-8")
    assert "AGENTS.md" in text
    assert "no `groundhog` executable" in text
    assert "a.ghog.status" in text
    assert "ghog day --detach" in text


def test_cli_init_exits_zero_with_the_grammar(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT12: ghog init succeeds with the closing-line grammar (Q16)."""
    deps = cli.Deps(home=lambda: tmp_path / "home")
    code = cli.main(["init", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "Skill pointer written:" in out
    assert "ghog init done" in out
    assert "exit=0" in out
    assert (tmp_path / init_files.AGENTS_FILE_NAME).is_file()


def test_cli_init_without_the_instruction_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AT12: a missing instruction file is the loud setup error."""

    def _missing() -> Path:
        return tmp_path / "absent" / "groundhog.md"

    monkeypatch.setattr(init_files, "instruction_path", _missing)
    deps = cli.Deps(home=lambda: tmp_path / "home")
    code = cli.main(["init", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_SETUP_ERROR
    out = capsys.readouterr().out
    assert "instruction file not found" in out
    assert "exit=5" in out


# eof
