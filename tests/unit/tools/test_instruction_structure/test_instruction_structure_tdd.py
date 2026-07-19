"""Structural check that the workflow instructions carry their handoff, hint, or list.

Step 5 of docs/plan.v0.9.0.handoff_automation.md guards the markdown sections
added in Steps 4 and 5: the writing and consolidation instructions carry a
``## Handoff`` that runs ``pw skill``, the review instruction leaves the
consolidation hint, and the splitting instructions present a multi-choice list
with a free-text entry. The check runs on every walk, so a later edit that drops
one fails fast (Q06).
"""

from __future__ import annotations

from tools import prompt_workflow_steps as steps

_INSTRUCTIONS = steps.llm_shared_dir() / "instructions"
_EXPECTED_DIAGRAM_COUNT = 4


def _read(name: str) -> str:
    """Return the text of an instruction file."""
    return (_INSTRUCTIONS / name).read_text(encoding="utf-8")


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


def test_review_instruction_leaves_the_consolidation_hint() -> None:
    """review-ask-questions hints the consolidation step on the reviewed document."""
    assert "consolidate-then-review-ask-questions" in _read("review-ask-questions.md")


def test_splitting_instructions_present_the_multi_choice() -> None:
    """process-draft and split-and-define list the next steps with a free-text entry."""
    for name in ("process-draft.md", "split-and-define.md"):
        content = _read(name)
        assert "write-requirement" in content
        assert "Type something else" in content


def test_group_commits_carries_the_commit_gate_multi_choice() -> None:
    """group-commits-msg presents the commit-gate multi-choice via pw skill."""
    content = _read("group-commits-msg.md")
    assert "pw skill --after-commit" in content
    assert "Go ahead, and implement step" in content
    assert "Go ahead, and prepare-release" in content
    assert "Never present the contextual option as only the printed command" in content
    assert "Type something else" in content


def test_prepare_release_distinguishes_branch_roles() -> None:
    """prepare-release preserves integration history and isolates feature commits."""
    content = " ".join(_read("prepare-release.md").split())
    assert "On-main release" in content
    assert "Integration release" in content
    assert "Feature release" in content
    assert "Never rebase a published, long-lived integration branch" in content
    assert 'rebase --onto main "<feature_base>" "<promotion_branch>"' in content
    assert "do not blindly use the oldest entry" in content
    assert "Never move or rewrite `<feature_branch>` itself" in content
    assert 'There is no feature-mode "merge stale anyway" path' in content
    assert 'merge --no-ff "<source_branch>"' in content


def test_prepare_release_stops_features_already_contained_by_main() -> None:
    """prepare-release does not attempt an empty replay of an integrated feature."""
    content = " ".join(_read("prepare-release.md").split())
    assert "branch tip already released" in content
    assert "feature-only merge can no longer select it" in content
    assert "Never silently convert the invocation to an on-main release" in content


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


def test_prepare_release_documents_default_develop_variant() -> None:
    """The local variant rebases topics for develop and releases from main."""
    content = " ".join(_read("prepare-release.md").split())
    assert "published long-lived hosting default" in content
    assert "rebase the feature onto current `develop`" in content
    assert "A feature may also go directly to main" in content
    assert "be picked twice with `--no-ff`" in content


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


def test_every_diataxis_page_states_its_invocation_model() -> None:
    """Each page says whether a human or the AI normally invokes its subject."""
    root = steps.llm_shared_dir() / "wiki"
    pages = (
        page
        for section in ("explanation", "tutorials", "how-to", "reference")
        for page in (root / section).glob("*.md")
    )

    assert all("## Invocation model" in page.read_text(encoding="utf-8") for page in pages)


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


def test_codex_plugin_packages_every_instruction() -> None:
    """Every shared instruction has a matching, self-contained Codex skill."""
    root = steps.llm_shared_dir()
    plugin = root / ".agents" / "llm-shared"
    instruction_names = {path.name for path in _INSTRUCTIONS.glob("*.md")}
    expected_skill_names = {
        name.removesuffix(".md").replace("_", "-") for name in instruction_names
    }
    packaged_skill_names = {
        path.name for path in (plugin / "skills").iterdir() if path.is_dir()
    }

    assert packaged_skill_names == expected_skill_names
    for instruction_name in instruction_names:
        skill_name = instruction_name.removesuffix(".md").replace("_", "-")
        skill = (plugin / "skills" / skill_name / "SKILL.md").read_text(
            encoding="utf-8",
        )
        packaged = plugin / "instructions" / instruction_name

        assert f"[Instruction](../../instructions/{instruction_name})" in skill
        assert packaged.read_bytes() == (_INSTRUCTIONS / instruction_name).read_bytes()


def test_pw_running_instructions_link_to_the_run_pw_note() -> None:
    """Each instruction that runs a pw command points at run-pw.md."""
    for name in (
        "write-requirement.md",
        "write-design.md",
        "write-plans.md",
        "consolidate-then-review-ask-questions.md",
        "process-draft.md",
        "group-commits-msg.md",
        "implement-step.md",
        "implement-missing-step.md",
        "implementation-check.md",
    ):
        assert "run-pw.md" in _read(name)


def test_question_skills_show_the_three_column_table() -> None:
    """Review and consolidate present open questions as a Q0x / Title / Recommended table."""
    for name in ("review-ask-questions.md", "consolidate-then-review-ask-questions.md"):
        assert "| Q0x | Title | Recommended Answer |" in _read(name)


def test_question_skills_use_the_oqm_wrapper() -> None:
    """Review and consolidate use oqm.bat instead of direct Python fallback."""
    for name in ("review-ask-questions.md", "consolidate-then-review-ask-questions.md"):
        content = _read(name)
        assert "run_commands.md" in content
        assert "oqm.bat" in content
        assert "python <LLM_SHARED_DIR>\\tools\\open_questions_md.py" not in content


def test_oqm_wrapper_clears_the_project_senv_guard() -> None:
    """oqm.bat clears the project guard before calling senv.bat."""
    content = (steps.llm_shared_dir() / "bin" / "oqm.bat").read_text(
        encoding="utf-8",
    )
    assert "NO_MORE_SENV_!LLM_SHARED_PRJ_DIR_NAME!=" in content
    assert "%PRJ_DIR%\\senv.bat" in content
    assert "open_questions_md.py" in content


def test_python_tool_instructions_use_wrappers() -> None:
    """Instructions should avoid direct Python script calls when wrappers exist."""
    for name in (
        "group-commits-msg.md",
        "update-merge-commit-msg.md",
        "git-history-report.md",
    ):
        content = _read(name)
        assert "run_commands.md" in content
        assert 'python "%LLM_SHARED_DIR%\\tools\\' not in content
        assert "python <llm-shared>/tools/" not in content


# eof
