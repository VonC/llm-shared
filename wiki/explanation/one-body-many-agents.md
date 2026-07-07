# One body, many agents

<img src="../assets/logo-llm-shared-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🤖 The same skill runs from GitHub Copilot, Claude Code and ChatGPT Codex
because the skill is not written three times. Each host gets a thin
pointer; the body lives once under `instructions/`.

## 🔗 The pointer pattern

`.github/skills/<skill>/SKILL.md` and `.claude/skills/<skill>/SKILL.md`
are frontmatter plus a reference to the same `instructions/<skill>.md`.
Codex is reached two ways: `AGENTS.md` sections and user-level prompts
(`ghog init` writes them for groundhog), or the whole set at once through
the self-contained plugin package under `.agents/llm-shared/`
([the how-to](../how-to/register-skills-as-a-codex-plugin.md)). A fourth
agent that understands none of these folders is simply handed the body
file as context — the slash command name and the file name are always
the same.

The clone always sits beside the projects that use it, never inside
them: no vendoring, no Git submodule required. Every discovery mechanism
— workspace folder, `--add-dir`, symlink, plugin junction — references
the one clone in place, which is why a single `git pull` updates the
skills everywhere.

## 🚪 The session references it, the project never does

The consequence is worth insisting on: nothing in your project ever
declares llm-shared. What references it is the **session** you open on
the project, through one of two mechanisms:

- **another root folder in your workspace** — the multi-root workspace
  holds your project root first and the llm-shared root second; that
  alone is enough for GitHub Copilot to discover the skills, prompts and
  agents and offer them to your project,
- **an additional directory on the session** — `/add-dir ..\llm-shared`
  in a running Claude Code session (or `claude --add-dir=../llm-shared`
  at launch), and the same `--add-dir` flag when launching Codex (see
  [openai/codex#2797](https://github.com/openai/codex/issues/2797#issuecomment-4555303886));
  the [Codex plugin route](../how-to/register-skills-as-a-codex-plugin.md)
  makes that reference permanent instead of per-session.

Close the session and your project is exactly as before: no config file
gained a path, no dependency was added, nothing to commit. The pairing
lives in how you open the tools, not in the repository — which is also
why two colleagues can point the same project at different llm-shared
checkouts without stepping on each other.

The benefit is not just less duplication: it is that a fix to a skill
lands everywhere at once, and that the behavior is testable as text — the
body either says it or it does not, whatever the host.

## 🧩 Host differences, isolated at the edges

What actually differs between hosts is kept out of the bodies:

- the command prefix (`/` versus `$`) is decided at print time by
  `pw skill` and `rules/command_prefix_char.md`,
- menus go through `rules/interactive_menu.md`, which picks the host's
  native choice mechanism and never assumes a TTY,
- shell mechanics go through `rules/run_commands.md`, and the `bin\*.bat`
  launchers self-locate so no host needs an environment first,
- sandbox quirks (Codex needing escalation for `senv.bat`) are documented
  in the one place that hits them.

## 📜 Why MIT fits this model

The repository exists to be copied into other projects — symlinked
skills, vendored folders, single body files handed as context. MIT puts
no condition on that beyond keeping the copyright notice, and it removes
a question copyleft would raise: whether the documents the skills
generate inside someone else's repository inherit the license. It also
matches code already in the tree (`tools\batcolors` ships MIT with the
same holder). The `senv_dev_workflow` build tooling stays under its own
terms — MIT covers llm-shared only.

## 🧱 The boundary with senv_dev_workflow

llm-shared owns the workflow: skills, rules, templates, launchers, the
release-notes side. The build side — `update-changelog.bat`,
`update-version.bat`, `t_build.bat` behind `brel` — comes from the
vendored `senv_dev_workflow` under `tools\dev_workflow\`. The two meet at
exactly one file: `version.txt`, which the notes skill writes and the
release build reads.

## 👉 Where the pieces are listed

- [Repository layout](../reference/repository-layout.md) for who reads
  which folder.
- [Plug llm-shared into your project](../tutorials/01-plug-llm-shared-into-your-project.md)
  for the three wiring options.
