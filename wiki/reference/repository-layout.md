# Repository layout

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Where everything lives in the llm-shared tree, and which agent reads
what.

## Invocation model

Repository layout is configuration, not a command. Humans install or register
the host entry points; AI agents then discover and read the shared bodies,
instructions, and tools automatically. Consult paths directly when maintaining
the integration or diagnosing discovery.

## LLM compatibility

This table describes the integrations shipped in the current tree. A supported
host integration does not imply that every auxiliary command has a native
adapter there. Canonical instructions remain available for explicit loading.

| LLM / host | Entry point | Coverage and limits |
| --- | --- | --- |
| OpenAI ChatGPT/Codex | `.agents/llm-shared/skills/<skill>/SKILL.md` and `.codex-plugin/plugin.json` | Supported plugin registration; commands use `$llm-shared:<skill>`; redirects resolve from the installed plugin layout |
| Anthropic Claude Code | `.claude/skills/<skill>/SKILL.md` | Supported skill discovery; includes humanizer and the family-specific review roles |
| Google Gemini through Antigravity | `.agent/workflows/<skill>.md` | Supported workflow registration through the host's workflow directory; applies to Antigravity, not every Gemini interface |
| GitHub Copilot | `.github/skills/`, `.github/prompts/`, `.github/agents/` | Supported skill, one-shot prompt, and agent entry points; command surfaces depend on the entry-point type |
| Grok | `.grok/commands/<command>.md` | Portable redirects cover shared instructions, one-shot prompts, humanizer, and compatibility aliases; native discovery and slash commands are unverified; review identity is `unknown` |
| Another host, including plain ChatGPT or Gemini chat | Canonical `instructions/` files supplied explicitly | No native integration implied; local execution requires the relevant filesystem, shell, and host capabilities |

For review-specific adapter coverage, use the
[host adapter matrix](independent-review-mode-contract.md#host-adapter-matrix).
For the composition of a skill and the meaning of scaffolding, see
[One body, many agents](../explanation/one-body-many-agents.md).
To integrate another host, follow
[Add scaffolding for another LLM](../how-to/add-an-llm-adapter.md).

## 🚪 Agent entry points

```txt
.github/                     GitHub Copilot discovery
├─ agents/                   agent definitions (split-large-file)
├─ copilot-instructions.md   redirect to rules/chat.md
├─ prompts/                  one-shot prompts (analyse, discuss, check-api*,
│                            fix-issue, extend-test-coverage, ...)
└─ skills/<skill>/SKILL.md   frontmatter + reference to instructions/<skill>.md
.claude/                     Claude Code discovery
├─ CLAUDE.md                 redirect to rules/chat.md
└─ skills/<skill>/SKILL.md   mirrors .github/skills/
AGENTS.md                    the Codex channel: run_commands pointer + groundhog section
.agents/llm-shared/          source-linked ChatGPT Codex plugin package
├─ .codex-plugin/plugin.json manifest; "skills": "./skills/" drives discovery
├─ skills/<skill>/SKILL.md   BOM-less wrappers with discovery metadata
└─ instructions/             compatibility redirects to root instructions/
.agent/workflows/<skill>.md  Google Antigravity workflow wrappers,
                             junctioned into projects, slash-invoked
.grok/commands/<command>.md  portable Grok redirects, explicitly loaded
```

Independent review adapters live in the Codex and Antigravity wrapper sets.
Claude carries the four family-specific requestor and reviewer skills but no
shared `review-requestor` wrapper. The exact host matrix is in the
[independent review mode contract](independent-review-mode-contract.md#host-adapter-matrix).

## 📚 Shared bodies and rules

```txt
instructions/                one canonical markdown body per shared skill
├─ status-session.md         inspect the checkpoint or latest recorded work
├─ pause-session.md          save the latest private session checkpoint
├─ resume-session.md         consume it once, or reread with --force
└─ prompts/                  canonical one-shot and humanizer bodies
rules/                       canonical shared rules, including chat and
                             LLM-specific adapter maintenance
templates/                   document skeletons the skills fill
```

Provider skill and workflow folders delegate to `instructions/`; another agent
can load the matching canonical body directly.

Grok adapters cover all shared commands, including the one-shot prompts;
automatic discovery is host-dependent and unverified. ChatGPT or Gemini
outside their coding hosts can be given the same canonical files explicitly.
Session prompt and usage-flag templates live in `templates/`; their generated
files stay in the consuming project's ignored review artifact home. See
[pause/resume usage](../how-to/pause-and-resume-a-session.md).

## ⚙️ Executable support

```txt
bin/                         self-locating .bat launchers: prompt_workflow (pw),
                             ghog, gcba, gcmp, wac, oqm, covg, ghd, tth,
                             new_draft, python_check, review_exchange, the
                             family review renderers, update_llm_shared_plugin,
                             plus bundled venvs/
tools/                       the Python behind the launchers:
├─ prompt_workflow*.py       pw: menu, handoff, skill modes
├─ review_exchange*.py       durable exchange state and transitions
├─ code_review*.py           immutable evidence and answer rendering
├─ git_batch_commit*.py      validate and replay a.commit
├─ new_draft*.py             rename a draft, branch or worktree
├─ open_questions_md.py      the oqm modes
├─ coverage_gap_functions*.py  covg
├─ wrap_commit*.py           wac
├─ trim_thinking*.py         tth: trim an exported conversation
├─ groundhog/                the ghog CLI: runner, gate, snapshot, durations
├─ git_history_dashboard/    the ghd builder
├─ git_history_diagrams/     deterministic prepare-release SVG histories
├─ prepare_release/          topology detection and merge-tree previews
├─ sensitive_history/        contextual commit, path, and blob scanner
├─ html_to_pptx/             presentation to native PPTX and PDF
├─ codex_plugin_package.py   Codex plugin validator, cachebuster, marketplace name
├─ codex_plugin_redirects.py  cache-relative plugin redirect validator
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

## Dependency environment

The project environment sets `UV_SYSTEM_CERTS=1` so direct uv commands use the
platform certificate store. Its Git lockfile filter keeps committed package
URLs public and restores configured mirror URLs in working copies. Filter
installation precedes environment synchronization, and an unchanged lockfile
can be refreshed through the filter; local lockfile edits are preserved.
The dependency set pins pip 26.2 for CVE-2026-13346.

## 🌍 What is generalized versus project-specific

The skills, rules, templates and tools are meant to be referenced from
other projects (multi-root workspace, `--add-dir`, or handed bodies). The
`docs\` folder shows the workflow applied to llm-shared itself: its own
drafts, requirements, designs and plans — worked examples of every
template.

Related: [Independent review mode contract](independent-review-mode-contract.md),
[Plug llm-shared into your project](../tutorials/01-plug-llm-shared-into-your-project.md),
[One body, many agents](../explanation/one-body-many-agents.md).
