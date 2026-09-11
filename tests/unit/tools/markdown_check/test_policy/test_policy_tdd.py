"""TDD contracts for strict repository Markdown policy loading."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tools.markdown_check.policy import PolicyError, load_policy

if TYPE_CHECKING:
    from pathlib import Path


def test_policy_loads_disabled_md013_and_md033_allowance(tmp_path: Path) -> None:
    """The current supported configuration produces one effective policy."""
    path = tmp_path / ".markdownlint.json"
    path.write_text(
        json.dumps({"MD013": False, "MD033": {"allowed_elements": ["img"]}}),
        encoding="utf-8",
    )

    policy = load_policy(path)

    assert "MD013" not in policy.enabled_rules
    assert {"MD012", "MD024", "MD025", "MD050"} <= policy.enabled_rules
    assert policy.allowed_html == frozenset({"img"})


@pytest.mark.parametrize("rule", ["MD012", "MD024", "MD025"])
def test_policy_rejects_mandatory_rule_disables(tmp_path: Path, rule: str) -> None:
    """Mandatory blank-run, duplicate and title rules cannot be disabled."""
    path = tmp_path / ".markdownlint.json"
    path.write_text(json.dumps({rule: False, "MD013": False}), encoding="utf-8")

    with pytest.raises(PolicyError, match="mandatory"):
        load_policy(path)


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"UNKNOWN": False},
        {"MD013": True},
        {"MD001": {"enabled": True}},
        {"MD033": []},
        {"MD033": {"allowed_elements": "img"}},
        {"MD033": {"allowed_elements": [1]}},
        {"MD033": {"allowed_elements": ["img", "IMG"]}},
        {"MD033": {"allowed_elements": [], "extra": True}},
    ],
)
def test_policy_rejects_unknown_keys_and_invalid_shapes(
    tmp_path: Path,
    payload: object,
) -> None:
    """Unsupported keys and option shapes fail before inventory evaluation."""
    path = tmp_path / ".markdownlint.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PolicyError):
        load_policy(path)


def test_policy_accepts_explicit_supported_enable_and_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    """Supported booleans enable rules while unreadable JSON fails closed."""
    path = tmp_path / ".markdownlint.json"
    path.write_text(json.dumps({"MD001": True}), encoding="utf-8")
    assert "MD001" in load_policy(path).enabled_rules

    path.write_text("{", encoding="utf-8")
    with pytest.raises(PolicyError, match="invalid Markdown policy"):
        load_policy(path)


# eof
