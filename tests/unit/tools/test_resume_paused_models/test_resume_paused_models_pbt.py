"""Generated Windows root spellings share one canonical key.

Step 2 of v0.14.0 resume-paused: separator choice, repeated separators, letter
case, a trailing separator and the extended-length prefix are aliases of one
checkout root, and the canonical display parses back to itself.
"""

from __future__ import annotations

import string

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.resume_paused_models import CanonicalRoot

EXAMPLES = 5
SEGMENT = st.text(alphabet=string.ascii_letters + string.digits + "_-", min_size=1, max_size=8)


@settings(max_examples=EXAMPLES)
@given(st.lists(SEGMENT, min_size=1, max_size=4), st.data())
def test_root_spellings_share_one_canonical_key(segments: list[str], data: st.DataObject) -> None:
    """Separators, case, a trailing separator and the extended prefix are aliases."""
    canonical = CanonicalRoot.parse("C:\\" + "\\".join(segments))
    separators = data.draw(st.lists(st.sampled_from(["\\", "/", "\\\\", "/\\"]), min_size=len(segments), max_size=len(segments)))
    spelled = "".join(separator + segment for separator, segment in zip(separators, segments, strict=True))
    flips = data.draw(st.lists(st.booleans(), min_size=len(spelled), max_size=len(spelled)))
    spelled = "".join(character.swapcase() if flip else character for character, flip in zip(spelled, flips, strict=True))
    prefix = data.draw(st.sampled_from(["C:", "c:", "\\\\?\\C:", "//?/c:"]))
    alias = CanonicalRoot.parse(prefix + spelled + data.draw(st.sampled_from(["", "\\", "/"])))
    assert alias == canonical
    assert CanonicalRoot.parse(alias.display).display == alias.display


# eof
