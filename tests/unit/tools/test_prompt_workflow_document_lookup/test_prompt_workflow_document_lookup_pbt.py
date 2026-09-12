"""Bounded filename properties for exact effort identity and separator folding.

Generate expected identities independently of the matcher; filesystem shape,
freshness and failure scenarios remain in the deterministic suite.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tools import prompt_workflow_docs as docs

_KINDS = (
    ("draft", "draft", ".md"),
    ("feature-request", "feature-request", ".md"),
    ("issue", "issue", ".md"),
    ("design", "design", ".md"),
    ("plan", "plan", ".md"),
    ("validation-plan", "plan", ".validation.md"),
)
_VERSIONS = st.tuples(*(st.integers(min_value=0, max_value=30) for _ in range(3)))
_WORDS = st.lists(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8), min_size=2, max_size=5)


@given(
    kind=st.sampled_from(_KINDS),
    version=_VERSIONS,
    words=_WORDS,
    separators=st.tuples(st.sampled_from(("-", "_")), st.sampled_from(("-", "_"))),
)
@settings(max_examples=40)
def test_exact_identity_folds_either_separator(
    kind: tuple[str, str, str], version: tuple[int, int, int],
    words: list[str], separators: tuple[str, str],
) -> None:
    """Independent spellings of the same generated word sequence always match."""
    document_type, prefix, suffix = kind
    version_name = f"v{version[0]}.{version[1]}.{version[2]}"
    filename_slug = separators[0].join(words)
    requested_slug = separators[1].join(words)
    name = f"{prefix}.{version_name}.{filename_slug}{suffix}"

    assert docs._exact_doc_matches(name, document_type, version_name, requested_slug)


@given(kind=st.sampled_from(_KINDS), version=_VERSIONS, words=_WORDS)
@settings(max_examples=40)
def test_exact_identity_rejects_different_versions_and_topics(
    kind: tuple[str, str, str], version: tuple[int, int, int], words: list[str],
) -> None:
    """Changed version, first token or added subtopic cannot qualify the identity."""
    document_type, prefix, suffix = kind
    version_name = f"v{version[0]}.{version[1]}.{version[2]}"
    other_version = f"v{version[0]}.{version[1]}.{version[2] + 1}"
    slug = "_".join(words)
    filename_slug = "-".join(words)
    different_slug = "-".join([f"x{words[0]}", *words[1:]])

    for name in (
        f"{prefix}.{other_version}.{filename_slug}{suffix}",
        f"{prefix}.{version_name}.{different_slug}{suffix}",
        f"{prefix}.{version_name}.{filename_slug}-sub{suffix}",
    ):
        assert not docs._exact_doc_matches(name, document_type, version_name, slug)


# eof
