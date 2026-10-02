"""Full-suite levels of groundhog: value, ordering and resolution.

v0.13.0 full_suite_levels, Step 1: the pure level model the next steps wire
into the CLI, the day walk and the full run. Nothing here reads the process
environment or the file system; the caller injects the environment lookup.

A ``FullLevel`` is ordered by the proof it establishes, ``none < pass < cov
< speed``: ``cov`` implies ``pass`` because a covered full run still requires
every test to pass, and ``speed`` implies ``cov``. ``none`` is the internal
level of the default walk, never an accepted ``--full`` or ``GHOG_FULL``
value, so no selector or restart line can ever carry a ``none`` level (its
selector is empty). The reporting value ``unproven`` (no valid proof for the
current sources) is not a level: :func:`proof_token` renders it for an absent
proof.

Resolution happens once per invocation (:func:`resolve_level`): an explicit
``--full`` wins and the environment is then not read at all, so a valid
parameter overrides an invalid variable; otherwise a non-empty ``GHOG_FULL``;
otherwise the command default, ``speed`` for ``ghog full`` and ``none`` for
every other command. Any other value, ``none`` included, raises
:class:`LevelError`, a setup error naming the accepted values.

Fix (v0.13.0 full_suite_levels, Step 2): the model no longer imports the
``runner`` process adapter for the ``full`` subcommand name. The runner now
shapes the full run by level and imports :class:`FullLevel`, so the pure model
names that subcommand itself and the dependency points one way only, from the
adapter to the model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, Final

from tools.groundhog.models import GroundhogError

if TYPE_CHECKING:
    from collections.abc import Callable

# The environment variable carrying the level of every groundhog call.
GHOG_FULL_ENV: Final = "GHOG_FULL"
# The ``ghog full`` subcommand name (``runner.SUB_FULL``), the one command
# whose default level is ``speed``; named here so the model never imports the
# process adapter.
_FULL_SUB: Final = "full"
# The origin named by a rejected parameter, as the caller typed it.
PARAM_ORIGIN: Final = "--full"
# The text rendered for an absent proof; never a level, never a selector.
UNPROVEN: Final = "unproven"


class FullLevel(IntEnum):
    """One full-suite level, ordered by the proof it establishes."""

    NONE = 0
    PASS = 1
    COV = 2
    SPEED = 3

    @property
    def token(self) -> str:
        """Return the lowercase token of the level, such as ``cov``."""
        return self.name.lower()


class LevelSource(StrEnum):
    """Where a resolved level came from."""

    PARAM = "param"
    ENV = "env"
    DEFAULT = "default"


@dataclass(frozen=True)
class ResolvedLevel:
    """A level and the source it was resolved from.

    Attributes:
        level: The resolved level.
        source: The parameter, the environment variable or the default.
    """

    level: FullLevel
    source: LevelSource


# The values a caller may select; ``none`` is internal only.
ACCEPTED_LEVELS: Final = (FullLevel.PASS, FullLevel.COV, FullLevel.SPEED)
# The accepted tokens, in level order, for parsing and for the error line.
_ACCEPTED_BY_TOKEN: Final = {level.token: level for level in ACCEPTED_LEVELS}
# Every level by token, ``none`` included, for reading a saved proof back.
_LEVEL_BY_TOKEN: Final = {level.token: level for level in FullLevel}


class LevelError(GroundhogError):
    """A rejected level value: a setup error naming the accepted values."""

    def __init__(self, value: str, origin: str) -> None:
        """Build the message naming the value, its origin and the choices.

        Args:
            value: The rejected value, exactly as received.
            origin: ``--full`` or ``GHOG_FULL``, where the value came from.
        """
        accepted = ", ".join(_ACCEPTED_BY_TOKEN)
        super().__init__(
            f"invalid full level '{value}' from {origin}; accepted values: {accepted}",
        )
        self.value = value
        self.origin = origin


def command_default(sub: str) -> FullLevel:
    """Return the level a command runs at when nothing selects one.

    Args:
        sub: The subcommand name.

    Returns:
        ``speed`` for ``full``, ``none`` for every other command.
    """
    return FullLevel.SPEED if sub == _FULL_SUB else FullLevel.NONE


def resolve_level(
    sub: str,
    param: str | None,
    environ: Callable[[str], str | None],
) -> ResolvedLevel:
    """Resolve the level of one invocation: parameter, variable, default.

    Args:
        sub: The subcommand name, for the command default.
        param: The ``--full`` value, ``None`` when the option is absent.
        environ: The environment lookup, called only without a parameter.

    Returns:
        The resolved level and its source.

    Raises:
        LevelError: When the selected value is not an accepted level.
    """
    if param is not None:
        return ResolvedLevel(_accepted(param, PARAM_ORIGIN), LevelSource.PARAM)
    value = environ(GHOG_FULL_ENV)
    if value:
        return ResolvedLevel(_accepted(value, GHOG_FULL_ENV), LevelSource.ENV)
    return ResolvedLevel(command_default(sub), LevelSource.DEFAULT)


def effective_level(level: FullLevel | None, sub: str) -> FullLevel:
    """Return the level an invocation runs at, ``None`` meaning the default.

    Args:
        level: The carried level, ``None`` for a directly built invocation.
        sub: The subcommand name, for the command default.

    Returns:
        The carried level, else the command default.
    """
    return command_default(sub) if level is None else level


def level_selector(level: FullLevel) -> str:
    """Return the ``--full`` selector a restart line carries for a level.

    Args:
        level: The level to carry.

    Returns:
        ``--full=<token>``, or an empty string at ``none``.
    """
    if level is FullLevel.NONE:
        return ""
    return f"{PARAM_ORIGIN}={level.token}"


def proof_token(level: FullLevel | None) -> str:
    """Return the ``proof=`` token of a proof level.

    Args:
        level: The valid proof, ``None`` when no proof holds.

    Returns:
        The level token, or ``unproven`` for ``None``.
    """
    return UNPROVEN if level is None else level.token


def level_from_token(token: str) -> FullLevel | None:
    """Read a saved level token back, ``none`` included.

    Args:
        token: The token, such as ``cov`` or ``none``.

    Returns:
        The level, or ``None`` for any other text (``unproven`` included).
    """
    return _LEVEL_BY_TOKEN.get(token)


def _accepted(value: str, origin: str) -> FullLevel:
    """Parse one selected value against the accepted levels.

    Args:
        value: The selected value, exactly as received.
        origin: ``--full`` or ``GHOG_FULL``, for the error line.

    Returns:
        The selected level.

    Raises:
        LevelError: When the value is not ``pass``, ``cov`` or ``speed``.
    """
    level = _ACCEPTED_BY_TOKEN.get(value)
    if level is None:
        raise LevelError(value, origin)
    return level


# eof
