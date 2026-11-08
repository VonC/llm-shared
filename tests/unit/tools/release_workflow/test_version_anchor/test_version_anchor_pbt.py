"""Anchor token replacement over generated titles, notes and line endings.

Step 2 of v0.14.0 version-sources: whatever the title, the notes, the line
ending and the byte-order mark, replacing the token span changes only the
token bytes, and the document reads back with the same title and notes.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.unit.tools.release_workflow.version_support import version_txt
from tools.release_workflow.sources import anchor
from tools.release_workflow.sources.model import compose

_PRINTABLE = st.text(alphabet=st.characters(min_codepoint=0x20, max_codepoint=0x7E), max_size=12)
_NOTE_LINES = st.lists(_PRINTABLE, max_size=4)


@settings(max_examples=25)
@given(title=_PRINTABLE, lines=_NOTE_LINES, newline=st.sampled_from(["\n", "\r\n"]), bom=st.booleans())
def test_replacement_changes_only_the_token(title: str, lines: list[str], newline: str, *, bom: bool) -> None:
    """The bytes before and after the token span are kept exactly."""
    notes = "".join(f"{line}\n" for line in lines)
    content = version_txt(f"0.13.0-SNAPSHOT -- {title}", notes, newline=newline, bom=bom)
    document = anchor.parse_document(content)
    span = document.token_span
    replaced = compose(content, [(span, b"10.2.3")])
    assert replaced == content[:span.start] + b"10.2.3" + content[span.end:]
    reread = anchor.parse_document(replaced)
    assert (str(reread.token), reread.title, reread.notes) == ("10.2.3", title.strip(), notes.replace("\n", newline))


# eof
