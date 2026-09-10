"""Suite-wide Hypothesis defaults for a parallel test run.

The full suite runs on xdist workers, so wall-clock time inside a test now
measures contention as much as the code under test. Hypothesis enforces a
200ms per-example deadline by default and reports a ``FlakyFailure`` when one
example crosses it and a rerun does not, which is exactly what contention
produces: an example measured at 72ms alone was measured at 288ms under load.

Fix: default ``deadline`` to ``None`` for the whole suite. This removes a
wall-clock assertion that parallel scheduling makes unreliable; it does not
remove slowness detection, which belongs to the project's own duration gate in
the sequential ``ghog timings`` run. Several property suites already set
``deadline=None`` by hand for the same reason, so this makes the established
convention the default. A module that sets its own ``deadline`` still wins,
because an explicit ``@settings`` value overrides the active profile.
"""

from __future__ import annotations

from hypothesis import HealthCheck, settings

_PROFILE = "llm-shared"

settings.register_profile(
    _PROFILE,
    deadline=None,
    # Contended workers make per-example setup slow rather than wrong; the
    # duration gate, not Hypothesis, owns the verdict on how slow is too slow.
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile(_PROFILE)


# eof
