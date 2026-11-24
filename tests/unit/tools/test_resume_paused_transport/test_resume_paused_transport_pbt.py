"""Property tests of the selector wildcard and the inert command argument.

Step 6 of v0.15.0 resume-paused: whatever plain live name a pane carries, its
selector has no space and resolves to that pane alone; a name holding another
glob character never gets a selector; and any command text, shell
metacharacters included, is the single last argument after ``--``. Each word
is drawn as one integer mapped onto every word of the alphabet up to its
length limit (bijective numeration), cheaper than one draw per character;
``test_word_mapping_edges`` pins the mapping.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.resume_paused_input import PaneRecord
from tools.resume_paused_transport import (
    ask_arguments,
    resolve_selector,
    selector_value,
)

EXAMPLES = 40
PLAIN = tuple("abcXYZ019 -_.|/:@#()&;'\"%!^$<>éü中")
GLOBS = tuple("*?[]\\")
TARGET = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
NAME_LIMIT = 24
COMMAND_LIMIT = 40


def word(number: int, alphabet: tuple[str, ...]) -> str:
    """Map one integer onto one word: 0 is empty, then every word in length order."""
    letters: list[str] = []
    while number:
        number, digit = divmod(number - 1, len(alphabet))
        letters.append(alphabet[digit])
    return "".join(letters)


def words(alphabet: tuple[str, ...], limit: int, *, empty: bool = False) -> st.SearchStrategy[str]:
    """Draw every word of the alphabet up to the length limit, through one integer."""
    last = sum(len(alphabet) ** length for length in range(1, limit + 1))
    return st.integers(0 if empty else 1, last).map(lambda number: word(number, alphabet))


plain_names = words(PLAIN, NAME_LIMIT)
glob_names = st.tuples(plain_names, st.sampled_from(GLOBS), plain_names).map("".join)


def test_word_mapping_edges() -> None:
    """Zero is empty, the alphabet comes first, then two letters, up to the longest last word."""
    base = len(PLAIN)
    last = sum(base**length for length in range(1, NAME_LIMIT + 1))
    assert (word(0, PLAIN), word(1, PLAIN), word(base, PLAIN)) == ("", PLAIN[0], PLAIN[-1])
    assert word(base + 1, PLAIN) == PLAIN[0] * 2
    assert word(last, PLAIN) == PLAIN[-1] * NAME_LIMIT


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(session=plain_names, name=plain_names)
def test_a_plain_name_always_resolves_to_its_own_pane(session: str, name: str) -> None:
    """The wildcard selector of a plain name has no space and matches its pane."""
    target = PaneRecord(TARGET, session, name, "C:\\work\\api", "claude-code", (), None)

    selector = resolve_selector((target,), target).selector

    assert selector == f"session:{selector_value(session)} name:{selector_value(name)}"
    assert selector is not None
    assert selector.count(" ") == 1


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(name=glob_names)
def test_a_name_with_another_glob_character_never_gets_a_selector(name: str) -> None:
    """No exact glob exists, so no selector is offered."""
    assert selector_value(name) is None


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(command=words(PLAIN + GLOBS, COMMAND_LIMIT, empty=True))
def test_any_command_is_the_single_last_argument(command: str) -> None:
    """Shell metacharacters stay inert: the command is one argument after ``--``."""
    arguments = ask_arguments("session:S name:N", command)

    assert arguments[-2:] == ("--", command)
    assert arguments.index("--") == len(arguments) - 2


# eof
