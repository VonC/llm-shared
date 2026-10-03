"""Folder reduction retains all sources without retaining nested roots."""

from pathlib import PurePosixPath

from hypothesis import given
from hypothesis import strategies as st

from tools.groundhog.group_coverage import cov_folders


@given(st.lists(st.lists(st.sampled_from(("a", "b", "c")), min_size=1, max_size=5), max_size=30))
def test_minimal_folders(parts: list[list[str]]) -> None:
    """Every source is covered and no selected folder lies inside another."""
    sources = ["/".join([*path, "module.py"]) for path in parts]
    folders = cov_folders(sources)
    assert all(any(PurePosixPath(source).is_relative_to(folder) for folder in folders) for source in sources)
    assert all(not PurePosixPath(a).is_relative_to(b) for a in folders for b in folders if a != b)
