"""Run evidence of groundhog: the keys a closing and a status line carry.

v0.13.0 full_suite_levels, Step 2: every run now reports its objective, its
valid proof and what it ran or reused, in the closing line of its report and in
``a.ghog.status``. This module holds that evidence as values and renders its
keys; the executors fill it in and the reporters print it.

- A day walk carries ``full=`` (the selected objective), ``src=`` (where it
  came from), ``proof=`` (the valid proof after the walk, or ``unproven``),
  ``reused=`` (``none``, ``check+affected`` on an upgrade, ``all`` on a noop)
  and ``scope=`` (the scope it ran and proved).
- A direct ``ghog full`` carries ``full=``, ``src=``, its earned ``proof=``
  and ``scope=``.
- Any other run, and every step inside a walk, carries ``scope=`` only.

The keys are appended after the current ones, so a reader matching the
current keys by name keeps working. A running line carries ``proof=pending``
in place of a proof and no ``reused=``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Final

from tools.groundhog import runner
from tools.groundhog.levels import ResolvedLevel, effective_level, proof_token
from tools.groundhog.models import RunStats

if TYPE_CHECKING:
    from tools.groundhog.context import Invocation
    from tools.groundhog.levels import FullLevel
    from tools.groundhog.reporting import ClosingMetrics

# The proof a running line names: the walk has not judged anything yet.
PROOF_PENDING: Final = "pending"
# The commands whose own evidence names a level: the walk and the direct run.
_LEVEL_SUBS: Final = (runner.SUB_DAY, runner.SUB_FULL)


class Reused(StrEnum):
    """What a day walk took from the snapshot instead of running."""

    NONE = "none"
    CHECK_AFFECTED = "check+affected"
    ALL = "all"


@dataclass(frozen=True)
class RunEvidence:
    """The evidence of one run, rendered as appended ``key=value`` keys.

    Attributes:
        scope_key: The scope the run ran and proved, such as ``whole``.
        level: The objective and its source, ``None`` for a run that only
            carries its scope.
        proof: The valid or earned proof, ``None`` read as ``unproven``.
        reused: What a day walk reused, ``None`` for any other run.
    """

    scope_key: str
    level: ResolvedLevel | None = None
    proof: FullLevel | None = None
    reused: Reused | None = None

    def closing_keys(self) -> str:
        """Render the keys of a closing line and a done status line.

        Returns:
            ``full= src= proof=`` for a leveled run, then ``reused=`` for a
            walk, then ``scope=``.
        """
        keys = self._level_keys()
        if self.level is not None:
            keys.append(f"proof={proof_token(self.proof)}")
        if self.reused is not None:
            keys.append(f"reused={self.reused}")
        keys.append(f"scope={self.scope_key}")
        return " ".join(keys)

    def running_keys(self) -> str:
        """Render the keys of a running status line.

        Returns:
            ``full= src= scope= proof=pending`` for a leveled run, else
            ``scope=`` alone.
        """
        keys = [*self._level_keys(), f"scope={self.scope_key}"]
        if self.level is not None:
            keys.append(f"proof={PROOF_PENDING}")
        return " ".join(keys)

    def _level_keys(self) -> list[str]:
        """Render the objective and its source, when the run carries a level.

        Returns:
            ``full=<level>`` and ``src=<source>``, or nothing.
        """
        if self.level is None:
            return []
        return [f"full={self.level.level.token}", f"src={self.level.source}"]


@dataclass(frozen=True)
class RunOutcome:
    """The end of one run: its exit code, its evidence and its closing values.

    Attributes:
        code: The contract exit code.
        evidence: The evidence the closing and done lines carry.
        stats: The counters of the run's last pytest child, empty without one.
        metrics: The closing values of that child, ``None`` without one.
        judged: Whether the run judged a gate; a setup error, a project
            without a pytest suite and an interrupted child did not, so a
            walk keeps its saved proof for them.
    """

    code: int
    evidence: RunEvidence
    stats: RunStats = field(default_factory=RunStats)
    metrics: ClosingMetrics | None = None
    judged: bool = True


def for_invocation(invocation: Invocation, proof: FullLevel | None = None) -> RunEvidence:
    """Build the evidence of one run from its invocation.

    Args:
        invocation: The parsed invocation, or a step derived by the walk.
        proof: The valid or earned proof, for a leveled run.

    Returns:
        The level, proof and scope of a day walk or a direct ``ghog full``
        (``reused=none`` for the walk); the scope alone for any other run and
        for every step inside a walk.
    """
    scope_key = invocation.scope.key()
    if invocation.in_walk or invocation.sub not in _LEVEL_SUBS:
        return RunEvidence(scope_key)
    resolved = ResolvedLevel(
        effective_level(invocation.level, invocation.sub),
        invocation.level_source,
    )
    reused = Reused.NONE if invocation.sub == runner.SUB_DAY else None
    return RunEvidence(scope_key, resolved, proof, reused)


# eof
