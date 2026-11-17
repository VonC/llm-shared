"""Prove the download budget override: defaults, exact values and refused forms.

Step 1 of v0.14.0 git-cliff-provisioning (design Q18): unset, the download
budget D is 300 s and the caller's wait W is D + 60 s; a set value is an ASCII
decimal integer from 300 through 3600, never clamped nor replaced by the
default; the socket, probe, metadata and retry delay budgets stay fixed. The
lookup ignores case, as Windows variable names do.
"""

from __future__ import annotations

import pytest

from tools.release_workflow.git_cliff.budget import (
    DOWNLOAD_BUDGET_VARIABLE,
    BudgetPolicy,
    BudgetSettingError,
    resolve_budget,
)

INVALID_INPUT = 2
_SOCKET, _PROBE, _METADATA, _RETRY_DELAY = 30, 15, 60, 5
_DEFAULT_DOWNLOAD, _DEFAULT_WAIT = 300, 360


def test_unset_gives_the_default_budgets() -> None:
    """Without the variable, D is 300 s, W is 360 s and the fixed budgets apply."""
    policy = resolve_budget({"PATH": r"C:\Windows"})
    assert (policy.download, policy.wait) == (_DEFAULT_DOWNLOAD, _DEFAULT_WAIT)
    assert (policy.socket, policy.probe, policy.metadata, policy.retry_delay) == (_SOCKET, _PROBE, _METADATA, _RETRY_DELAY)
    assert policy.source == "default"


@pytest.mark.parametrize(("raw", "download"), [("300", 300), ("900", 900), ("3600", 3600), ("0900", 900)])
def test_a_value_in_range_sets_the_exact_download_and_wait(raw: str, download: int) -> None:
    """Every accepted value gives exactly D and D + 60, with the fixed budgets unchanged."""
    policy = resolve_budget({DOWNLOAD_BUDGET_VARIABLE: raw})
    expected = BudgetPolicy(download=download, wait=download + 60, source=f"{DOWNLOAD_BUDGET_VARIABLE}={raw}")
    assert policy == expected
    assert (policy.socket, policy.probe, policy.metadata, policy.retry_delay) == (_SOCKET, _PROBE, _METADATA, _RETRY_DELAY)


@pytest.mark.parametrize("raw", ["", "-1", "+600", "300.5", "600s", " 600", "600 ", "299", "3601", "\u0663\u0660\u0660", "\u00b3\u2070\u2070", "0" * 5000 + "1"])
def test_every_other_form_is_refused_without_clamping(raw: str) -> None:
    """Empty, signed, fractional, unit, padded, out-of-range and non-ASCII digits are refused."""
    with pytest.raises(BudgetSettingError) as caught:
        resolve_budget({DOWNLOAD_BUDGET_VARIABLE: raw})
    assert DOWNLOAD_BUDGET_VARIABLE in str(caught.value)
    assert "from 300 through 3600" in str(caught.value)
    assert caught.value.exit_code == INVALID_INPUT


@pytest.mark.parametrize("name", [DOWNLOAD_BUDGET_VARIABLE.lower(), "Llm_Shared_Git_Cliff_Download_Timeout_Seconds"])
def test_the_lookup_ignores_case(name: str) -> None:
    """A Windows environment name matches whatever its case; messages use the canonical name."""
    expected_download = 1200
    policy = resolve_budget({name: "1200"})
    assert policy.download == expected_download
    assert policy.source == f"{DOWNLOAD_BUDGET_VARIABLE}=1200"
    with pytest.raises(BudgetSettingError, match=DOWNLOAD_BUDGET_VARIABLE):
        resolve_budget({name: "60"})


def test_similar_names_are_not_the_override() -> None:
    """Only the exact variable name, ignoring case, sets the budget."""
    environment = {DOWNLOAD_BUDGET_VARIABLE + "_X": "900", "GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS": "900"}
    assert resolve_budget(environment).download == _DEFAULT_DOWNLOAD


# eof
