"""Group patterns preserve segment boundaries, directory matches and precedence."""

import pytest

from tools.groundhog.group_patterns import compile_patterns, matches


@pytest.mark.parametrize(("pattern", "path", "expected"), [
    ("tests/*.py", "tests/test_x.py", True),
    ("tests/*.py", "tests/unit/test_x.py", False),
    ("tests/?.py", "tests/a.py", True),
    ("tests/?.py", "tests/ab.py", False),
    ("tests/**/test_*.py", "tests/test_x.py", True),
    ("tests/**/test_*.py", "tests/a/b/test_x.py", True),
    ("test_*.py", "a/b/test_x.py", True),
    ("sentinel", "tests/sentinel/test_x.py", True),
    ("tools/sentinel", "tools/sentinel/a.py", True),
    ("/tools", "tools/x.py", True),
    ("/tools", "other/tools/x.py", False),
    ("tools/**", "tools/.hidden/x.py", True),
    ("**/tests/**/*sentinel*/**", "src/pkg/tests/unit/test_sentinel/test_x.py", True),
    ("**/tests/**/*sentinel*/**", "tests/test_sentinel/test_x.py", True),
    ("/tools/**", "other/tools/x.py", False),
    ("/tools/**", "tools/x.py", True),
    ("tools/", "tools/x.py", True),
])
def test_match_semantics(pattern: str, path: str, *, expected: bool) -> None:
    """Match the documented glob grammar, including hidden paths."""
    assert matches(compile_patterns([pattern]), path) is expected


def test_last_matching_pattern_wins() -> None:
    """An exclusion removes prior matches and a later inclusion restores one."""
    compiled = compile_patterns([" ", "# comment", "tests/**", "!tests/slow/**", "tests/slow/test_one.py"])
    assert not matches(compiled, "tests/slow/test_two.py")
    assert matches(compiled, "tests/slow/test_one.py")
    assert not matches(compiled, "tools/module.py")
