"""The completeness checks refuse every gap in the evidence before any review.

Step 6 of v0.14.0 git-cliff-provisioning (design "Outputs and
classification" and "Statuses"; design decisions Q11 and Q13; plan decision
Q16); split from the bundle leaf with `bundle_checks` in code review round 2.

- A complete bundle passes; a manifest entry of the pin must name this bundle
  with the reviewed asset identity.
- Refused: a missing candidate, no range, one version for both candidates, a
  matrix without the full history, with a broken chain, a duplicate or a
  missing case, other fixture tags, a pin without upstream integrity, other
  flags or environment names, a `cliff.toml` digest other than the listed
  one, outputs that do not follow the ranges, an unclassified, unknown or
  defect hunk, an intentional entry without its reason, another kind.
- The exclusion of 69 needs the audit's revision, commands and every
  exit-path category with references and a finding, and the observed
  success, usage error and failing render with consistent statuses.
- Round 2: each observation is checked on its own, so a repeated name cannot
  hide a 69 or an inconsistent status; a case where the pin returned 69 is
  refused; llm-shared's ranges must be exactly the chain of its recorded
  tags, each tag once, with full history alone refused when tags are
  recorded.
"""

from __future__ import annotations

import dataclasses
from datetime import date
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    BASELINE,
    DIFFERING,
    DIFFERING_INDEX,
    PIN,
    SAMPLE_RANGES,
    sample_bundle,
    sample_inputs,
    sample_outputs,
)
from tests.unit.tools.release_workflow.git_cliff_support import synthetic_pin
from tools.release_workflow.git_cliff.bundle import (
    CLIFF_TOML,
    Audit,
    AuditCategory,
    BundleError,
    Classification,
    ObservedStatus,
    with_review,
)
from tools.release_workflow.git_cliff.bundle_checks import (
    AUDIT_CATEGORIES,
    OBSERVATIONS,
    require_admissible,
    require_complete,
)
from tools.release_workflow.git_cliff.comparison import (
    CaseResult,
    ComparisonResult,
    RangeCase,
    RunDigest,
    chained_ranges,
)
from tools.release_workflow.git_cliff.fixture_history import FixtureHashes

if TYPE_CHECKING:
    from tools.release_workflow.git_cliff.bundle import Bundle

_LOCATION = f"tools/release_workflow/git_cliff/bundles/{PIN}"
_DAY = date(2026, 11, 21)


def test_a_complete_bundle_passes_the_checks() -> None:
    """Every input, every hunk classified intentional, an audit excluding 69 with its evidence, no admitted pin."""
    require_complete(sample_bundle(), location=_LOCATION, pins=())


def test_an_admitted_pin_must_reference_this_bundle_with_the_reviewed_identity() -> None:
    """A manifest entry names this bundle's directory and the reviewed asset identity; another directory or digest is refused."""
    pin = synthetic_pin(PIN)
    require_complete(sample_bundle(), location=_LOCATION, pins=(pin,))
    for other in (dataclasses.replace(pin, evidence="docs/evidence"), dataclasses.replace(pin, sha256="0" * 64)):
        with pytest.raises(BundleError, match="manifest"):
            require_complete(sample_bundle(), location=_LOCATION, pins=(other,))


def _without_baseline() -> object:
    """Inputs whose candidates miss the baseline."""
    inputs = sample_inputs()
    return dataclasses.replace(inputs, candidates=inputs.candidates[1:])


def _pin_without_upstream() -> object:
    """Inputs whose pin was trusted on HTTPS alone."""
    inputs = sample_inputs()
    pin = dataclasses.replace(inputs.candidates[1], trust="evidence-only-https")
    return dataclasses.replace(inputs, candidates=(inputs.candidates[0], pin))


def _ranges(*cases: RangeCase) -> object:
    """Inputs with other ranges."""
    return dataclasses.replace(sample_inputs(), ranges=cases)


_CLASSIFIED = f"{DIFFERING.key} #1"
_FIXTURE_RANGES = tuple(case for case in SAMPLE_RANGES if case.repository == "fixture")


@pytest.mark.parametrize(("changes", "reason"), [
    pytest.param({"inputs": _without_baseline()}, "candidates", id="missing-candidate"),
    pytest.param({"inputs": dataclasses.replace(sample_inputs(), ranges=())}, "ranges", id="no-range"),
    pytest.param({"inputs": dataclasses.replace(sample_inputs(), pin=BASELINE)}, "both", id="one-version"),
    pytest.param({"inputs": _ranges(*SAMPLE_RANGES[1:])}, "full history", id="no-full-history"),
    pytest.param({"inputs": _ranges(RangeCase("llm-shared"), RangeCase("llm-shared", "v0.1.0..v0.2.0"), RangeCase("llm-shared", "v0.3.0..HEAD"),
                                    *_FIXTURE_RANGES)}, "chained", id="broken-chain"),
    pytest.param({"inputs": _ranges(*SAMPLE_RANGES, _FIXTURE_RANGES[0])}, "chained", id="duplicate-case"),
    pytest.param({"inputs": _ranges(*SAMPLE_RANGES[:-1])}, "chained", id="missing-fixture-case"),
    pytest.param({"inputs": dataclasses.replace(sample_inputs(), fixture=FixtureHashes("a" * 40, sample_inputs().fixture.tags[:-1]))},
                 "fixture tags", id="fixture-tags"),
    pytest.param({"inputs": _pin_without_upstream()}, "upstream", id="pin-trust"),
    pytest.param({"inputs": dataclasses.replace(sample_inputs(), flags=("-c", "x"))}, "flags", id="flags"),
    pytest.param({"inputs": dataclasses.replace(sample_inputs(), environment=("HOME",))}, "environment", id="environment"),
    pytest.param({"files": ((CLIFF_TOML, "0" * 64), *sample_bundle().files[1:])}, CLIFF_TOML, id="cliff-digest"),
    pytest.param({"outputs": ComparisonResult(sample_outputs().cases[:1])}, "ranges", id="outputs-not-ranges"),
    pytest.param({"classification": ()}, "unclassified", id="unclassified"),
    pytest.param({"classification": (*sample_bundle().classification, Classification("llm-shared full history #1", "intentional", "x"))},
                 "unknown hunk", id="unknown-hunk"),
    pytest.param({"classification": (Classification(_CLASSIFIED, "defect", "the security group moved"),)}, "defect", id="defect"),
    pytest.param({"classification": (Classification(_CLASSIFIED, "intentional", " "),)}, "reason", id="no-reason"),
    pytest.param({"classification": (Classification(_CLASSIFIED, "maybe", "x"),)}, "maybe", id="kind"),
])
def test_the_checks_refuse_each_gap(changes: dict[str, object], reason: str) -> None:
    """Each gap is refused with its reason, before any admission."""
    bundle = dataclasses.replace(sample_bundle(), **changes)
    with pytest.raises(BundleError, match=reason):
        require_complete(bundle, location=_LOCATION, pins=())


def _audit(**changes: object) -> Audit:
    """The sample audit with some fields changed."""
    audit = sample_bundle().audit
    assert audit is not None
    return dataclasses.replace(audit, **changes)


def _categories(index: int, **changes: object) -> tuple[AuditCategory, ...]:
    """The sample categories with one of them changed."""
    categories = _audit().categories
    return (*categories[:index], dataclasses.replace(categories[index], **changes), *categories[index + 1:])


def _observed(*statuses: ObservedStatus) -> tuple[ObservedStatus, ...]:
    """The sample observations with some replaced by name, or added."""
    replaced = {status.name: status for status in statuses}
    kept = tuple(replaced.pop(item.name, item) for item in sample_bundle().observed_statuses)
    return (*kept, *replaced.values())


@pytest.mark.parametrize(("changes", "reason"), [
    pytest.param({"audit": None}, "no exit-path audit", id="no-audit"),
    pytest.param({"audit": _audit(revision="")}, "revision", id="no-revision"),
    pytest.param({"audit": _audit(commands=())}, "command", id="no-command"),
    pytest.param({"audit": _audit(commands=(" ",))}, "command", id="blank-command"),
    pytest.param({"audit": _audit(categories=_audit().categories[:-1])}, "cover", id="missing-category"),
    pytest.param({"audit": _audit(categories=(*_audit().categories, _audit().categories[0]))}, "cover", id="repeated-category"),
    pytest.param({"audit": _audit(categories=_categories(0, references=()))}, "references", id="no-reference"),
    pytest.param({"audit": _audit(categories=_categories(1, references=(" ",)))}, "references", id="blank-reference"),
    pytest.param({"audit": _audit(categories=_categories(2, finding=" "))}, "finding", id="no-finding"),
    pytest.param({"audit": _audit(excludes_69=False)}, "does not exclude status 69", id="not-excluded"),
    pytest.param({"observed_statuses": sample_bundle().observed_statuses[:-1]}, "must include", id="missing-observation"),
    pytest.param({"observed_statuses": _observed(ObservedStatus("usage error", " ", 2))}, "command", id="blank-observed-command"),
    pytest.param({"observed_statuses": _observed(ObservedStatus("panic", "git-cliff --panic", 69))}, "contradicts", id="observed-69"),
    pytest.param({"observed_statuses": _observed(ObservedStatus("success", "git-cliff --version", 1))}, "success", id="failing-success"),
    pytest.param({"observed_statuses": _observed(ObservedStatus("failing render", "git-cliff -c broken.toml", 0))}, "a failure must not be", id="passing-failure"),
])
def test_the_exclusion_of_69_needs_its_audit_evidence_and_consistent_observations(changes: dict[str, object], reason: str) -> None:
    """The revision, the commands, each exit-path category with references and a finding, and the three required observations."""
    bundle = dataclasses.replace(sample_bundle(), **changes)
    with pytest.raises(BundleError, match=reason):
        require_complete(bundle, location=_LOCATION, pins=())
    assert AUDIT_CATEGORIES == ("error return", "argument-parsing errors", "propagated helper statuses", "panics and abnormal termination")
    assert OBSERVATIONS == ("success", "usage error", "failing render")


def _replaced_case(index: int, case: CaseResult) -> ComparisonResult:
    """The sample outputs with one case replaced."""
    cases = sample_outputs().cases
    return ComparisonResult((*cases[:index], case, *cases[index + 1:]))


def test_identical_outputs_with_hunks_and_differing_outputs_without_are_refused() -> None:
    """Hunks exist exactly where the two digests differ."""
    cases = sample_outputs().cases
    with_hunk = _replaced_case(0, dataclasses.replace(cases[0], hunks=("@@ -1 +1 @@\n-a\n+b",)))
    without = _replaced_case(DIFFERING_INDEX, dataclasses.replace(cases[DIFFERING_INDEX], hunks=()))
    for outputs in (with_hunk, without):
        with pytest.raises(BundleError, match="hunks"):
            require_complete(dataclasses.replace(sample_bundle(), outputs=outputs), location=_LOCATION, pins=())


def test_results_of_other_versions_are_refused() -> None:
    """Each case holds the baseline's result, then the pin's."""
    case = sample_outputs().cases[0]
    outputs = _replaced_case(0, dataclasses.replace(case, results=tuple(reversed(case.results))))
    with pytest.raises(BundleError, match="baseline"):
        require_complete(dataclasses.replace(sample_bundle(), outputs=outputs), location=_LOCATION, pins=())


def _with_tags(*tags: str, ranges: tuple[str, ...] | None = None) -> Bundle:
    """A bundle whose inputs record these llm-shared tags, with ranges chained from `ranges` (the tags by default) and matching outputs."""
    inputs = sample_inputs()
    names = tags if ranges is None else ranges
    cases = (*chained_ranges("llm-shared", names), *(case for case in SAMPLE_RANGES if case.repository == "fixture"))
    same = RunDigest("1" * 64, 0)
    differing = sample_outputs().cases[DIFFERING_INDEX]
    outputs = ComparisonResult(tuple(differing if case == DIFFERING else CaseResult(case, ((BASELINE, same), (PIN, same))) for case in cases))
    recorded = tuple((name, f"{index:040x}") for index, name in enumerate(tags, start=1))
    return dataclasses.replace(sample_bundle(), inputs=dataclasses.replace(inputs, llm_shared_tags=recorded, ranges=cases), outputs=outputs)


def test_the_ranges_must_chain_exactly_the_recorded_tags() -> None:
    """Round 2: chained from llm-shared's recorded tags, it passes; an omitted, a repeated tag or full history alone is refused."""
    require_complete(_with_tags("v0.1.0", "v0.2.0"), location=_LOCATION, pins=())
    for bundle in (_with_tags("v0.1.0", "v0.2.0", ranges=("v0.2.0",)), _with_tags("v0.1.0", "v0.1.0"), _with_tags("v0.1.0", ranges=())):
        with pytest.raises(BundleError, match="chained ranges of its recorded tags"):
            require_complete(bundle, location=_LOCATION, pins=())


def test_a_case_where_the_pin_returned_69_is_refused_even_with_a_current_review() -> None:
    """Round 2: a comparison run of the pin returning 69 contradicts the audit, whatever the review says."""
    cases = sample_outputs().cases
    failing = dataclasses.replace(cases[0], results=(cases[0].results[0], (PIN, RunDigest(cases[0].results[1][1].sha256, 69))))
    bundle = dataclasses.replace(sample_bundle(), outputs=ComparisonResult((failing, *cases[1:])))
    with pytest.raises(BundleError, match=f"git-cliff {PIN} returned 69"):
        require_admissible(with_review(bundle, "approved", _DAY), location=_LOCATION, pins=())


@pytest.mark.parametrize(("observed", "reason"), [
    pytest.param((ObservedStatus("success", "git-cliff --version", 69), ObservedStatus("success", "git-cliff --version", 0)), "returned 69",
                 id="hidden-69"),
    pytest.param((ObservedStatus("success", "git-cliff --version", 1), ObservedStatus("success", "git-cliff --version", 0)), "returned 1",
                 id="hidden-failing-success"),
])
def test_a_repeated_observation_cannot_hide_a_status_even_with_a_current_review(observed: tuple[ObservedStatus, ...], reason: str) -> None:
    """Round 2: each observation is checked on its own, before the later one of the same name."""
    bundle = dataclasses.replace(sample_bundle(), observed_statuses=(*observed, *sample_bundle().observed_statuses[1:]))
    with pytest.raises(BundleError, match=reason):
        require_admissible(with_review(bundle, "approved", _DAY), location=_LOCATION, pins=())


# eof
