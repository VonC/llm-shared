# How to use the skills from Google Antigravity

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Goal: call the llm-shared skills from a Google Antigravity session
with the same `/write-design`-style syntax as the other hosts, while the
bodies stay mutualized under `instructions/`.

## Invocation model

The initial host wiring is a human setup action. Once the host can discover the
skills, the user invokes a top-level skill and the AI owns its internal commands
and handoffs. Return to these manual steps only to register a new project,
refresh the integration, or diagnose discovery.

## 📦 What the repository ships for Antigravity

Antigravity invokes workflows — markdown files under `.agent/workflows/`
— through the `/` menu of its agent input: typing `/write-design` makes
the agent read `.agent/workflows/write-design.md` and follow its steps.
The repository ships one such wrapper per skill, 22 in total, generated
from the same descriptions as the Codex wrappers. Each wrapper is three
steps: locate the shared `instructions/<skill>.md` body (workspace root,
sibling `../llm-shared` clone, or `llm-shared` submodule), read it in
full, follow it with the arguments given after the slash command.

So the syntax is not different: the same `/` prefix and the same skill
names as Claude Code, with `$` remaining the Codex spelling. The only
naming nuance is inherited from the Codex normalization: hyphens
everywhere, so `/prepare-release-notes` and `/fix-slow-test`.

## 📋 Wiring a project session

Antigravity documents workflow discovery from the workspace
`.agent/workflows/` folder only — files anywhere else are ignored, and
discovery across a second workspace root is not documented. The reliable
wiring is therefore a junction inside the project, still pointing at the
one clone:

```cmd
mklink /J "%CD%\.agent" "..\llm-shared\.agent"
```

or, when the project already has its own `.agent\` folder, junction only
the workflows subfolder (or link the wrapper files individually):

```cmd
mklink /J "%CD%\.agent\workflows" "..\llm-shared\.agent\workflows"
```

A junction is a link, not a copy: a `git pull` in the clone updates the
wrappers for every project at once. Add `.agent/` to the project's
`.gitignore` when the junction should stay a per-machine choice.

## ⌨️ Calling a skill

In the Antigravity agent panel, type `/` and pick the workflow, exactly
like a Claude Code slash command:

```txt
/write-requirement feature-request v0.10.0 progress-log
/groundhog
```

Two Antigravity-specific notes:

- workflows normally confirm terminal commands; a `// turbo` line above
  a step (or `// turbo-all` in the file) lets a trusted workflow run its
  commands unattended — the llm-shared wrappers ship without it, so the
  usual permission flow applies,
- Antigravity also reads `AGENTS.md` at the project root (since
  v1.20.3), so the `## groundhog` section that `ghog init` writes for
  Codex triggers the same fixing loop here, and project rules can live
  in `GEMINI.md` or `AGENTS.md` without duplication.

## 🧪 The skills format, version permitting

Antigravity also understands the Claude-style `SKILL.md` folder format —
skills are then matched from their description, not slash-invoked. The
discovery path has moved across releases (reported as `.agent/skills/`,
`<workspace>/.agents/skills/`, and `~/.gemini/config/skills/` at user
level), so llm-shared does not ship a dedicated copy for it: the
`.agent/workflows/` route above is the stable, documented one, and it
keeps the familiar slash syntax. If your Antigravity version reads
`<workspace>/.agents/skills/`, note that llm-shared deliberately keeps
that path empty — its Codex plugin lives one level down at
`.agents/llm-shared/` precisely so the same skills are never loaded
twice.

## ✅ Check the wiring

Open the project in Antigravity, type `/` in the agent input: the 22
llm-shared workflows appear in the dropdown. Run `/write-requirement`
with no arguments — the agent must answer by asking for the three
mandatory inputs (type, version, topic), proof that it read the shared
body and not just the wrapper.

## 🔗 Sources for the Antigravity behavior

Antigravity moves fast and its official documentation site renders
client-side; the statements above rest on these references, worth
re-checking when a new version changes the behavior:

- [Google Antigravity documentation](https://antigravity.google/docs) —
  the official entry point.
- [Antigravity workflows guide (agentpedia)](https://agentpedia.codes/blog/workflows)
  — the `.agent/workflows/` location, the frontmatter format, the `/`
  invocation, the "files anywhere else are ignored" rule, turbo mode.
- [Antigravity rules and AGENTS.md guide (agentpedia)](https://agentpedia.codes/blog/user-rules)
  — `GEMINI.md` and `AGENTS.md` locations, the v1.20.3 AGENTS.md
  support, `~/.gemini/` global rules.
- [Where to put your agent skills, updated for Antigravity (Google Cloud Community)](https://medium.com/google-cloud/confused-about-where-to-put-your-agent-skills-ea778f3c64f3)
  — the per-tool skills directories, including
  `<workspace>/.agents/skills/` and `~/.gemini/config/skills/`.
- [Antigravity agent workflow documentation (Mace Labs)](https://macelabs.com/google-antigravity-agent-workflow-documentation/)
  — workflow structure and slash execution.
- [Your Claude skills now work in Antigravity (Substack)](https://alexmcfarland.substack.com/p/your-claude-skills-now-work-in-antigravity)
  — the `SKILL.md` compatibility and the `.agent/skills/` variant.
- [Antigravity IDE skills guide (agensi.io)](https://www.agensi.io/learn/antigravity-ide-skills-guide)
  — the `.antigravity/skills/` variant and the Manager View role
  assignment.

Related: [Plug llm-shared into your project](../tutorials/01-plug-llm-shared-into-your-project.md),
[Register the skills as a Codex plugin](register-skills-as-a-codex-plugin.md),
[One body, many agents](../explanation/one-body-many-agents.md).
