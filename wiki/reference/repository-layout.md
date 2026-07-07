# Repository layout

<img src="../assets/logo-llm-shared-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Where everything lives in the llm-shared tree, and which agent reads
what.

## 🚪 Agent entry points

```txt
.github/                     GitHub Copilot discovery
├─ agents/                   agent definitions (split-large-file)
├─ copilot-instructions.md   shared chat and code-writing rules
├─ prompts/                  one-shot prompts (analyse, discuss, check-api*,
│                            fix-issue, extend-test-coverage, ...)
└─ skills/<skill>/SKILL.md   frontmatter + reference to instructions/<skill>.md
.claude/                     Claude Code discovery
├─ CLAUDE.md                 shared chat and code-writing rules
└─ skills/<skill>/SKILL.md   mirrors .github/skills/
AGENTS.md                    the Codex channel: run_commands pointer + groundhog section
.agents/llm-shared/          self-contained ChatGPT Codex plugin package
├─ .codex-plugin/plugin.json manifest; "skills": "./skills/" drives discovery
├─ skills/<skill>/SKILL.md   22 BOM-less wrappers (name + description only)
└─ instructions/             bundled copy of the bodies
.agent/workflows/<skill>.md  22 Google Antigravity workflow wrappers,
                             junctioned into projects, slash-invoked
```

## 📚 Shared bodies and rules

```txt
instructions/                one markdown body per skill — the single source
rules/                       blacklist, markdown, preserve_code, run_commands,
                             command_prefix_char, interactive_menu
templates/                   document skeletons the skills fill
```

Both skill folders delegate to `instructions/`; a third agent is handed
the matching body file directly.

## ⚙️ Executable support

```txt
bin/                         self-locating .bat launchers: prompt_workflow (pw),
                             ghog, gcba, gcmp, wac, oqm, covg, ghd, new_draft,
                             python_check, plus the bundled venvs/
tools/                       the Python behind the launchers:
├─ prompt_workflow*.py       pw: menu, handoff, skill modes
├─ git_batch_commit*.py      validate and replay a.commit
├─ new_draft*.py             rename a draft, branch or worktree
├─ open_questions_md.py      the oqm modes
├─ coverage_gap_functions*.py  covg
├─ wrap_commit*.py           wac
├─ groundhog/                the ghog CLI: runner, gate, snapshot, durations
├─ git_history_dashboard/    the ghd builder
├─ html_to_pptx/             presentation to native PPTX and PDF
├─ uv_run.py                 cert-aware uv launcher
├─ batcolors/                vendored batch coloring (submodule)
└─ dev_workflow/             vendored release tooling: update-changelog,
                             update-version, t_build (brel)
scripts/                     activity_report.sh, prepare_release_notes.sh,
                             update-merge-commit-msg/*.sh
```

## 📖 Documentation and meta

```txt
README.md                    the workflow at a glance
DEVELOPMENT.md               per-phase detail, diagrams, command reference
GROUNDHOG.md                 the full groundhog manual
docs/                        the effort documents of llm-shared itself, plus
                             the presentation (html, local.js, pptx, pdf)
wiki/                        this documentation
tests/                       the pytest suite of the tools
senv.bat, senv.doskey        local shell setup and aliases
version.txt, CHANGELOG.md    release state
pyproject.toml, uv.lock      dependencies, managed with uv
```

## 🌍 What is generalized versus project-specific

The skills, rules, templates and tools are meant to be referenced from
other projects (multi-root workspace, `--add-dir`, or handed bodies). The
`docs\` folder shows the workflow applied to llm-shared itself: its own
drafts, requirements, designs and plans — worked examples of every
template.

Related: [Plug llm-shared into your project](../tutorials/01-plug-llm-shared-into-your-project.md),
[One body, many agents](../explanation/one-body-many-agents.md).
