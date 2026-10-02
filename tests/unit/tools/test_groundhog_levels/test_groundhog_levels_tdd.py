"""Unit tests for the groundhog full-suite levels (v0.13.0 full_suite_levels).

Step 1: the level order and tokens, the resolution precedence (``--full``
over ``GHOG_FULL`` over the command default), a valid parameter overriding an
invalid variable without reading it, ``none`` and unknown values rejected
from both sources with the accepted values named, an empty variable read as
absent, the command defaults, the selector that never spells
``--full=none``, and the ``unproven`` proof token.
"""

from __future__ import annotations

import pytest

from tools.groundhog import levels, runner
from tools.groundhog.levels import FullLevel, LevelError, LevelSource, ResolvedLevel
from tools.groundhog.models import GroundhogError

_ACCEPTED_TEXT = "accepted values: pass, cov, speed"


class _Environ:
    """A recording environment lookup holding one optional GHOG_FULL value."""

    def __init__(self, value: str | None) -> None:
        """Hold the value returned for GHOG_FULL.

        Args:
            value: The variable value, ``None`` when unset.
        """
        self._value = value
        self.reads: list[str] = []

    def __call__(self, name: str) -> str | None:
        """Record the lookup and return the held value for GHOG_FULL.

        Args:
            name: The variable name.

        Returns:
            The held value for ``GHOG_FULL``, ``None`` for any other name.
        """
        self.reads.append(name)
        return self._value if name == levels.GHOG_FULL_ENV else None


def test_levels_are_ordered_by_the_proof_they_establish() -> None:
    """Levels order none < pass < cov < speed, each with its lowercase token."""
    assert FullLevel.NONE < FullLevel.PASS < FullLevel.COV < FullLevel.SPEED
    assert [level.token for level in FullLevel] == ["none", "pass", "cov", "speed"]
    assert levels.ACCEPTED_LEVELS == (FullLevel.PASS, FullLevel.COV, FullLevel.SPEED)


def test_parameter_wins_and_the_variable_is_not_read() -> None:
    """An explicit --full wins; GHOG_FULL is then never read."""
    environ = _Environ("speed")
    resolved = levels.resolve_level(runner.SUB_DAY, "cov", environ)
    assert resolved == ResolvedLevel(FullLevel.COV, LevelSource.PARAM)
    assert environ.reads == []


def test_valid_parameter_overrides_an_invalid_variable() -> None:
    """A valid --full resolves even when GHOG_FULL holds garbage."""
    resolved = levels.resolve_level(runner.SUB_FULL, "pass", _Environ("fast"))
    assert resolved == ResolvedLevel(FullLevel.PASS, LevelSource.PARAM)


def test_variable_wins_over_the_default() -> None:
    """A non-empty GHOG_FULL is read when no parameter is given."""
    environ = _Environ("cov")
    resolved = levels.resolve_level(runner.SUB_DAY, None, environ)
    assert resolved == ResolvedLevel(FullLevel.COV, LevelSource.ENV)
    assert environ.reads == [levels.GHOG_FULL_ENV]


@pytest.mark.parametrize("value", [None, ""])
def test_absent_or_empty_variable_falls_back_to_the_default(value: str | None) -> None:
    """An unset or empty GHOG_FULL reads as absent: the command default."""
    day = levels.resolve_level(runner.SUB_DAY, None, _Environ(value))
    full = levels.resolve_level(runner.SUB_FULL, None, _Environ(value))
    assert day == ResolvedLevel(FullLevel.NONE, LevelSource.DEFAULT)
    assert full == ResolvedLevel(FullLevel.SPEED, LevelSource.DEFAULT)


@pytest.mark.parametrize("value", ["none", "fast", "COV", " cov", ""])
def test_rejected_parameter_names_the_value_and_the_choices(value: str) -> None:
    """Rejected --full values (none, unknown, miscased, empty) are setup errors."""
    with pytest.raises(LevelError) as raised:
        levels.resolve_level(runner.SUB_DAY, value, _Environ(None))
    error = raised.value
    assert isinstance(error, GroundhogError)
    assert error.value == value
    assert error.origin == "--full"
    assert str(error) == f"invalid full level '{value}' from --full; {_ACCEPTED_TEXT}"


@pytest.mark.parametrize("value", ["none", "fast", "unproven"])
def test_rejected_variable_names_the_variable(value: str) -> None:
    """Rejected GHOG_FULL values (none, unknown) are setup errors naming it."""
    with pytest.raises(LevelError) as raised:
        levels.resolve_level(runner.SUB_FULL, None, _Environ(value))
    assert raised.value.origin == levels.GHOG_FULL_ENV
    assert str(raised.value) == f"invalid full level '{value}' from GHOG_FULL; {_ACCEPTED_TEXT}"


@pytest.mark.parametrize(
    ("sub", "expected"),
    [
        (runner.SUB_FULL, FullLevel.SPEED),
        (runner.SUB_DAY, FullLevel.NONE),
        (runner.SUB_CHECK, FullLevel.NONE),
        (runner.SUB_AFFECTED, FullLevel.NONE),
        (runner.SUB_SINGLE, FullLevel.NONE),
    ],
)
def test_command_default_is_speed_for_full_only(sub: str, expected: FullLevel) -> None:
    """The ghog full command defaults to speed; every other command to none."""
    assert levels.command_default(sub) is expected


def test_effective_level_reads_none_as_the_command_default() -> None:
    """A directly built invocation (level None) runs at the command default."""
    assert levels.effective_level(None, runner.SUB_FULL) is FullLevel.SPEED
    assert levels.effective_level(None, runner.SUB_SINGLE) is FullLevel.NONE
    assert levels.effective_level(FullLevel.COV, runner.SUB_FULL) is FullLevel.COV


def test_selector_never_spells_full_none() -> None:
    """The selector is empty at none and --full=<token> above it."""
    assert levels.level_selector(FullLevel.NONE) == ""
    assert levels.level_selector(FullLevel.PASS) == "--full=pass"
    assert levels.level_selector(FullLevel.COV) == "--full=cov"
    assert levels.level_selector(FullLevel.SPEED) == "--full=speed"
    assert all("none" not in levels.level_selector(level) for level in FullLevel)


def test_proof_token_renders_an_absent_proof_as_unproven() -> None:
    """proof= is the level token, or unproven when no proof holds."""
    assert levels.proof_token(None) == "unproven"
    assert levels.proof_token(FullLevel.NONE) == "none"
    assert levels.proof_token(FullLevel.SPEED) == "speed"


def test_level_from_token_reads_every_saved_level_back() -> None:
    """Saved tokens map back, none included; anything else is no level."""
    assert [levels.level_from_token(level.token) for level in FullLevel] == list(FullLevel)
    assert levels.level_from_token("unproven") is None
    assert levels.level_from_token("") is None


# eof
