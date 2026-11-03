"""Closed marker grammar supports only the approved operands and operators."""

from __future__ import annotations

import pytest

from tests.unit.tools.release_workflow.test_support import ENV
from tools.release_workflow.markers import evaluate, satisfies


@pytest.mark.parametrize(("marker", "expected"), [
    ("os_name == 'nt' and python_version >= '3.13.0'", True),
    ("'win' in sys_platform or os_name == 'posix'", True),
    ("(os_name != 'nt' or python_full_version < '3.14')", True),
    ("platform_machine not in 'ARM64 x86'", True),
    ("python_version > '3.13.0'", False),
    ("platform_system <= 'Windows' and implementation_name >= 'cpython'", True),
])
def test_marker_grammar(marker: str, *, expected: bool) -> None:
    """Support the closed boolean, comparison and membership language."""
    assert evaluate(marker, ENV) is expected


@pytest.mark.parametrize("marker", [
    "extra == 'x'", "os_name ==", "python_version ~= '3.13'",
    "python_version == '3.13rc1'", "os_name == 'nt' or unknown == 'x'",
    "os_name == 'nt' garbage", "(os_name == 'nt'", "__import__('os')",
])
def test_unsupported_markers(marker: str) -> None:
    """Even inactive branches must be parsed and validated without eval."""
    with pytest.raises(ValueError, match=r"marker|Marker|version"):
        evaluate(marker, ENV)


@pytest.mark.parametrize("specifier", ["~=3.13", "===3.13", "==3.*", ">=3.13rc1", "==3.13+local", ""])
def test_unsupported_specifiers(specifier: str) -> None:
    """Only the specified release-version clauses are supported."""
    with pytest.raises(ValueError, match="specifier"):
        satisfies("3.13.9", specifier)


def test_supported_specifiers() -> None:
    """Tuple padding and conjunction match the repository's requirement."""
    assert satisfies("3.13.9", ">=3.13, <3.14")
    assert satisfies("3.13", "==3.13.0, !=3.14, <=3.13, >3.12")
    assert not satisfies("3.14", ">=3.13, <3.14")


@pytest.mark.parametrize("marker", [
    "os_name not equals 'nt'", "os_name and 'nt'", "(os_name == 'nt' 'bad'",
    "'nt' == (", "os_name == 'nt' or python_version == 'bad'", "",
])
def test_more_malformed_markers(marker: str) -> None:
    """Incomplete tokens and unsupported operators fail in every branch."""
    with pytest.raises(ValueError, match=r"[Mm]arker|version"):
        evaluate(marker, ENV)


def test_marker_whitespace_and_depth() -> None:
    """Trailing whitespace is harmless; excessive nesting has a bounded error."""
    assert evaluate("os_name == 'nt'  ", ENV)
    with pytest.raises(ValueError, match="nesting"):
        evaluate("(" * 2000 + "os_name == 'nt'" + ")" * 2000, ENV)

# eof
