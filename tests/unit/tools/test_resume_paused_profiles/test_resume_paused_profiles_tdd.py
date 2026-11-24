"""Profile registry, caller classification and boot-boundary policy tests.

Step 1 of v0.15.0 resume-paused: the shipped registry pins nothing, a pinned
profile needs version, OS build and digest to agree, recognized agent callers
are rejected inside and outside TUIOS, and the Q21 comparison only detects a
net backward clock movement.
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from tests.unit.tools.resume_paused_test_support import (
    CODEX_DIGEST,
    CODEX_VERSION,
    OS_BUILD,
    at,
    codex_registry,
)
from tools.resume_paused_profiles import (
    DISCLOSED_LIMITS,
    SUPPORTED_PROFILES,
    BootObservation,
    CallerOrigin,
    Host,
    HostProfile,
    ProfileRegistry,
    ReadAccount,
    Reason,
    Verdict,
    boot_boundary,
    classify_caller,
)


def test_shipped_registry_supports_no_host_version() -> None:
    """No profile passed Step 1 validation, so observed candidates stay unsupported."""
    for host, version in ((Host.CODEX, CODEX_VERSION), (Host.CLAUDE, "2.1.325")):
        decision = SUPPORTED_PROFILES.select(host, version, OS_BUILD, CODEX_DIGEST)

        assert decision.verdict is Verdict.UNSUPPORTED
        assert decision.profile is None
        assert decision.reasons == (Reason("profile-version-unpinned"),)


def test_pinned_profile_requires_version_build_and_digest() -> None:
    """Only the exact pinned combination selects a profile."""
    registry = codex_registry()

    supported = registry.select(Host.CODEX, CODEX_VERSION, OS_BUILD, CODEX_DIGEST)

    assert supported.verdict is Verdict.SUPPORTED
    assert supported.profile is not None
    assert supported.profile.evidence == "synthetic"
    assert registry.select(Host.CODEX, CODEX_VERSION, 22631, CODEX_DIGEST).reasons == (Reason("os-build-unpinned"),)
    assert registry.select(Host.CODEX, CODEX_VERSION, OS_BUILD, "b" * 64).reasons == (Reason("image-digest-mismatch"),)
    assert registry.select(Host.CODEX, CODEX_VERSION, OS_BUILD).verdict is Verdict.UNSUPPORTED


def test_registry_refuses_two_pins_for_one_host_version() -> None:
    """A second pin for the same version would make selection ambiguous."""
    profile = HostProfile(Host.CLAUDE, "2.1.325", frozenset({OS_BUILD}), "synthetic")

    with pytest.raises(ValueError, match=r"duplicate profile for claude 2\.1\.325"):
        ProfileRegistry((profile, profile))


def test_read_account_counts_each_complete_read() -> None:
    """Byte accounting adds one file and its bytes per read."""
    assert ReadAccount().plus(10).plus(5) == ReadAccount(files=2, bytes_read=15)


@pytest.mark.parametrize(
    ("environment", "ancestry", "origin", "reasons"),
    [
        ({"CLAUDECODE": "1", "TUIOS_PANE_ID": "p"}, ("cmd.exe",), CallerOrigin.AGENT, (Reason("agent-environment-marker"),)),
        ({"CODEX_THREAD_ID": "t", "CLAUDECODE": "1"}, None, CallerOrigin.AGENT, (Reason("agent-environment-marker", 2), Reason("ancestry-unavailable"))),
        ({}, ("powershell.exe", "Codex.EXE", "claude.exe"), CallerOrigin.AGENT, (Reason("agent-ancestor", 2),)),
        ({"TUIOS_PANE_ID": "p"}, ("cmd.exe", "explorer.exe"), CallerOrigin.UNPROVED, ()),
        ({"CLAUDECODE": ""}, None, CallerOrigin.UNPROVED, (Reason("ancestry-unavailable"),)),
    ],
)
def test_caller_classification(
    environment: dict[str, str], ancestry: tuple[str, ...] | None, origin: CallerOrigin, reasons: tuple[Reason, ...],
) -> None:
    """Markers or agent ancestors reject; missing ancestry never rejects a human shell."""
    decision = classify_caller(environment, ancestry)

    assert decision.origin is origin
    assert decision.reasons == reasons


def test_boot_boundary_uses_the_fixed_boot_instant() -> None:
    """A forward clock step keeps the fixed instant as the history boundary."""
    observation = BootObservation(boot_created_at=at(0), now=at(600), uptime=timedelta(seconds=300))

    decision = boot_boundary(observation, timedelta(seconds=5))

    assert decision.verdict is Verdict.SUPPORTED
    assert decision.boundary == at(0)
    assert decision.reasons == ()


def test_boot_boundary_stays_pending_on_backward_clock_movement() -> None:
    """A computed boot earlier than the fixed one beyond tolerance is pending."""
    observation = BootObservation(boot_created_at=at(100), now=at(300), uptime=timedelta(seconds=206))

    assert boot_boundary(observation, timedelta(seconds=6)).verdict is Verdict.SUPPORTED
    pending = boot_boundary(observation, timedelta(seconds=5))

    assert pending.verdict is Verdict.PENDING
    assert pending.boundary is None
    assert pending.reasons == (Reason("clock-backward-beyond-tolerance"),)


@pytest.mark.parametrize(("uptime", "tolerance"), [(-1, 5), (10, -1)])
def test_boot_boundary_rejects_invalid_evidence(uptime: int, tolerance: int) -> None:
    """Negative uptime or tolerance is invalid evidence, never a boundary."""
    observation = BootObservation(boot_created_at=at(0), now=at(60), uptime=timedelta(seconds=uptime))

    assert boot_boundary(observation, timedelta(seconds=tolerance)).reasons == (Reason("boot-evidence-invalid"),)


def test_disclosed_limits_name_the_five_residual_limits() -> None:
    """Every activation report carries the Q20, Q21, Q26 and Q27 limits."""
    assert DISCLOSED_LIMITS == (
        "detached-foreground-or-hook-work",
        "hook-configuration-history-unavailable",
        "undetectable-backward-clock-change",
        "roots-without-records",
        "running-local-command-not-yet-recorded",
    )


# eof
