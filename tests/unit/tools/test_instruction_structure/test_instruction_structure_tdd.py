"""Structural check that the workflow instructions carry their handoff, hint, or list.

Step 5 of docs/plan.v0.9.0.handoff_automation.md guards the markdown sections
added in Steps 4 and 5: the writing and consolidation instructions carry a
``## Handoff`` that runs ``pw skill``, the review instruction leaves the
consolidation hint, and the splitting instructions present a multi-choice list
with a free-text entry. The check runs on every walk, so a later edit that drops
one fails fast (Q06).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_steps as steps

# Keep this module's scenarios on one xdist worker so its module-scoped
# fixtures are built once rather than once per worker (--dist loadgroup).
pytestmark = pytest.mark.xdist_group("instruction-structure")

if TYPE_CHECKING:
    from pathlib import Path

_INSTRUCTIONS = steps.llm_shared_dir() / "instructions"
_EXPECTED_DIAGRAM_COUNT = 4


def _read(name: str) -> str:
    """Return the text of an instruction file."""
    return (_INSTRUCTIONS / name).read_text(encoding="utf-8")


def _assert_contains_all(content: str, fragments: tuple[str, ...]) -> None:
    """Report every required fragment missing from one instruction slice."""
    missing = tuple(fragment for fragment in fragments if fragment not in content)
    assert not missing, f"missing instruction fragments: {missing!r}"


def test_writing_and_consolidate_instructions_carry_a_handoff() -> None:
    """The four writing and consolidation instructions run pw skill in a ## Handoff."""
    for name in (
        "write-requirement.md",
        "write-design.md",
        "write-plans.md",
        "consolidate-then-review-ask-questions.md",
    ):
        content = _read(name)
        assert "## Handoff" in content
        assert "pw skill" in content


def test_consolidation_commits_one_question_snapshot_before_editing() -> None:
    """Every document type records its answered questions before the fold."""
    content = _read("consolidate-then-review-ask-questions.md")
    snapshot = content.index("## Pre-consolidation question snapshot")
    integration = content.index("You need to remove `Qxx:` sections")
    snapshot_contract = " ".join(content[snapshot:integration].split())

    assert snapshot < integration
    for document_type in (
        "feature request",
        "issue",
        "design",
        "implementation plan",
    ):
        assert document_type in snapshot_contract
    for required_text in (
        "plain `git reset`",
        "git diff --cached --name-only",
        "git add -A <document-path>",
        "prints exactly `<document-path>` and no other path",
        "group-commits-msg.template.md",
        "wac.bat",
        "gcba.bat",
        "--root-a-commit --non-interactive",
        "do not present another commit menu",
        "Leave any unrelated working-tree changes unstaged",
    ):
        assert required_text in snapshot_contract


def test_review_instruction_leaves_the_consolidation_hint() -> None:
    """review-ask-questions hints the consolidation step on the reviewed document."""
    assert "consolidate-then-review-ask-questions" in _read("review-ask-questions.md")


def test_splitting_instructions_present_the_multi_choice() -> None:
    """process-draft and split-and-define list the next steps with a free-text entry."""
    for name in ("process-draft.md", "split-and-define.md"):
        content = _read(name)
        assert "write-requirement" in content
        assert "Type something else" in content


def test_umbrella_child_stops_for_review_before_requirement_handoff() -> None:
    """Only an approved umbrella-derived child may reach write-requirement."""
    content = _read("process-draft.md")
    umbrella = content.split("## Umbrella continuation mode", 1)[1].split(
        "## User choices for process-draft",
        1,
    )[0]
    initial_handoff = content.split(
        "## Step 8 for process-draft, hand off to the next instruction",
        1,
    )[1].split("## Design decisions for process-draft", 1)[0]
    umbrella = " ".join(umbrella.split())

    _assert_contains_all(
        umbrella,
        (
            "stop for human review",
            "Do not run `pw skill`, enter Step 8",
            "only an explicit `Go ahead`",
            "update only the focused child draft",
            "Write this source as an actual Markdown file",
            "verify that it is a real file",
            "git status --short -- <child-path>",
            "path-scoped status is clean",
            "Recovery exception",
            "truthful, material focused-draft change",
            "lead with the exact path-scoped Git status entry",
            "review the file itself",
            "conversation copy is only a convenience",
            "never surround it with Markdown backticks",
            "cause an `umbrella does not exist` error",
        ),
    )
    _assert_contains_all(
        content,
        (
            "produce a real Markdown child draft on disk",
            "new working-tree result of the current continuation",
            "Merely finding an unchanged tracked file",
        ),
    )
    assert "run the selection straight away" in initial_handoff


def test_process_draft_docs_keep_the_on_disk_umbrella_child_contract() -> None:
    """README and Diataxis pages keep the file-backed child review gate."""
    root = steps.llm_shared_dir()
    pages = {
        "README": (root / "README.md").read_text(encoding="utf-8"),
        "tutorial": (
            root / "wiki/tutorials/02-from-draft-to-settled-requirement.md"
        ).read_text(encoding="utf-8"),
        "how-to": (root / "wiki/how-to/split-a-mixed-draft.md").read_text(
            encoding="utf-8",
        ),
        "reference": (root / "wiki/reference/artifact-files.md").read_text(
            encoding="utf-8",
        ),
    }

    assert "writes and verifies the canonical focused child Markdown file" in pages[
        "README"
    ]
    assert "Review the file itself" in pages["tutorial"]
    assert "Review that file itself" in pages["how-to"]
    assert "required on-disk artifact" in pages["reference"]
    for content in pages.values():
        assert "preview" in content


def test_process_draft_offers_and_passes_every_docs_layout() -> None:
    """The initial draft flow records one of the four supported effort paths."""
    content = _read("process-draft.md")
    for path in ("docs/", "docs/vX.Y/", "docs/vX.Y.Z/", "docs/vX.Y/vX.Y.Z/"):
        assert path in content
    for layout in ("flat", "minor", "version", "minor-version"):
        assert f"--docs-layout {layout}" in content
    assert "documentation-layout choice" in content
    assert "five setup menus" in content


def test_group_commits_carries_the_commit_gate_multi_choice() -> None:
    """group-commits-msg presents the commit-gate multi-choice via pw skill."""
    content = _read("group-commits-msg.md")
    assert "pw skill --after-commit" in content
    assert "Go ahead, and implement step" in content
    assert "Go ahead, and prepare-release" in content
    assert "Never present the contextual option as only the printed command" in content
    assert "Type something else" in content


def _assert_release_wiki_step(instruction: str) -> None:
    """Check the prepare-release instruction's wiki-audit contract."""
    content = " ".join(instruction.split())
    assert "### Step 8 — Audit and update existing Diataxis wiki roots" in instruction
    assert "`<PRJ_DIR>/wiki`" in instruction
    assert "`<PRJ_DIR>/docs/wiki`" in instruction
    assert "complete release range `<last_tag>..HEAD`" in content
    assert "`review-and-update-project-docs`" in instruction
    assert "`group-commits-msg`" in instruction
    assert instruction.index("### Step 8") < instruction.index(
        "### Step 10 — Prepare the release notes",
    )


def _assert_release_wiki_review_contract(review: str) -> None:
    """Check the project-doc review contract used by release preparation."""
    content = " ".join(review.split())
    assert "`wiki/` or `docs/wiki/`" in content
    assert "If a Git range was provided" in review
    assert "explanation, tutorials, how-to guides, then reference" in content
    assert "a.prepare-release.active" in review


def _assert_release_wiki_files(root: Path) -> None:
    """Check Diataxis coverage and host entry-point coverage."""
    pages = (
        root / "wiki" / "explanation" / "why-documents-before-code.md",
        root / "wiki" / "tutorials" / "05-prepare-a-release-from-develop.md",
        root / "wiki" / "how-to" / "prepare-a-release.md",
        root / "wiki" / "reference" / "skills-catalog.md",
    )
    for path in pages:
        assert "wiki" in path.read_text(encoding="utf-8").lower()

    entry_points = (
        root / ".github" / "skills" / "prepare-release" / "SKILL.md",
        root / ".claude" / "skills" / "prepare-release" / "SKILL.md",
        root / ".agents" / "llm-shared" / "skills" / "prepare-release" / "SKILL.md",
        root / ".agent" / "workflows" / "prepare-release.md",
    )
    for path in entry_points:
        assert "wiki" in path.read_text(encoding="utf-8").lower()


def test_prepare_release_audits_existing_diataxis_wikis_before_notes() -> None:
    """Release prep covers every release commit before generating its notes."""
    root = steps.llm_shared_dir()
    instruction = _read("prepare-release.md")
    review = _read("review-and-update-project-docs.md")
    _assert_release_wiki_step(instruction)
    _assert_release_wiki_review_contract(review)
    _assert_release_wiki_files(root)


def test_prepare_release_stops_historical_feature_merges() -> None:
    """prepare-release does not reword a non-tip historical feature merge."""
    content = " ".join(_read("prepare-release.md").split())
    assert "branch tip already released" in content
    assert "feature is already integrated into `<target_branch>`" in content
    assert "cannot safely invent or reword a non-tip historical merge" in content


def test_prepare_release_uses_read_only_planner_and_merge_tree_preview() -> None:
    """prepare-release plans topology and conflicts before changing branches."""
    content = " ".join(_read("prepare-release.md").split())
    assert "prepare_release_plan.bat" in content
    assert "--no-conflict-preview" in content
    assert "--feature-base" in content
    assert "git merge-tree --write-tree -z --name-only --messages" in content
    assert "isolated temporary object directory" in content
    assert "first conflict because a human resolution changes" in content


def test_prepare_release_planner_uses_package_directories() -> None:
    """Planner sources and tests live in matching prepare_release packages."""
    root = steps.llm_shared_dir()
    source = root / "tools" / "prepare_release"
    tests = root / "tests" / "unit" / "tools" / "prepare_release"
    launcher = (root / "bin" / "prepare_release_plan.bat").read_text(
        encoding="utf-8",
    )

    assert (source / "__init__.py").is_file()
    assert (source / "prepare_release_plan.py").is_file()
    assert (tests / "__init__.py").is_file()
    assert (tests / "test_prepare_release_plan_workflow.py").is_file()
    assert "tools\\prepare_release\\prepare_release_plan.py" in launcher


def test_prepare_release_treats_later_versions_as_notes() -> None:
    """The invocation branch selects content while the lowest new version labels it."""
    content = " ".join(_read("prepare-release.md").split())
    assert "Choose the lowest version strictly greater than the last" in content
    assert "feature-request" in content
    assert "forward-looking notes for later efforts" in content
    assert "Drafts never trigger Step 2" in content
    assert "selecting the invocation branch selects its content" in content
    assert "Later-version plans are forward-looking notes" in content


def test_prepare_release_owns_planner_invocation_end_to_end() -> None:
    """The caller supplies context; the skill runs every planner command itself."""
    content = " ".join(_read("prepare-release.md").split())
    assert "The user only has to invoke `$llm-shared:prepare-release`" in content
    assert "Never ask the user to run `prepare_release_plan.bat`" in content
    assert "Do not depend on the user's current shell having `LLM_SHARED_DIR`" in content
    assert "automatically rerun the release planner" in content

    root = steps.llm_shared_dir()
    tutorial = (root / "wiki/tutorials/05-prepare-a-release-from-develop.md").read_text(
        encoding="utf-8",
    )
    how_to = (root / "wiki/how-to/prepare-a-release.md").read_text(encoding="utf-8")
    for page in (tutorial, how_to):
        assert "$llm-shared:prepare-release" in page
        assert "$env:LLM_SHARED_DIR" not in page


def test_prepare_release_gives_actionable_unsupported_path_handoffs() -> None:
    """Unsupported planner paths stop safely with commands and a re-entry point."""
    content = " ".join(_read("prepare-release.md").split())

    assert "Unsupported planner handoffs" in content
    assert "Every unsupported result must end with an actionable block" in content
    assert "git revert -m 1 <excluded_merge_oid>" in content
    assert "git cherry-pick --abort" in content
    assert "Re-enter prepare-release" in content
    assert "no combined planner run can model an evolving main" in content
    assert "do not claim that the planner accepts an explicit commit list" in content
    assert "Independently count `main..<integration_branch>`" in content


def test_prepare_release_wiki_marks_planner_capability_boundaries() -> None:
    """Diátaxis pages distinguish supported paths from actionable stops."""
    root = steps.llm_shared_dir()
    scenarios = (root / "wiki/reference/prepare-release-scenarios.md").read_text(
        encoding="utf-8",
    )
    planner = (root / "wiki/reference/prepare-release-planner.md").read_text(
        encoding="utf-8",
    )
    how_to = (root / "wiki/how-to/prepare-a-release.md").read_text(encoding="utf-8")
    tutorial = (root / "wiki/tutorials/05-prepare-a-release-from-develop.md").read_text(
        encoding="utf-8",
    )

    assert "Required unsupported-path output" in scenarios
    assert "Supported and unsupported planning paths" in planner
    assert "git switch -c prepare-release/exclude-<topic>" in how_to
    assert "git switch -c prepare-release/<feature>-clean main" in how_to
    assert "The `main..develop` scope must contain at least one commit" in tutorial


def test_prepare_release_names_and_applies_gitworkflow_precisely() -> None:
    """Topic graduation is gitworkflow, while bulk develop promotion is explicit."""
    content = " ".join(_read("prepare-release.md").split())
    assert "Workflow model: gitworkflow topic graduation" in content
    assert 'Do not call this generic "Git flow"' in content
    assert "oldest integration branch it may eventually enter" in content
    assert "all-topics-ready bulk exception" in content
    assert "GitFlow-style recovery shortcut, not normal gitworkflow" in content
    assert "does not preview this revert path" in content
    assert "https://git-scm.com/docs/gitworkflows" in content
    assert "https://github.com/rocketraman/gitworkflow" in content


def test_gitworkflow_explanation_links_the_primary_context() -> None:
    """The explanation distinguishes the named workflow and cites its context."""
    explanation = (
        steps.llm_shared_dir() / "wiki/explanation/why-release-branch-roles-matter.md"
    ).read_text(encoding="utf-8")
    assert "The model is gitworkflow, one word" in explanation
    assert "This is not a spelling variant of generic" in explanation
    assert "https://stackoverflow.com/a/44470240/6309" in explanation
    assert "https://stackoverflow.com/a/216228/6309" in explanation
    assert "https://stackoverflow.com/a/53405887/6309" in explanation


def test_llm_shared_pwiki_alias_serves_wiki_and_loads_before_guard() -> None:
    """The llm-shared console always gets a pwiki macro for the root wiki."""
    root = steps.llm_shared_dir()
    senv = (root / "senv.bat").read_text(encoding="utf-8")
    doskeys = (root / "senv.doskey").read_text(encoding="utf-8")
    macro_load = 'doskey /MACROFILE="%LLM_SHARED_DIR%\\senv.doskey"'
    guard = "if defined NO_MORE_SENV_%PRJ_DIR_NAME% ( goto:eof )"

    assert senv.index(macro_load) < senv.index(guard)
    assert 'pwiki=python "%LLM_SHARED_DIR%\\tools\\serve_docs\\serve_docs.py"' in doskeys
    assert '"%PRJ_DIR%\\wiki"' in doskeys
    assert '"%PRJ_DIR%\\docs\\wiki"' not in doskeys


def test_llm_shared_senv_delegates_project_venv_setup_to_switchpy() -> None:
    """The project shell leaves venv repair and dependency sync to switchpy."""
    root = steps.llm_shared_dir()
    senv = (root / "senv.bat").read_text(encoding="utf-8")

    assert "call switchpy %PYTHON_VERSION% local" in senv
    assert "call:ensure_project_venv_scaffold" not in senv
    assert "call:ensure_project_venv_tools" not in senv
    assert "repair_venv_scaffold.py" not in senv
    assert "-m ensurepip" not in senv
    assert 'uv.exe" sync' not in senv


def test_llm_shared_senv_reinitializes_project_scoped_aliases() -> None:
    """A console inherited from another repository cannot keep its aliases."""
    root = steps.llm_shared_dir()
    senv = (root / "senv.bat").read_text(encoding="utf-8")

    clear = 'set "INIT_DONE="'
    initialize = 'call "%~dp0tools\\init.bat" %*'

    assert senv.index(clear) < senv.index(initialize)


def test_llm_shared_senv_bootstraps_shared_sensitive_rules_file() -> None:
    """A new workstation gets an empty shared rules file before hook setup."""
    root = steps.llm_shared_dir()
    senv = (root / "senv.bat").read_text(encoding="utf-8")

    shared_rules = (
        'set "SENSITIVE_SHARED_RULES='
        '%PROG%\\git\\a.sensitive.replacements.local.txt"'
    )
    bootstrap = 'if not exist "%SENSITIVE_SHARED_RULES%" ('
    create_empty = 'type NUL > "%SENSITIVE_SHARED_RULES%"'
    install_hooks = (
        'python "%PRJ_DIR%\\tools\\sensitive_history\\install_hooks.py"'
    )

    assert senv.index(shared_rules) < senv.index(bootstrap)
    assert senv.index(bootstrap) < senv.index(create_empty)
    assert senv.index(create_empty) < senv.index(install_hooks)


def test_sensitive_history_scanner_has_package_launcher_and_alias() -> None:
    """The audit skill and interactive shell share one stable scanner launcher."""
    root = steps.llm_shared_dir()
    source = root / "tools" / "sensitive_history"
    tests = root / "tests" / "unit" / "tools" / "sensitive_history"
    launcher = (root / "bin" / "sensitive_history_scan.bat").read_text(
        encoding="utf-8",
    )
    doskeys = (root / "senv.doskey").read_text(encoding="utf-8")
    instruction = _read("sanitize-git-history.md")

    assert (source / "__init__.py").is_file()
    assert (source / "history_scan.py").is_file()
    assert (source / "sensitive_history_scan.py").is_file()
    assert (tests / "test_history_scan.py").is_file()
    assert "tools\\sensitive_history\\sensitive_history_scan.py" in launcher
    assert 'shscan="%LLM_SHARED_DIR%\\bin\\sensitive_history_scan.bat"' in doskeys
    assert "sensitive_history_scan.bat" in instruction
    assert "automatically" in instruction


def test_git_history_diagrams_have_package_launcher_alias_and_docs() -> None:
    """Diagram sources, tests, launcher, alias, assets, and Diátaxis set stay together."""
    root = steps.llm_shared_dir()
    source = root / "tools" / "git_history_diagrams"
    tests = root / "tests" / "unit" / "tools" / "git_history_diagrams"
    launcher = (root / "bin" / "git_history_diagrams.bat").read_text(
        encoding="utf-8",
    )
    doskeys = (root / "senv.doskey").read_text(encoding="utf-8")

    assert (source / "generate_git_history_diagrams.py").is_file()
    assert (source / "scenarios.py").is_file()
    assert (source / "svg_renderer.py").is_file()
    assert (tests / "test_git_history_diagrams.py").is_file()
    assert r"tools\git_history_diagrams\generate_git_history_diagrams.py" in launcher
    assert r'ghdiag="%LLM_SHARED_DIR%\bin\git_history_diagrams.bat"' in doskeys
    assert (
        len(list((root / "wiki" / "assets" / "prepare-release").glob("*.svg")))
        == _EXPECTED_DIAGRAM_COUNT
    )
    for page in (
        "wiki/explanation/why-git-history-diagrams-use-explicit-arrows.md",
        "wiki/tutorials/07-generate-git-history-diagrams.md",
        "wiki/how-to/update-git-history-diagrams.md",
        "wiki/reference/git-history-diagram-generator.md",
    ):
        content = (root / page).read_text(encoding="utf-8")
        assert ".svg" in content


def test_wiki_leads_with_workflow_and_keeps_diataxis_order() -> None:
    """The wiki foregrounds self-review while retaining predictable navigation."""
    root = steps.llm_shared_dir()
    home = (root / "wiki" / "README.md").read_text(encoding="utf-8")
    headings = (
        "## 💡 Explanation",
        "## 🎓 Tutorials",
        "## 🧭 How-to guides",
        "## 📖 Reference",
    )
    required_phrases = (
        "AI-assisted development with review and reset loops",
        "must review what it has just generated",
        "groundhog reset loop",
        "100% by default",
        "statistical outlier",
        "`Why:`",
        "`What:`",
        "The release phase is equally complete",
        "Anthropic Claude Code",
        "OpenAI ChatGPT Codex",
        "Google Gemini Antigravity",
        "GitHub Copilot",
    )

    assert all(phrase in home for phrase in required_phrases)
    assert [home.index(heading) for heading in headings] == sorted(
        home.index(heading) for heading in headings
    )


def test_wiki_server_mounts_the_linked_presentation_and_orders_navigation() -> None:
    """The home deck URL is mounted and the sidebar follows Diátaxis order."""
    root = steps.llm_shared_dir()
    home = (root / "wiki" / "README.md").read_text(encoding="utf-8")
    config = (root / "wiki" / "serve_docs.ini").read_text(encoding="utf-8")
    server = (root / "tools" / "serve_docs" / "serve_docs.py").read_text(
        encoding="utf-8",
    )

    assert "../docs/llm-shared_presentation.html#solution-workflow-phases" in home
    assert "../docs/llm-shared_presentation.html" in config
    assert "../docs/llm-shared_logo.png" in config
    assert 'DIATAXIS_SECTION_ORDER = ("explanation", "tutorials", "how-to", "reference")' in server


def test_sensitive_history_reference_shows_both_input_file_formats() -> None:
    """Scanner reference gives neutral, runnable terms and rules examples."""
    root = steps.llm_shared_dir()
    content = (root / "wiki" / "reference" / "sensitive-history-scan.md").read_text(
        encoding="utf-8",
    )

    assert "### Example terms file" in content
    assert "shscan --terms-file a.sensitive.terms.local.txt" in content
    assert "### Example replacement-rules file" in content
    assert "shscan --rules a.sensitive.replacements.example.txt" in content
    assert "literal:example-project-name==>public-project" in content
    assert "regex:(?i)example[._-]internal==>public-name" in content


@pytest.fixture(scope="session")
def diataxis_page_texts() -> tuple[str, ...]:
    """Read every Diataxis page outside the measured test-call phase."""
    root = steps.llm_shared_dir() / "wiki"
    return tuple(
        page.read_text(encoding="utf-8")
        for section in ("explanation", "tutorials", "how-to", "reference")
        for page in (root / section).glob("*.md")
    )


def test_every_diataxis_page_states_its_invocation_model(
    diataxis_page_texts: tuple[str, ...],
) -> None:
    """Each page says whether a human or the AI normally invokes its subject."""
    assert all("## Invocation model" in content for content in diataxis_page_texts)


def test_wiki_logos_match_the_home_page_width() -> None:
    """Every theme logo uses the same explicit width as the wiki home page."""
    root = steps.llm_shared_dir()
    lines = (
        line
        for page in (root / "wiki").rglob("*.md")
        for line in page.read_text(encoding="utf-8").splitlines()
    )
    logo_lines = [line for line in lines if "<img" in line and "logo-llm-shared" in line]
    assert all('width="200"' in line and 'height="' not in line for line in logo_lines)


def test_run_pw_note_documents_the_launcher() -> None:
    """run-pw.md references the command rules and the launcher, not the bare alias."""
    content = _read("run-pw.md")
    assert "run_commands.md" in content
    assert "prompt_workflow.bat" in content
    assert "C:\\Users\\" not in content


def test_run_commands_documents_python_script_invocation() -> None:
    """run_commands.md gives the guard-clearing shape for direct Python scripts."""
    content = (steps.llm_shared_dir() / "rules" / "run_commands.md").read_text(
        encoding="utf-8",
    )
    assert "Python scripts use wrappers" in content
    assert "set NO_MORE_SENV_%PRJ_DIR_NAME%=& senv.bat && python" in content


def test_merge_reword_skill_covers_all_llms_and_shared_targets() -> None:
    """All four hosts discover the reword rule for develop and main merges."""
    root = steps.llm_shared_dir()
    trigger = "feature merge into develop or any merge into main"
    entry_points = (
        root / ".github" / "skills" / "update-merge-commit-msg" / "SKILL.md",
        root / ".claude" / "skills" / "update-merge-commit-msg" / "SKILL.md",
        root
        / ".agents"
        / "llm-shared"
        / "skills"
        / "update-merge-commit-msg"
        / "SKILL.md",
        root / ".agent" / "workflows" / "update-merge-commit-msg.md",
    )

    assert all(trigger in path.read_text(encoding="utf-8") for path in entry_points)

    instruction = _read("update-merge-commit-msg.md")
    assert "merging a feature branch into `develop` for integration" in instruction
    assert "promotion branch into `main`" in instruction
    assert "Do not push the target branch" in instruction


def test_wiki_explains_and_specifies_shared_target_rewording() -> None:
    """The wiki gives the rationale and exact contract for merge rewording."""
    wiki = steps.llm_shared_dir() / "wiki"
    explanation = (
        wiki / "explanation" / "why-release-branch-roles-matter.md"
    ).read_text(encoding="utf-8")
    reference = (wiki / "reference" / "skills-catalog.md").read_text(
        encoding="utf-8",
    )
    explanation_words = " ".join(explanation.split())
    reference_words = " ".join(reference.split())

    assert "The merge says why this topic entered its integration branch" in explanation
    assert "Rewording happens before the table checkpoint" in explanation_words
    assert "feature merge into its integration branch" in reference_words
    assert "any no-fast-forward merge into `main`" in reference_words
    assert "current commit" in reference_words
    assert "history-repair plan" in reference_words


# eof
