"""A dummy test that backs the single-test build gate in build.bat.

build.bat (and the brel alias) deliberately does not run the whole suite: ghog,
pt and check.bat are the real test, coverage and static gates. The release
build only confirms that pytest itself runs, by executing this one test.

To get a deterministic single test under `pytest --last-failed`, build.bat
first forces this test to fail (PYTEST_DUMMY_FAIL=1) to seed the last-failed
cache, then re-runs it with the variable unset so it passes. That also
sidesteps the empty `--last-failed --lfnf=none` collection issue,
https://github.com/pytest-dev/pytest/issues/13614, by guaranteeing one test.

Set PYTEST_DUMMY_FAIL to "1" to force the failure:
  PYTEST_DUMMY_FAIL=1 pytest tests/test_dummy.py
"""

from __future__ import annotations

import os

import pytest


def test_dummy() -> None:
    """Pass by default; fail only when PYTEST_DUMMY_FAIL is set to "1"."""
    if os.getenv("PYTEST_DUMMY_FAIL") == "1":
        pytest.fail("PYTEST_DUMMY_FAIL environment variable was set to 1.")
    # If the environment variable is not set, the test passes by default.
    assert True


# eof
