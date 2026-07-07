# Plug llm-shared into your project

<img src="../assets/logo-llm-shared-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🤖 In this tutorial you make the llm-shared skills available inside one of
your own projects, then confirm a slash command resolves. Allow 10 to 15
minutes. You need: a project under git, and one of GitHub Copilot in VS
Code, Claude Code (extension or CLI), or any LLM that reads workspace
files.

## 1. Clone llm-shared next to your projects

Put the repository as a sibling of the projects that will use it:

```cmd
cd /d C:\Users\you\git
git clone https://github.com/VonC/llm-shared
```

llm-shared is not a dependency of your project: nothing gets vendored
into your repository, and no Git submodule is needed. Every mechanism
below references this one clone in place, so one `git pull` here updates
the skills for every project at once. (A submodule layout also works —
`ghog init` computes its links for both — but the sibling clone is the
intended default.)

Using the shared skills needs no Python environment: they are plain
markdown. The bundled `bin\*.bat` launchers (`pw`, `ghog`, `gcba`, ...)
self-locate their own Python from the llm-shared `venvs\` folder.

## 2. Wire it into VS Code (Copilot or Claude extension)

Keep your real project as the first folder of the workspace and add
llm-shared as the second one. In the project's `.code-workspace` file:

```json
{
  "folders": [
    { "path": ".." },
    { "path": "../../llm-shared" }
  ]
}
```

Copilot Chat then discovers `.github/prompts/`, `.github/skills/` and
`.github/agents/` from both folders; the Claude Code extension picks up
`.claude/skills/` from the shared folder.

For an unattended run, set the Copilot "Chat Permissions Default" setting
to "Bypass Approval", and turn on the two `chat.notifyWindow*` settings so
the window signals when an answer lands.

## 3. Or wire it into Claude Code CLI

Claude Code reads `.claude/` from the current directory. Point it at the
shared folder with:

```bash
claude --add-dir=../llm-shared
```

To have the skills in every project without `--add-dir`, symlink them once:

```bash
ln -s "$(pwd)/.claude/skills" ~/.claude/skills
```

Run Claude in a non-blocking permission mode
(`claude --permission-mode acceptEdits`) so the workflow chains do not stop
on every file write.

## 4. Or register it as a ChatGPT Codex plugin

The clone ships a self-contained Codex plugin package under
`.agents/llm-shared/`. Wiring it takes a personal marketplace file, one
junction pointing at the clone, and three `codex plugin` commands; every
new Codex session then offers the 22 skills as `$llm-shared:<skill>`.
The full recipe with its pitfalls is in
[Register the skills as a Codex plugin](../how-to/register-skills-as-a-codex-plugin.md).
For one session only, `codex --add-dir ..\llm-shared` puts the clone in
scope without any registration; for groundhog alone, `ghog init` is
enough — no plugin machinery.

## 5. Or open it from Google Antigravity

Antigravity runs the skills as workflows: the clone ships one wrapper
per skill under `.agent/workflows/`, and a junction inside the project
(`mklink /J "%CD%\.agent" "..\llm-shared\.agent"`) makes them appear in
the `/` menu of the agent panel — same slash syntax, same names as
Claude Code. The recipe and the version caveats are in
[Use the skills from Google Antigravity](../how-to/use-the-skills-from-antigravity.md).

## 6. Or hand the bodies to any other LLM

Every slash command resolves to a plain markdown body under
[`instructions/`](../../instructions/), with the same name: `/write-design`
is `instructions/write-design.md`. Give the model that file as context,
plus the inputs the body expects (a draft, a requirement, a plan), and it
runs the same skill without knowing about `.github/` or `.claude/`.

## 7. Check that a skill resolves

In a chat session opened on your project, type `/write-requirement` (or ask
"write a requirement"). The agent should answer by asking for the three
mandatory inputs: type, version, topic. If it does, discovery works.

## 👉 Next steps after the setup

- [From draft note to settled requirement](02-from-draft-to-settled-requirement.md)
  to run the first phase of the workflow.
- [One body, many agents](../explanation/one-body-many-agents.md) for why
  the same skill text serves three different agents.
