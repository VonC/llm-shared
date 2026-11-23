"""Decide whether an evidence bundle can admit its pin: completeness first, then the user's current approval.

Step 6 of v0.14.0 git-cliff-provisioning (design "Outputs and
classification" and "Statuses"; design decisions Q11 and Q13; plan decision
Q16). Split from `bundle` in code review round 2, so the storage model and
these admission rules each stay one responsibility; nothing here writes.

- `require_complete(bundle, *, location, pins)` refuses, with the first gap
  it finds: flags, environment names or ranges other than the frozen rule
  (llm-shared's full history and the chained ranges of its recorded tags,
  each tag once, then exactly the fixture's), one version for both
  candidates, fixture tags other than its own, a pin without upstream-digest
  trust, a `cliff.toml` digest other than the listed one; outputs that do
  not follow the ranges, results of other versions, hunks where the outputs
  are equal or none where they differ, a case where the pin returned 69; an
  unknown, repeated or unclassified hunk, a defect, an intentional entry
  without its reason; an audit without its revision, commands, every
  exit-path category of `AUDIT_CATEGORIES` once with references and a
  finding, or the exclusion of 69; an observation that returned 69, has no
  command, or reports an inconsistent status, each checked on its own, and
  a missing one of `OBSERVATIONS`; and a manifest entry of the pin that does
  not name this bundle with the reviewed asset, size and digest.
- `require_admissible` adds the review: present, approved, by `user`, with an
  ISO local date, covering the current projection. A listed file changed
  after the approval never reaches it: `bundle.read`, through which every
  committed bundle passes, refuses it first.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import date
from typing import TYPE_CHECKING

from tools.release_workflow.git_cliff.bundle import (
    CLIFF_TOML,
    DECISIONS,
    REVIEWER,
    BundleError,
    covered_sha256,
)
from tools.release_workflow.git_cliff.candidates import UPSTREAM_DIGEST
from tools.release_workflow.git_cliff.comparison import (
    ENVIRONMENT,
    FLAGS,
    chained_ranges,
)
from tools.release_workflow.git_cliff.fixture_history import TAGS
from tools.release_workflow.git_cliff.manifest import ADMITTED_PINS

if TYPE_CHECKING:
    from tools.release_workflow.git_cliff.bundle import Audit, Bundle, ObservedStatus
    from tools.release_workflow.git_cliff.comparison import FrozenInputs
    from tools.release_workflow.git_cliff.manifest import AdmittedPin

KINDS = ("intentional", "defect")
AUDIT_CATEGORIES = ("error return", "argument-parsing errors", "propagated helper statuses", "panics and abnormal termination")
OBSERVATIONS = ("success", "usage error", "failing render")
_EXCLUDED_STATUS = 69
_LOCATION = "tools/release_workflow/git_cliff/bundles/{pin}"
_OBJECT = re.compile(r"[0-9a-f]{40}")


def _inputs_problem(bundle: Bundle) -> str | None:
    """Name the first missing or foreign input."""
    inputs = bundle.inputs
    versions = tuple(candidate.version for candidate in inputs.candidates)
    pin_trust = next((candidate.trust for candidate in inputs.candidates if candidate.version == inputs.pin), None)
    listed = dict(bundle.files).get(CLIFF_TOML)
    return next((problem for problem, failed in (
        (f"the flags {list(inputs.flags)} are not {list(FLAGS)}", inputs.flags != FLAGS),
        (f"the environment names {list(inputs.environment)}, not {list(ENVIRONMENT)}", inputs.environment != ENVIRONMENT),
        ("the inputs hold no ranges", not inputs.ranges),
        (f"the pin and the baseline are both {inputs.pin}", inputs.pin == inputs.baseline),
        ("the ranges must be llm-shared's full history and the chained ranges of its recorded tags, each tag once, then exactly the fixture's",
         not _matrix_complete(inputs)),
        (f"the fixture tags are {[name for name, _sha in inputs.fixture.tags]}, expected {list(TAGS)}",
         tuple(name for name, _sha in inputs.fixture.tags) != TAGS),
        (f"the candidates name {list(versions)}, expected the baseline {inputs.baseline} then the pin {inputs.pin}",
         versions != (inputs.baseline, inputs.pin)),
        (f"the pin {inputs.pin} has {pin_trust} trust; admission needs {UPSTREAM_DIGEST}", pin_trust != UPSTREAM_DIGEST),
        (f"{CLIFF_TOML} is listed as {listed}, the inputs record {inputs.cliff_toml.sha256}", listed != inputs.cliff_toml.sha256),
    ) if failed), None)


def _matrix_complete(inputs: FrozenInputs) -> bool:
    """Tell whether the ranges are exactly the chained cases of llm-shared's recorded tags, each once, then the fixture's."""
    names = [name for name, _commit in inputs.llm_shared_tags]
    return len(set(names)) == len(names) and inputs.ranges == (*chained_ranges("llm-shared", names), *chained_ranges("fixture", TAGS))


def _outputs_problem(bundle: Bundle) -> str | None:
    """Name the first case that does not follow the inputs."""
    if [case.case for case in bundle.outputs.cases] != list(bundle.inputs.ranges):
        return "the outputs do not follow the ranges of the inputs"
    for case in bundle.outputs.cases:
        versions = tuple(version for version, _digest in case.results)
        if versions != (bundle.baseline, bundle.pin):
            return f"{case.case.key}: the results must be the baseline {bundle.baseline}'s, then the pin {bundle.pin}'s"
        if (case.results[0][1].sha256 != case.results[1][1].sha256) != bool(case.hunks):
            return f"{case.case.key}: hunks must exist exactly where the two outputs differ"
        if case.results[1][1].status == _EXCLUDED_STATUS:
            return f"{case.case.key}: git-cliff {bundle.pin} returned {_EXCLUDED_STATUS}, which the exit-path audit excludes"
    return None


def _classification_problem(bundle: Bundle) -> str | None:
    """Name the first hunk without a valid intentional classification."""
    identifiers = bundle.outputs.hunk_ids
    known, seen = set(identifiers), set[str]()
    for entry in bundle.classification:
        if entry.hunk not in known or entry.hunk in seen:
            return f"the classification names an unknown hunk or one twice: {entry.hunk}"
        seen.add(entry.hunk)
        if entry.kind not in KINDS:
            return f"{entry.hunk}: unknown classification kind {entry.kind!r}"
        if entry.kind == "defect":
            return f"{entry.hunk} is classified as a defect: {entry.reason}"
        if not entry.reason.strip():
            return f"{entry.hunk} needs its upstream release-note reason"
    missing = [identifier for identifier in identifiers if identifier not in seen]
    return f"unclassified hunks: {', '.join(missing)}" if missing else None


def _blank(texts: tuple[str, ...]) -> bool:
    """Tell whether a list of texts is empty or holds a blank one."""
    return not texts or any(not text.strip() for text in texts)


def _audit_problem(audit: Audit | None) -> str | None:
    """Name what keeps the exit-path audit from supporting the exclusion of 69: its revision, commands and categories."""
    if audit is None:
        return "no exit-path audit is recorded"
    names = [category.name for category in audit.categories]
    return next((problem for problem, failed in (
        ("the exit-path audit lacks the revision it read", _OBJECT.fullmatch(audit.revision) is None),
        ("the exit-path audit records no clone or read command", _blank(audit.commands)),
        (f"the exit-path audit must cover {list(AUDIT_CATEGORIES)} once each, not {names}", Counter(names) != Counter(AUDIT_CATEGORIES)),
        ("each exit-path audit category needs its source references and its finding",
         any(_blank(item.references) or _blank((item.finding,)) for item in audit.categories)),
        ("the exit-path audit does not exclude status 69", not audit.excludes_69),
    ) if failed), None)


def _observation_issue(item: ObservedStatus) -> str | None:
    """Name what makes one observation contradict the audit or its own name: a 69, no command, an inconsistent status."""
    if item.status == _EXCLUDED_STATUS:
        return f"the observed {item.name!r} returned {_EXCLUDED_STATUS}, which contradicts the audit"
    if not item.command.strip():
        return f"the observed {item.name!r} needs its command"
    inconsistent = item.status != 0 if item.name == "success" else (item.name in OBSERVATIONS[1:] and item.status == 0)
    return f"the observed {item.name!r} returned {item.status}: a success must be status 0, and a failure must not be" if inconsistent else None


def _observation_problem(observed: tuple[ObservedStatus, ...]) -> str | None:
    """Name the first observation that does not corroborate the audit, each one checked, then a missing required case."""
    issue = next((found for item in observed if (found := _observation_issue(item)) is not None), None)
    if issue is not None:
        return issue
    names = {item.name for item in observed}
    missing = [name for name in OBSERVATIONS if name not in names]
    return f"the observed statuses must include {missing}" if missing else None


def _manifest_problem(bundle: Bundle, where: str, pins: tuple[AdmittedPin, ...]) -> str | None:
    """Name a manifest entry of the pin that does not reference this bundle and its reviewed identity."""
    reviewed = next(((item.asset, item.size, item.sha256) for item in bundle.inputs.candidates if item.version == bundle.pin), None)
    for pin in pins:
        admitted = (pin.asset, pin.size, pin.sha256)
        if pin.version == bundle.pin and (pin.evidence, admitted) != (where, reviewed):
            return f"the manifest admits {pin.version} as {admitted} with the evidence {pin.evidence}, not this bundle's reviewed {reviewed} at {where}"
    return None


def require_complete(bundle: Bundle, *, location: str | None = None, pins: tuple[AdmittedPin, ...] = ADMITTED_PINS) -> None:
    """Refuse a bundle that cannot admit its pin, before any review.

    Args:
        bundle: The bundle, as `read` returns it.
        location: Its repository-relative directory; by default `tools/release_workflow/git_cliff/bundles/<pin>`.
        pins: The manifest's admitted pins, read for their evidence references.

    Raises:
        BundleError: The first gap: an input, an output, a classification, the audit or the manifest reference.
    """
    where = _LOCATION.format(pin=bundle.pin) if location is None else location
    problem = (_inputs_problem(bundle) or _outputs_problem(bundle) or _classification_problem(bundle) or _audit_problem(bundle.audit)
               or _observation_problem(bundle.observed_statuses) or _manifest_problem(bundle, where, pins))
    if problem is not None:
        raise BundleError(problem)


def _review_problem(bundle: Bundle) -> str | None:
    """Name what keeps the review from admitting the pin."""
    review = bundle.review
    if review is None:
        return "the bundle holds no review by the user"
    problems = (
        (f"the reviewer is {review.reviewer!r}, not {REVIEWER!r}", review.reviewer != REVIEWER),
        (f"the user rejected this evidence on {review.date}", review.decision == "rejected"),
        (f"the review decision {review.decision!r} is neither approved nor rejected", review.decision not in DECISIONS),
        (f"the review date {review.date!r} is not an ISO local date", not _iso_date(review.date)),
        (f"the evidence changed after the review of {review.date}: it covers {review.covered_sha256}, the bundle is now {covered_sha256(bundle)}",
         review.covered_sha256 != covered_sha256(bundle)),
    )
    return next((problem for problem, failed in problems if failed), None)


def _iso_date(text: str) -> bool:
    """Tell whether a text is exactly an ISO calendar date, `YYYY-MM-DD`."""
    try:
        return date.fromisoformat(text).isoformat() == text
    except ValueError:
        return False


def require_admissible(bundle: Bundle, *, location: str | None = None, pins: tuple[AdmittedPin, ...] = ADMITTED_PINS) -> None:
    """Refuse a bundle that is incomplete or lacks the user's current approval.

    A listed file changed after the approval never reaches this check: `read`, through which every committed bundle
    passes, refuses it first.

    Raises:
        BundleError: The first completeness gap, or an absent, rejected, malformed or stale review.
    """
    require_complete(bundle, location=location, pins=pins)
    problem = _review_problem(bundle)
    if problem is not None:
        raise BundleError(problem)


# eof
