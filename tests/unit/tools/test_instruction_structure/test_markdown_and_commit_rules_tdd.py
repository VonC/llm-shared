"""The shared Markdown and commit rules keep bold as ``**`` and commits free of AI attribution.

Fix: an MD050 warning (``Expected: underscore; Actual: asterisk``) was allowed
to end with an agent matching the underscore style in its own lines. ``**`` is
now the bold style of every document: the warning is fixed by wrapping the bare
Python-style dunder name (such as ``__init__.py``) that set the underscore style
in backticks, and a name in lines the agent must not edit is reported at the
commit gate, the one finding that gate may show.

Fix: a host default added a ``Co-Authored-By`` trailer naming the assistant to
commit messages, and the user wants none, ever. ``rules/chat.md`` and the
grouped commit message rules now forbid any AI attribution line in commit
messages, ``a.commit`` groups and pull request descriptions.

Fix: commits reached the history with words VS Code's Code Spell Checker
underlines, because no gate looked at them outside VS Code. ``rules/spelling.md``
now runs ``spellcheck.bat check`` on every new or modified Markdown file (never
on source code) before any commit choice, and has the user settle each word (accepted into
``.vscode/settings.json`` or replaced), backticks or not; both commit gates
point to it.
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

ROOT = steps.llm_shared_dir()


def _section(text: str, heading: str) -> str:
    """Return the body of the level-two ``heading`` up to the next one."""
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


def _flat(text: str) -> str:
    """Join wrapped lines so a phrase can be found across line breaks."""
    return " ".join(text.split())


def test_md050_keeps_asterisk_bold_and_backticks_dunder_names() -> None:
    """MD050 is fixed at its cause, a bare dunder name, never by switching to ``__``."""
    rules = (ROOT / "rules/markdown.md").read_text(encoding="utf-8")
    names = _flat(_section(rules, "Code-like names and bold text"))
    for required in (
        "`**` is the bold style of every document",
        "never fixed by switching the bold to `__`",
        "`__init__.py`, `__main__` or `__name__`",
        "wrap it in backticks",
        "report the remaining warning at the commit gate",
    ):
        assert required in names
    assert "match the expected style in your own lines" not in names
    gate = _flat(_section(rules, "Lint every new or modified Markdown file before asking to commit"))
    assert "The only finding that may remain is one in a line this work must not edit" in gate


def test_commit_messages_carry_no_ai_attribution() -> None:
    """Both the general chat rule and the grouped commit rules forbid attribution lines."""
    chat = _flat((ROOT / "rules/chat.md").read_text(encoding="utf-8"))
    assert "never add an AI attribution line" in chat
    assert "no `Co-Authored-By:` trailer naming an assistant" in chat
    grouping = (ROOT / "instructions/group-commits-msg.md").read_text(encoding="utf-8")
    rules = _flat(_section(grouping, "Commit message rules for groups"))
    assert "never add a `Co-Authored-By:` trailer naming an assistant" in rules
    assert "The message ends with the `What:` list" in rules


def test_commit_gates_settle_every_spelling_finding_with_the_user() -> None:
    """Every reported word is accepted or replaced by the user's choice before any commit choice."""
    spelling = _flat((ROOT / "rules/spelling.md").read_text(encoding="utf-8"))
    for required in (
        'bin\\spellcheck.bat" check <file.md>',
        "Source code and other files are never spell-checked.",
        "inside backticks, a code block or plain text alike",
        "`Add to settings.json`, then `Replace with <suggestion>`",
        'bin\\spellcheck.bat" add-words <word>',
        "no `cSpell.ignoreRegExpList` pattern, no `cspell:ignore` or `cspell:disable` comment",
        "else cspell 9.8.0 on a Node 20.18 or later",
        "`dwl_inst_ver node 22`",
    ):
        assert required in spelling
    assert "[`spelling.md`](spelling.md)" in _flat((ROOT / "rules/chat.md").read_text(encoding="utf-8"))
    grouping = _flat((ROOT / "instructions/group-commits-msg.md").read_text(encoding="utf-8"))
    assert "spell-check the same Markdown files, and only them" in grouping
    requestor = _flat((ROOT / "instructions/code-review-requestor.md").read_text(encoding="utf-8"))
    assert "Never show `Commit` while an unknown word remains." in requestor


# eof
