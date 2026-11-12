"""Tests for `tools.spell_check`, the Code Spell Checker findings outside VS Code.

The check must report the words the VS Code Problems panel shows: the merged
``cSpell.*`` settings of the user, workspace and folder levels, the installed
language extensions, a pinned cspell on a recent enough Node, and every word
grouped with its locations and suggestions. ``add-words`` must insert the
accepted words at their place in ``cSpell.words`` without touching anything
else. No test starts a process: Node, npm and cspell answer through a stand-in.

Fix: spelling is checked on Markdown files only, never on source code (user
decision of 2026-11-08): ``check`` drops every other file and runs nothing
when no Markdown file remains.

Fix: a Node older than 22.18 no longer stops the check: cspell 9 runs on a
Node 20.18 or later, and the chosen Node comes first on the PATH of npm and
cspell.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any, cast

import pytest

from tests.script_entry import run_main
from tools import spell_check as sc

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

REPORT: dict[str, Any] = {
    "issues": [
        {
            "text": "collectreport", "row": 938, "col": 12,
            "uri": "file:///ROOT/docs/review.md",
            "suggestions": ["collecteront"],
        },
        {
            "text": "gcba", "row": 3, "col": 13,
            "uri": "file:///ROOT/docs/review.md",
            "suggestions": ["relieve", "receive", "received", "receiver", "receives", "recipe"],
            "suggestionsEx": [{"word": "receive", "isPreferred": True}, {"word": "relieve"}],
        },
        {
            "text": "collectreport", "row": 1216, "col": 30,
            "uri": "file:///ROOT/docs/review.md",
        },
    ],
}


def _done(command: Sequence[str], code: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    """Return one finished stand-in process."""
    return subprocess.CompletedProcess(list(command), code, stdout=stdout, stderr=stderr)


def _report_for(root: Path) -> str:
    """Return the sample report with its URIs under ``root``."""
    return json.dumps(REPORT).replace("file:///ROOT", root.resolve().as_uri())


def _user_dirs(tmp_path: Path) -> dict[str, str]:
    """Create VS Code user settings, a French extension and a Node link; return the environment."""
    appdata = tmp_path / "appdata"
    (appdata / "Code" / "User").mkdir(parents=True)
    (appdata / "Code" / "User" / "settings.json").write_text(
        '{\n  // user level\n  "cSpell.language": "en,fr",\n  "cSpell.userWords": ["Aaaah",],\n}\n',
        encoding="utf-8",
    )
    extension = tmp_path / "profile" / ".vscode" / "extensions" / "streetsidesoftware.code-spell-checker-french-1.0.1"
    (extension / "static").mkdir(parents=True)
    (extension / "static" / "cspell-ext.json").write_text("{}", encoding="utf-8")
    node = tmp_path / "prgs" / "nodes" / "node22" / "node.exe"
    node.parent.mkdir(parents=True)
    node.write_bytes(b"")
    return {"APPDATA": str(appdata), "USERPROFILE": str(tmp_path / "profile"), "PRGS": str(tmp_path / "prgs"), "PATH": ""}


def test_load_jsonc_drops_comments_and_trailing_commas_but_keeps_strings() -> None:
    """VS Code settings may hold comments and trailing commas; strings stay intact."""
    text = '{\n  // line\n  "a": "x // y /* z */",\n  /* block */\n  "b": [1, 2,],\n  "c": ",]",\n}\n'
    assert sc.load_jsonc(text) == {"a": "x // y /* z */", "b": [1, 2], "c": ",]"}


def test_read_levels_merges_user_workspace_and_folder_settings(tmp_path: Path) -> None:
    """Word lists are joined across levels and the most specific scalar wins."""
    user = tmp_path / "user.json"
    user.write_text('{"cSpell.language": "en,fr", "cSpell.userWords": ["déjà"], "editor.x": 1}', encoding="utf-8")
    vscode = tmp_path / ".vscode"
    vscode.mkdir()
    (vscode / "a.code-workspace").write_text('{"settings": {"cSpell.words": ["glovebox"]}}', encoding="utf-8")
    (vscode / "b.code-workspace").write_text('{"settings": []}', encoding="utf-8")
    (vscode / "settings.json").write_text(
        '{"cSpell.words": ["ghog"], "cSpell.language": "en", "cSpell.flagWords": "not a list"}', encoding="utf-8",
    )

    levels = sc.read_levels(tmp_path, user)
    config = sc.merge_settings(levels)

    assert levels[0] == {"language": "en,fr", "userWords": ["déjà"]}
    assert config == {"version": "0.2", "language": "en", "userWords": ["déjà"], "words": ["glovebox", "ghog"]}
    assert sc.read_levels(tmp_path / "missing", None) == []
    assert sc.read_levels(tmp_path / "missing", tmp_path / "absent.json") == []


@pytest.mark.parametrize(
    ("content", "expected"),
    [(b"{oops", "unreadable VS Code settings"), (b"[]", "hold no JSON object"), (b"\x80{}", "unreadable VS Code settings")],
)
def test_unusable_settings_fail_with_the_file_named(tmp_path: Path, content: bytes, expected: str) -> None:
    """Invalid JSON, a non-object or undecodable bytes stop the check with the file named."""
    settings = tmp_path / "settings.json"
    settings.write_bytes(content)
    with pytest.raises(sc.SpellCheckError, match=expected) as raised:
        sc.read_levels(tmp_path / "none", settings)
    assert str(settings) in str(raised.value)


def test_language_imports_keep_the_newest_language_extension(tmp_path: Path) -> None:
    """Each language extension's static config is imported once, newest version first chosen."""
    assert sc.language_imports(None) == []
    assert sc.language_imports(tmp_path / "missing") == []
    for name in ("code-spell-checker-4.10.0", "code-spell-checker-french-1.0.1", "code-spell-checker-french-1.2.0",
                 "code-spell-checker-french-1.0.9", "code-spell-checker-german-2.0.0"):
        folder = tmp_path / f"streetsidesoftware.{name}"
        folder.mkdir()
        if "-4.10.0" not in name:
            (folder / "static").mkdir()
            (folder / "static" / "cspell-ext.json").write_text("{}", encoding="utf-8")

    imports = sc.language_imports(tmp_path)

    assert [path.split("/")[-3] for path in imports] == [
        "streetsidesoftware.code-spell-checker-french-1.2.0",
        "streetsidesoftware.code-spell-checker-german-2.0.0",
    ]


def test_default_sources_and_build_config_follow_the_user_folders(tmp_path: Path) -> None:
    """APPDATA and USERPROFILE (or HOME) locate the settings and extensions."""
    environ = _user_dirs(tmp_path)
    sources = sc.default_sources(environ)
    config = sc.build_config(tmp_path, sources)
    assert config["language"] == "en,fr"
    assert config["userWords"] == ["Aaaah"]
    assert len(config["import"]) == 1
    assert sc.default_sources({"HOME": str(tmp_path)}).extensions_dir == tmp_path / ".vscode" / "extensions"
    assert sc.default_sources({}) == sc.SettingsSources(None, None)
    assert "import" not in sc.build_config(tmp_path, sc.SettingsSources(None, None))


def test_find_node_takes_the_first_recent_enough_node(tmp_path: Path) -> None:
    """PATH comes first, then the senv links newest first; old or broken ones are skipped."""
    path_dir = tmp_path / "path"
    path_dir.mkdir()
    (path_dir / "node.exe").write_bytes(b"")
    for link in ("node9", "node22", "node14"):
        (tmp_path / "nodes" / link).mkdir(parents=True)
        (tmp_path / "nodes" / link / "node.exe").write_bytes(b"")
    environ = {"PATH": str(path_dir), "PRGS": str(tmp_path)}
    versions = {"path": (0, "v22.9.0"), "node22": (0, "v22.23.4\n")}

    def run(command: Sequence[str], **_: object) -> subprocess.CompletedProcess[str]:
        code, version = versions.get(command[0].split("\\")[-2], (1, ""))
        return _done(command, code, version)

    candidates = sc.node_candidates(environ)
    assert [node.parent.name for node in candidates] == ["path", "node22", "node14", "node9"]
    node, cspell = sc.find_node(environ, run)
    assert (node.parent.name, cspell) == ("node22", "10.4.1")

    versions.pop("node22")
    node, cspell = sc.find_node(environ, run)
    assert (node.parent.name, cspell) == ("path", "9.8.0")

    versions["path"] = (0, "v18.20.0")
    with pytest.raises(sc.SpellCheckError) as raised:
        sc.find_node(environ, run)
    message = str(raised.value)
    assert "cspell needs Node 20.18 or later" in message
    assert "(18.20.0)" in message
    assert "(unknown version)" in message
    assert "dwl_inst_ver node 22" in message
    with pytest.raises(sc.SpellCheckError, match="found: none"):
        sc.find_node({"PATH": ""}, run)


def test_node_environment_puts_the_chosen_node_first(tmp_path: Path) -> None:
    """The npm and cspell runs find the chosen Node first on the PATH, even with no PATH at all."""
    node = tmp_path / "node22" / "node.exe"
    assert sc.node_environment(node, {"PATH": "C:/bin", "X": "1"}) == {
        "PATH": f"{node.parent}{os.pathsep}C:/bin", "X": "1",
    }
    assert sc.node_environment(node, {}) == {"PATH": str(node.parent)}


def test_ensure_cspell_installs_the_pinned_version_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An existing install is reused; a missing one goes through Node's own npm, Node first on the PATH."""
    monkeypatch.setattr(sc, "CSPELL_ROOT", tmp_path)
    node = tmp_path / "node22" / "node.exe"
    home = tmp_path / "cspell_9.8.0"
    env = {"PATH": str(node.parent)}
    calls: list[tuple[list[str], object]] = []

    def run(command: Sequence[str], **options: object) -> subprocess.CompletedProcess[str]:
        calls.append((list(command), options["env"]))
        entry = home / "node_modules" / "cspell" / "bin.mjs"
        entry.parent.mkdir(parents=True)
        entry.write_text("", encoding="utf-8")
        return _done(command)

    entry = sc.ensure_cspell(node, "9.8.0", env, run)
    assert entry == home / "node_modules" / "cspell" / "bin.mjs"
    assert calls == [([
        str(node), str(tmp_path / "node22" / "node_modules" / "npm" / "bin" / "npm-cli.js"), "install",
        "--prefix", str(home), "--no-save", "--no-audit", "--no-fund", "cspell@9.8.0",
    ], env)]
    assert sc.ensure_cspell(node, "9.8.0", env, run) == entry
    assert len(calls) == 1

    def fail(command: Sequence[str], **_: object) -> subprocess.CompletedProcess[str]:
        return _done(command, 1, stderr="E404\n")

    with pytest.raises(sc.SpellCheckError, match=r"npm could not install cspell 10\.4\.1 .*: E404"):
        sc.ensure_cspell(node, "10.4.1", env, fail)


@pytest.mark.parametrize(
    ("code", "stdout", "expected"),
    [(2, "", "cspell failed with exit code 2: boom"), (1, "not json", "no JSON report"), (0, "[]", "not an object")],
)
def test_run_cspell_rejects_failures_and_unusable_reports(
    tmp_path: Path, code: int, stdout: str, expected: str,
) -> None:
    """Exit codes 0 and 1 carry a report; anything else is an operational error."""
    def run(command: Sequence[str], **_: object) -> subprocess.CompletedProcess[str]:
        return _done(command, code, stdout, "boom\n")

    with pytest.raises(sc.SpellCheckError, match=expected):
        sc.run_cspell(["cspell"], tmp_path, {}, run)


def test_lint_command_uses_the_json_reporter_with_suggestions(tmp_path: Path) -> None:
    """The call names the root, the merged config and every file."""
    command = sc.lint_command(tmp_path / "node.exe", tmp_path / "bin.mjs", tmp_path, tmp_path / "c.json", ["a.md"])
    assert command[2:7] == ["lint", "--root", str(tmp_path), "--config", str(tmp_path / "c.json")]
    assert "--show-suggestions" in command
    assert command[-3:] == ["--reporter", "@cspell/cspell-json-reporter", "a.md"]


def test_word_key_sorts_like_the_settings_list() -> None:
    """Accents and case are ignored, and a lowercase word comes before its capitalized twin."""
    words = ["reprcrash", "Rescope", "répositories", "rescope", "repointed", "CLAUDECODE", "codepage"]
    assert sorted(words, key=sc.word_key) == [
        "CLAUDECODE", "codepage", "repointed", "répositories", "reprcrash", "rescope", "Rescope",
    ]


def test_unknown_words_group_locations_and_suggestions(tmp_path: Path) -> None:
    """Each word appears once with all its locations and at most five suggestions, preferred first."""
    report = json.loads(_report_for(tmp_path))
    report["issues"].append({"text": "outside", "row": 1, "col": 1, "uri": "C:/elsewhere/x.md"})

    words = sc.unknown_words(report, tmp_path)

    assert words == [
        sc.UnknownWord("collectreport", ("docs/review.md:938:12", "docs/review.md:1216:30"), ("collecteront",)),
        sc.UnknownWord("gcba", ("docs/review.md:3:13",),
                       ("receive", "relieve", "received", "receiver", "receives")),
        sc.UnknownWord("outside", ("C:/elsewhere/x.md:1:1",), ()),
    ]
    assert sc.unknown_words({}, tmp_path) == []


def test_renderers_show_a_table_or_a_clean_verdict() -> None:
    """The Markdown table lists every word; JSON keeps the same data."""
    words = [sc.UnknownWord("addfinalizer", ("a.md:1:2", "a.md:3:4"), ())]
    assert sc.render_markdown([]) == "cSpell: no unknown word."
    assert sc.render_markdown(words).splitlines() == [
        "cSpell: 1 unknown word(s).",
        "",
        "| Word | Where | cSpell suggestions |",
        "| --- | --- | --- |",
        "| `addfinalizer` | `a.md:1:2`, `a.md:3:4` | none |",
    ]
    assert json.loads(sc.render_json(words)) == [
        {"word": "addfinalizer", "locations": ["a.md:1:2", "a.md:3:4"], "suggestions": []},
    ]


def test_check_runs_cspell_with_the_merged_settings_and_removes_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The whole check: Node found, cspell reused, merged config passed, then deleted."""
    environ = _user_dirs(tmp_path)
    home = tmp_path / "cspell_10.4.1"
    (home / "node_modules" / "cspell").mkdir(parents=True)
    (home / "node_modules" / "cspell" / "bin.mjs").write_text("", encoding="utf-8")
    monkeypatch.setattr(sc, "CSPELL_ROOT", tmp_path)
    root = tmp_path / "repo"
    (root / ".vscode").mkdir(parents=True)
    (root / ".vscode" / "settings.json").write_text('{"cSpell.words": ["ghog"]}', encoding="utf-8")
    seen: dict[str, Any] = {}

    def run(command: Sequence[str], **options: object) -> subprocess.CompletedProcess[str]:
        if command[1:] == ["--version"]:
            return _done(command, 0, "v22.23.4")
        config = command[command.index("--config") + 1]
        seen["config_path"] = config
        with open(config, encoding="utf-8") as stream:  # noqa: PTH123 - the path is a command argument
            seen["config"] = json.load(stream)
        seen["cwd"] = options["cwd"]
        seen["path"] = cast("dict[str, str]", options["env"])["PATH"]
        seen["files"] = command[-1]
        return _done(command, 1, _report_for(root))

    words = sc.check(root, ["docs/review.md", "tools/new.py"], environ=environ, run=run)

    assert [entry.word for entry in words] == ["collectreport", "gcba"]
    assert seen["config"]["words"] == ["ghog"]
    assert seen["config"]["userWords"] == ["Aaaah"]
    assert seen["cwd"] == root
    assert seen["files"] == "docs/review.md"
    assert seen["path"] == str(tmp_path / "prgs" / "nodes" / "node22")
    assert not (tmp_path / seen["config_path"]).exists()


def test_check_reads_markdown_only_and_needs_nothing_without_it(tmp_path: Path) -> None:
    """Source files are dropped; with no Markdown file left, no Node, npm or cspell runs."""
    assert sc.markdown_files(["a.md", "tools/x.py", "README.MD", "bin/x.bat"]) == ["a.md", "README.MD"]

    def run(command: Sequence[str], **_: object) -> subprocess.CompletedProcess[str]:
        pytest.fail(f"unexpected process {command}")

    assert sc.check(tmp_path, ["tools/x.py", "bin/x.bat"], environ={}, run=run) == []


def test_add_words_inserts_in_order_and_keeps_the_layout(tmp_path: Path) -> None:
    """New words land at their sorted place; indentation, CRLF and other keys stay."""
    settings = tmp_path / ".vscode" / "settings.json"
    settings.parent.mkdir()
    original = '{\r\n  "peacock.color": "#b8b5d9",\r\n  "cSpell.words": [\r\n    "analysing",\r\n    "codepage",\r\n    "rescope"\r\n  ]\r\n}\r\n'
    settings.write_bytes(original.encode("utf-8"))

    added = sc.add_words(settings, ["collectreport", "codepage", "Rescope", "addfinalizer", "zzz"])

    assert added == ["collectreport", "Rescope", "addfinalizer", "zzz"]
    assert settings.read_bytes().decode("utf-8") == (
        '{\r\n  "peacock.color": "#b8b5d9",\r\n  "cSpell.words": [\r\n    "addfinalizer",\r\n'
        '    "analysing",\r\n    "codepage",\r\n    "collectreport",\r\n    "rescope",\r\n'
        '    "Rescope",\r\n    "zzz"\r\n  ]\r\n}\r\n'
    )
    assert sc.add_words(settings, ["zzz"]) == []


def test_add_words_creates_the_list_or_the_file_when_missing(tmp_path: Path) -> None:
    """A settings file without the key gets it last; a missing file is created."""
    with_keys = tmp_path / "a" / "settings.json"
    with_keys.parent.mkdir()
    with_keys.write_text('{\n  "peacock.color": "#fff"\n}\n', encoding="utf-8")
    assert sc.add_words(with_keys, ["Implé"]) == ["Implé"]
    assert sc.load_jsonc(with_keys.read_text(encoding="utf-8")) == {"peacock.color": "#fff", "cSpell.words": ["Implé"]}
    assert "Implé" in with_keys.read_text(encoding="utf-8")

    empty_words = tmp_path / "c" / "settings.json"
    empty_words.parent.mkdir()
    empty_words.write_text('{\n  "cSpell.words": []\n}\n', encoding="utf-8")
    assert sc.add_words(empty_words, ["ghog"]) == ["ghog"]
    assert empty_words.read_text(encoding="utf-8") == '{\n  "cSpell.words": [\n    "ghog"\n  ]\n}\n'

    missing = tmp_path / "b" / ".vscode" / "settings.json"
    assert sc.add_words(missing, ["ghog"]) == ["ghog"]
    assert missing.read_text(encoding="utf-8") == '{\n  "cSpell.words": [\n    "ghog"\n  ]\n}\n'


def test_add_words_refuses_empty_words_and_broken_settings(tmp_path: Path) -> None:
    """An empty word or an unreadable file changes nothing."""
    settings = tmp_path / "settings.json"
    with pytest.raises(sc.SpellCheckError, match="non-empty words"):
        sc.add_words(settings, ["ok", " "])
    settings.write_text("{oops", encoding="utf-8")
    with pytest.raises(sc.SpellCheckError, match="unreadable VS Code settings"):
        sc.add_words(settings, ["ghog"])
    assert settings.read_text(encoding="utf-8") == "{oops"


def test_main_reports_words_clean_runs_and_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Exit 1 lists words, 0 means clean, 2 reports an operational error on stderr."""
    reports = [[sc.UnknownWord("ghog", ("a.md:1:1",), ())], []]

    def fake_check(root: Path, files: Sequence[str], **_: object) -> list[sc.UnknownWord]:
        assert root == tmp_path.resolve()
        assert list(files) == ["a.md"]
        if not reports:
            message = "cspell 10.4.1 needs Node 22.18 or later"
            raise sc.SpellCheckError(message)
        return reports.pop(0)

    monkeypatch.setattr(sc, "check", fake_check)
    arguments = ["check", "--root", str(tmp_path), "a.md"]

    assert sc.main(arguments, environ={}) == sc.EXIT_WORDS
    assert "| `ghog` | `a.md:1:1` | none |" in capsys.readouterr().out
    assert sc.main([*arguments[:3], "--format", "json", "a.md"], environ={}) == sc.EXIT_CLEAN
    assert json.loads(capsys.readouterr().out) == []
    assert sc.main(arguments) == sc.EXIT_ERROR
    assert capsys.readouterr().err == "spellcheck: cspell 10.4.1 needs Node 22.18 or later\n"


def test_main_add_words_and_script_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """The add-words command reports what it added; the real guard exits with main's status."""
    assert sc.main(["add-words", "--root", str(tmp_path), "ghog"]) == 0
    assert capsys.readouterr().out == "cSpell words added: ghog\n"
    monkeypatch.setattr(sys, "argv", ["spell_check.py", "add-words", "--root", str(tmp_path), "ghog"])

    with pytest.raises(SystemExit) as raised:
        run_main(sc)

    assert raised.value.code == 0
    assert capsys.readouterr().out == "cSpell words added: none (already listed)\n"


# eof
