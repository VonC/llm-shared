"""Step 1 through 4 acceptance for independent review-mode documentation.

The suite pins discovery, terminology, tutorials, task ownership, recovery,
the exact reference contract, and the incremental AC01-through-AC12 record.
Final Step 5 coverage belongs to the sibling final-acceptance module. Resume
Step 6 updates recovery expectations for the shipped automatic pickup flow.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tools.review_exchange_models import ArtifactState

from .conftest import (
    _CODE_TUTORIAL,
    _COVERAGE,
    _EXPLANATION,
    _HOW_TO_GUIDES,
    _INVENTORY_CANDIDATES,
    _REFERENCE,
    _SELF_REVIEW_EXPLANATION,
    _SELF_REVIEW_HOW_TO,
    _SPEC_TUTORIAL,
    assert_contains,
    assert_local_links,
    assert_named_paths,
    read_declared,
)

if TYPE_CHECKING:
    from pathlib import Path

_RECOVERY_GUIDE = _HOW_TO_GUIDES[-1]
_STEP_1_PAGES = (
    "README.md", "wiki/README.md", _EXPLANATION,
    _SELF_REVIEW_EXPLANATION, _SELF_REVIEW_HOW_TO, _COVERAGE,
)
_CANONICAL_INSTRUCTIONS = (
    "instructions/review-requestor.md",
    "instructions/spec-reviewer.md",
    "instructions/code-reviewer.md",
)
_BACKTICK = "`"
_REVIEW_OUTCOMES = (
    "disabled", "activated", "observed", "started", "continued",
    "ownership-picked-up", "reclaimed",
    "force-reclaimed", "completed", "force-completed", "published", "repaired",
    "found", "timed-out", "abandoned", "escalated", "inconsistent",
    "repair-required", "consumed", "cancelled", "archived", "resolved",
    "another-round", "continue-owning-workflow", "fatal-input",
)


def _heading_position(markdown: str, label: str) -> int:
    """Return the position of one second-level heading containing a label."""
    match = re.search(rf"^## .*{label}.*$", markdown, re.MULTILINE)
    assert match is not None
    return match.start()


def _second_level_section(markdown: str, heading: str) -> str:
    """Return one declared second-level section without reading other files."""
    start = markdown.index(f"## {heading}")
    end = markdown.find("\n## ", start + len(heading) + 3)
    return markdown[start:] if end < 0 else markdown[start:end]


def test_step_1_entry_points_distinguish_review_modes_and_keep_diataxis_order(
    docs_root: Path,
) -> None:
    """Step 1 discovery: both entry points route to the new explanation."""
    root_readme = read_declared(docs_root, "README.md")
    wiki_readme = read_declared(docs_root, "wiki/README.md")

    assert "independent review mode" in root_readme
    assert _EXPLANATION in root_readme
    assert "self-review loop" in root_readme
    assert "independent review mode" in wiki_readme
    assert "explanation/independent-review-mode-and-human-authority.md" in wiki_readme
    headings = tuple(
        _heading_position(wiki_readme, label)
        for label in ("Explanation", "Tutorials", "How-to guides", "Reference")
    )
    assert headings == tuple(sorted(headings))


def test_step_1_visual_identity_and_reciprocal_comparison_stay_distinct(
    docs_root: Path,
) -> None:
    """Step 1 identity: generic independent logo, retained self-review logo."""
    explanation = read_declared(docs_root, _EXPLANATION)
    self_review_explanation = read_declared(docs_root, _SELF_REVIEW_EXPLANATION)
    self_review_how_to = read_declared(docs_root, _SELF_REVIEW_HOW_TO)

    assert "../assets/logo-llm-shared-transparent.png" in explanation
    assert "logo-llm-shared-review-transparent.png" in self_review_explanation
    assert "logo-llm-shared-review-transparent.png" in self_review_how_to
    comparison_link = "independent-review-mode-and-human-authority.md"
    assert comparison_link in self_review_explanation
    assert f"../explanation/{comparison_link}" in self_review_how_to


def test_step_1_explanation_names_authorities_and_canonical_policy(
    docs_root: Path,
) -> None:
    """Step 1 authority: advisory results and durable evidence are explicit."""
    explanation = read_declared(docs_root, _EXPLANATION)

    for role in ("requestor", "reviewer", "human"):
        assert role in explanation
    assert "does not authorize consolidation or commit" in explanation
    assert "not working context" in explanation
    for instruction in _CANONICAL_INSTRUCTIONS:
        assert f"../../{instruction}" in explanation


def test_step_1_declared_links_and_named_paths_resolve(docs_root: Path) -> None:
    """Step 1 links: bounded declared pages resolve local targets and fragments."""
    assert_local_links(docs_root, _STEP_1_PAGES)
    assert_named_paths(
        docs_root,
        (
            *_STEP_1_PAGES,
            *_CANONICAL_INSTRUCTIONS,
            "wiki/assets/logo-llm-shared-transparent.png",
            "wiki/assets/logo-llm-shared-review-transparent.png",
        ),
    )


def test_step_1_coverage_keeps_complete_enumerations_and_evidence(
    docs_root: Path,
) -> None:
    """Step 1 coverage: criteria, candidates, and initial evidence stay named."""
    coverage = read_declared(docs_root, _COVERAGE)

    for number in range(1, 13):
        assert coverage.count(f"| AC{number:02d} |") == 1
    for candidate in _INVENTORY_CANDIDATES:
        assert coverage.count(f"{_BACKTICK}{candidate}{_BACKTICK}") == 1
    assert "| AC02 | Page evidence |" in coverage
    assert "| AC10 | Validation evidence | Complete |" in coverage
    assert "## Step 1 executable evidence" in coverage


def test_step_2_tutorials_append_numbers_cross_link_and_resolve(
    docs_root: Path,
) -> None:
    """Step 2 order: tutorials 09 and 10 append, cross-link, and resolve."""
    wiki_readme = read_declared(docs_root, "wiki/README.md")
    specification = read_declared(docs_root, _SPEC_TUTORIAL)
    code = read_declared(docs_root, _CODE_TUTORIAL)

    spec_link = "tutorials/09-run-your-first-specification-review.md"
    code_link = "tutorials/10-run-your-first-implementation-code-review.md"
    assert "tutorials/08-protect-your-first-repository.md" in wiki_readme
    assert wiki_readme.index(spec_link) < wiki_readme.index(code_link)
    assert "10-run-your-first-implementation-code-review.md" in specification
    assert "09-run-your-first-specification-review.md" in code
    for tutorial in (specification, code):
        assert "../assets/logo-llm-shared-transparent.png" in tutorial
    assert_local_links(docs_root, (_SPEC_TUTORIAL, _CODE_TUTORIAL, "wiki/README.md"))


def test_step_2_tutorials_show_two_agent_sessions_and_round_trip(
    docs_root: Path,
) -> None:
    """Step 2 handoff: each journey shows both agents and the returned answer."""
    for tutorial_path in (_SPEC_TUTORIAL, _CODE_TUTORIAL):
        tutorial = read_declared(docs_root, tutorial_path)
        assert "Requestor agent session" in tutorial
        assert "Reviewer agent session" in tutorial
        assert "bounded wait" in tutorial
        assert "paths.answer" in tutorial
        assert "changes-requested" in tutorial
        assert "round 2" in tutorial.casefold()
        assert "Return to the requestor agent session" in tutorial


def test_step_2_family_evidence_and_human_choices_stay_distinct(
    docs_root: Path,
) -> None:
    """Step 2 families: identity, evidence, and human gates remain distinct."""
    specification = read_declared(docs_root, _SPEC_TUTORIAL)
    code = read_declared(docs_root, _CODE_TUTORIAL)

    for term in ("umbrella", "reviewed specification", "round"):
        assert term in specification
    for choice in ("Consolidate", "Revise and review again"):
        assert choice in specification
    for term in (
        "implementation plan",
        "implementation step",
        "request_index_tree",
        "resolved_validation_set",
        "validation-state compare",
        "a.commit",
    ):
        assert term in code
    for choice in ("Commit", "Rework and review again"):
        assert choice in code


def test_step_2_coverage_records_completed_tutorial_evidence(
    docs_root: Path,
) -> None:
    """Step 2 coverage: AC03 and tutorial evidence name both pages and tests."""
    coverage = read_declared(docs_root, _COVERAGE)

    assert "## Step 2 executable evidence" in coverage
    assert "| AC03 | Page evidence | Complete |" in coverage
    assert _SPEC_TUTORIAL in coverage
    assert _CODE_TUTORIAL in coverage
    assert "test_step_2_tutorials_show_two_agent_sessions_and_round_trip" in coverage
    assert "| AC05 | Page evidence | Complete |" in coverage


def test_step_3_five_how_to_pages_assign_all_seven_goals(docs_root: Path) -> None:
    """Step 3 topology: five focused pages own all seven operational goals."""
    wiki_readme = read_declared(docs_root, "wiki/README.md")
    required_phrases = {
        _HOW_TO_GUIDES[0]: ("Enable review mode", "Disable review mode"),
        _HOW_TO_GUIDES[1]: ("Start a specification review", "Resume a specification review"),
        _HOW_TO_GUIDES[2]: ("Start an implementation code review", "Resume an implementation code review"),
        _HOW_TO_GUIDES[3]: ("Read the returned result", "Continue an authorized action"),
        _HOW_TO_GUIDES[4]: ("Reclaim an expired live exchange", "Recover a stopped exchange"),
    }

    for path, phrases in required_phrases.items():
        guide = read_declared(docs_root, path)
        assert path.removeprefix("wiki/") in wiki_readme
        assert "../assets/logo-llm-shared-transparent.png" in guide
        assert "## Invocation model" in guide
        for phrase in phrases:
            assert phrase in guide
    assert_local_links(docs_root, (*_HOW_TO_GUIDES, "wiki/README.md"))


def test_step_3_procedures_follow_returned_paths_and_exit_contract(
    docs_root: Path,
) -> None:
    """Step 3 results: paths are authoritative and exits retain their meaning."""
    for path in _HOW_TO_GUIDES:
        guide = read_declared(docs_root, path)
        assert "final JSON" in guide
        assert "`paths`" in guide
        assert "Do not reconstruct protocol filenames or edit protocol artifacts." in guide

    results = read_declared(docs_root, _HOW_TO_GUIDES[3])
    for exit_code in ("Exit `0`", "Exit `3`", "Exit `2`"):
        assert exit_code in results
    assert "owning_action_authorized" in results
    assert "owning-action-pending" in results


def test_step_3_recovery_separates_reclaim_from_human_operations(
    docs_root: Path,
) -> None:
    """Step 3 recovery: ordinary reclaim precedes marked human-only commands."""
    recovery = read_declared(docs_root, _RECOVERY_GUIDE)
    ordinary = recovery.index("## Reclaim an expired live exchange")
    human = recovery.index("## Human decision required")

    assert ordinary < human
    for label in ("Authority:", "Precondition:", "Evidence effect:"):
        assert recovery.index(label, human) > human
    for command in (
        "reclaim --force",
        "review_exchange.bat resolve",
        "complete --force",
    ):
        assert recovery.index(command) > human
    for state in (
        "timeout",
        "abandoned",
        "no-progress",
        "disagreement",
        "inconsistent",
        "interrupted",
    ):
        assert state in recovery


def _assert_phrases(content: str, phrases: tuple[str, ...]) -> None:
    """Assert one bounded list of exact documentation phrases."""
    normalized = " ".join(content.split())
    for phrase in phrases:
        assert phrase in normalized


def test_step_3_new_session_pickup_is_discoverable_and_precise(
    docs_root: Path,
) -> None:
    """Bare resume recovers the session while retaining the established ownership fence."""
    readme = read_declared(docs_root, "README.md")
    explanation = read_declared(docs_root, _EXPLANATION)
    recovery = read_declared(docs_root, _RECOVERY_GUIDE)
    reference = read_declared(docs_root, _REFERENCE)

    _assert_phrases(readme, ("enter `resume`", "automatic pickup"))
    _assert_phrases(
        recovery,
        (
            "Continue an active review with resume",
            "automatic pickup",
            "missing or stale session capability",
            "Let the skill check migration first",
            "without waiting for the previous lease to expire",
        ),
    )
    _assert_phrases(explanation, ("new generation", "not a reset", "`reclaim`"))
    _assert_phrases(
        reference,
        (
            "| `pickup` |",
            "`ownership_generation`",
            "`ownership_token`",
            "`ownership-picked-up`",
        ),
    )


def test_step_3_coverage_records_task_and_recovery_evidence(
    docs_root: Path,
) -> None:
    """Step 3 coverage: AC04 and AC07 retain guides and executable tests."""
    coverage = read_declared(docs_root, _COVERAGE)

    assert "## Step 3 executable evidence" in coverage
    assert "| AC04 | Page evidence | Complete |" in coverage
    assert "| AC07 | Page evidence | Complete |" in coverage
    for path in _HOW_TO_GUIDES:
        assert path in coverage
    assert "test_step_3_recovery_separates_reclaim_from_human_operations" in coverage
    assert "| AC10 | Validation evidence | Complete |" in coverage


def test_step_4_reference_pins_every_state_and_fatal_payload(docs_root: Path) -> None:
    """Step 4 states: typed rows plus disabled and fatal stay complete."""
    reference = read_declared(docs_root, _REFERENCE)
    state_section = _second_level_section(reference, "State matrix")
    documented = set(re.findall(r"^\| `([^`]+)` \|", state_section, re.MULTILINE))

    assert documented == {state.value for state in ArtifactState} | {
        "disabled",
        "fatal",
    }
    fatal_row = next(
        line for line in state_section.splitlines() if line.startswith("| `fatal` |")
    )
    for value in (
        "caller",
        "null `identity`",
        "empty `paths`",
        "null round",
        "`fatal-input`",
        "Correct the input and re-run",
    ):
        assert value in fatal_row


def test_step_4_reference_pins_result_artifact_and_human_contract(
    docs_root: Path,
) -> None:
    """Step 4 result: fields, exits, artifacts, paths, and choices are exact."""
    reference = read_declared(docs_root, _REFERENCE)
    result_section = _second_level_section(reference, "Final result contract")

    assert_contains(
        result_section,
        tuple(
            f"`{field}`"
            for field in (
                "diagnostic", "identity", "operation", "outcome",
                "paths", "round", "state",
            )
        ),
    )
    assert_contains(
        result_section,
        tuple(
            f"`{key}`"
            for key in (
                "answer", "coordination", "request", "tombstone",
                "transcript", "transition_lock",
            )
        ),
    )
    assert_contains(result_section, ("Exit `0`", "Exit `3`", "Exit `2`"))
    assert_contains(
        result_section,
        (
            "Consolidate",
            "Revise and review again",
            "Commit",
            "Rework and review again",
        ),
    )
    assert "one final JSON object on standard output" in result_section
    assert "standard error is progress only" in result_section
    assert "returned `paths` object is authoritative" in result_section


def test_step_4_reference_pins_reviewed_outcomes_and_sources(docs_root: Path) -> None:
    """Step 4 outcomes: the reviewed inline-string snapshot stays explicit."""
    reference = read_declared(docs_root, _REFERENCE)
    outcome_section = _second_level_section(reference, "Operation outcome snapshot")
    documented = tuple(
        re.findall(r"^\| `([^`]+)` \|", outcome_section, re.MULTILINE),
    )

    assert documented == _REVIEW_OUTCOMES
    for source in (
        "plain `OperationResult`",
        "conditional `OperationResult`",
        "all `WaitOutcome` values",
        "both `ConfirmationOutcome` values",
        "CLI fatal payload",
    ):
        assert source in outcome_section


def test_step_4_adapters_and_inventory_dispositions_are_complete(
    docs_root: Path,
) -> None:
    """Step 4 discovery: host gaps and all inventory decisions stay visible."""
    reference = read_declared(docs_root, _REFERENCE)
    adapters = _second_level_section(reference, "Host adapter matrix")
    coverage = read_declared(docs_root, _COVERAGE)

    for row in (
        ("Codex", ".agents/llm-shared/skills/", "$", "review-requestor"),
        ("Claude Code", ".claude/skills/", "/", "absent"),
        ("Antigravity", ".agent/workflows/", "/", "review-requestor"),
    ):
        line = next(line for line in adapters.splitlines() if f"| {row[0]} |" in line)
        for value in row[1:]:
            assert value in line
        assert "canonical" in line
    for candidate in _INVENTORY_CANDIDATES:
        assert f"| `{candidate}` | Update |" in coverage
        inventory = read_declared(docs_root, candidate)
        assert "independent-review-mode-contract.md" in inventory
    assert_local_links(docs_root, (_REFERENCE, "wiki/README.md", *_INVENTORY_CANDIDATES))
