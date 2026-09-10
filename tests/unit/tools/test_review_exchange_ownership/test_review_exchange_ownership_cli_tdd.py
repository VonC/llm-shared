"""CLI boundary tests for paired Step 3 ownership capability flags."""

# ruff: noqa: S105

from __future__ import annotations

import argparse

import pytest

from tools.review_exchange_cli_ownership import (
    add_ownership_arguments,
    capability_from_args,
    failure_payload,
)
from tools.review_exchange_ownership import OwnershipCapability, OwnershipFailure

_TOKEN = "sensitive-token-value-0123456789abcd"


def _parser() -> argparse.ArgumentParser:
    """Build the focused parser used by capability tests."""
    parser = argparse.ArgumentParser()
    add_ownership_arguments(parser)
    return parser


def test_generation_and_token_are_one_optional_pair() -> None:
    """Both flags are absent or both produce one typed capability."""
    assert capability_from_args(_parser().parse_args([])) is None
    args = _parser().parse_args(
        ["--ownership-generation", "3", "--ownership-token", _TOKEN],
    )
    assert capability_from_args(args) == OwnershipCapability(3, _TOKEN)

    with pytest.raises(ValueError, match="must be supplied together"):
        capability_from_args(
            _parser().parse_args(["--ownership-generation", "3"]),
        )


@pytest.mark.parametrize(
    "arguments",
    [
        ["--ownership-generation", "0", "--ownership-token", _TOKEN],
        ["--ownership-generation", "x", "--ownership-token", _TOKEN],
        ["--ownership-generation", "1", "--ownership-token", ""],
        ["--ownership-generation", "1", "--ownership-token", "short"],
    ],
)
def test_malformed_capability_values_fail_without_echoing_secret(
    arguments: list[str],
) -> None:
    """Parser diagnostics reject malformed values without containing a token."""
    with pytest.raises((ValueError, SystemExit)) as raised:
        capability_from_args(_parser().parse_args(arguments))
    assert _TOKEN not in str(raised.value)


def test_duplicate_capability_flags_are_rejected() -> None:
    """A command cannot hide one ownership value behind a later duplicate."""
    with pytest.raises(SystemExit):
        _parser().parse_args(
            [
                "--ownership-generation",
                "1",
                "--ownership-generation",
                "2",
                "--ownership-token",
                _TOKEN,
            ],
        )


def test_failure_payload_is_typed_and_never_contains_plaintext_token() -> None:
    """Ownership rejection exposes current generation but no secret material."""
    failure = OwnershipFailure(
        "ownership-superseded",
        "ownership capability was superseded",
        7,
    )

    payload = failure_payload(failure)

    assert payload == {
        "current_ownership_generation": 7,
        "diagnostic": "ownership capability was superseded",
        "outcome": "ownership-superseded",
    }
    assert _TOKEN not in str(payload)


# eof
