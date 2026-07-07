# How to register the skills as a ChatGPT Codex plugin

<img src="../assets/logo-llm-shared-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Goal: make all 22 llm-shared skills available in every ChatGPT Codex
session as `$llm-shared:<skill>`, without copying a single file out of
the clone.

## 📦 What the repository already ships

The plugin package lives under `.agents/llm-shared/` in the clone:

```txt
.agents/llm-shared/
├─ .codex-plugin/plugin.json     manifest; its "skills": "./skills/" line drives discovery
├─ skills/<skill>/SKILL.md       22 wrappers, UTF-8 without BOM, name + description frontmatter only
└─ instructions/                 bundled copy of the bodies, so the package stands alone
```

It sits one level below `.agents/` on purpose: a package directly in
`.agents/skills` would also be picked up as raw project skills and every
skill would appear twice.

## 📋 Wiring it on a machine

1. Create the personal marketplace file at
   `%USERPROFILE%\.agents\plugins\marketplace.json`, with the marketplace
   named `personal` and one plugin entry:

   ```json
   {
     "name": "llm-shared",
     "source": { "source": "local", "path": "./plugins/llm-shared" },
     "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
     "category": "Productivity"
   }
   ```

2. Point `%USERPROFILE%\plugins\llm-shared` at the clone with a junction
   — a link, not a copy, so the skills stay live with the repository:

   ```cmd
   mklink /J "%USERPROFILE%\plugins\llm-shared" "C:\path\to\llm-shared\.agents\llm-shared"
   ```

3. Register the marketplace root — the folder that contains both
   `.agents\plugins\marketplace.json` and `plugins\llm-shared`, so the
   user profile itself, not the plugins folder:

   ```cmd
   codex plugin marketplace add %USERPROFILE%
   codex plugin marketplace list
   ```

   The list must show `personal` with your profile as its root.

4. Install and enable the plugin:

   ```cmd
   codex plugin list
   codex plugin add llm-shared@personal
   ```

   The add writes `[plugins."llm-shared@personal"] enabled = true` into
   `%USERPROFILE%\.codex\config.toml` and copies the package into the
   plugin cache under `.codex\plugins\cache\personal\llm-shared\`.

5. Start a new Codex session. The skill list is injected when a thread
   is created, so a resumed thread never gains the new skills.

## ✅ Check the registration took

Outside any session, render the model-visible prompt:

```cmd
codex debug prompt-input
```

It must list the plugin-prefixed skills (`llm-shared:process-draft`,
`llm-shared:group-commits-msg`, ...) with no skipped-skill or
missing-frontmatter warning. Inside a fresh session, `$llm-` completes to
the same names, and asking "list your available skills from llm-shared"
returns the 22 entries.

## 🪙 What the metadata costs per session

The upfront price is the registry only — names, descriptions and source
paths, in the order of 1.3k to 1.8k tokens per session. The `SKILL.md`
bodies and the instruction files are read only when a skill actually
runs.

## ⚠️ Pitfalls this recipe already avoids

- **A wrapper folder around the plugin root** — the installed root must
  directly contain `.codex-plugin\plugin.json` and `skills\`; one extra
  nesting level and no skill is ever injected.
- **A UTF-8 BOM in SKILL.md** — Codex then misses the `---` at byte 0
  and reports missing frontmatter; the shipped wrappers are BOM-less,
  keep them that way when editing on Windows.
- **Underscores or extra frontmatter keys** — Codex skill names refuse
  `_` (the wrapper for `fix_slow_test.md` is named `fix-slow-test`), and
  the validator rejects keys beyond `name`, `description` and a
  `metadata` mapping.
- **Duplicate direct installs** — copying the wrappers into
  `%USERPROFILE%\.codex\skills` as well makes every skill appear twice;
  the plugin route alone is enough.

## 🧪 The lighter route for groundhog only

`ghog init` needs none of this: it writes the project `AGENTS.md`
section and the `~/.codex/prompts/groundhog.md` custom prompt, which is
enough to trigger the fixing loop from Codex — see
[Register groundhog in a project](register-groundhog-in-a-project.md).
The plugin route is for the whole skill set.

Related: [Plug llm-shared into your project](../tutorials/01-plug-llm-shared-into-your-project.md),
[Pick up skill edits without restarting](pick-up-skill-edits-without-restarting.md),
[One body, many agents](../explanation/one-body-many-agents.md).
