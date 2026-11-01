"""Keep Hypothesis source discovery on its portable, cached path.

Hypothesis's site-packages shortcut uses forward slashes. On Windows, loaded
module filenames contain backslashes and otherwise cause native realpath I/O
for every third-party module on the first constant-biased example. Normalize
the spelling before the original classifier; retain its source constants,
strategies, shrinking, example counts and classification of local modules.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from hypothesis.internal import constants_ast
from hypothesis.internal.conjecture import providers

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(scope="session", autouse=True)
def portable_hypothesis_module_paths() -> Iterator[None]:
    """Normalize module separators without precomputing outside test timing."""
    classify = constants_ast.is_local_module_file

    def portable_path(path: str) -> bool:
        normalized = path.replace("\\", "/")
        # Hypothesis already excludes these exact test paths, but does so
        # after resolving them on disk. Apply its lexical exclusion first;
        # local application modules still use the original classifier.
        candidate = Path(normalized)
        if ("test" in candidate.parts or "tests" in candidate.parts
                or candidate.stem.startswith("test_") or candidate.stem.endswith("_test")):
            return False
        return classify(normalized)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(providers, "is_local_module_file", portable_path)
        yield


# eof
