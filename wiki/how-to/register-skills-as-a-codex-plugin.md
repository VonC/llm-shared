# How to register the skills as a ChatGPT Codex plugin

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Plugin registration and thread restart are human-owned host configuration.
An AI can update the package and run the requested CLI refresh, but the user
chooses the marketplace and starts the new Codex thread that loads it.

🤖 Goal: make all 24 llm-shared skills available in every ChatGPT Codex
session as `$llm-shared:<skill>`, without copying a single file out of
the clone.

## 📦 What the repository already ships

The plugin package lives under `.agents/llm-shared/` in the clone:

```txt
.agents/llm-shared/
├─ .codex-plugin/plugin.json     manifest; its "skills": "./skills/" line drives discovery
├─ skills/<skill>/SKILL.md       24 wrappers, UTF-8 without BOM, name + description frontmatter only
└─ instructions/                 bundled copy of the bodies, so the package stands alone
```

It sits one level below `.agents/` on purpose: a package directly in
`.agents/skills` would also be picked up as raw project skills and every
skill would appear twice.

## 🧩 Keep every instruction in the package

For every root `instructions\<name>.md`, the plugin package must contain:

- `skills\<hyphenated-name>\SKILL.md`, with valid `name` and `description`
  frontmatter,
- `instructions\<name>.md`, as an exact bundled copy of the root instruction,
- `[Instruction](../../instructions/<name>.md)` in the wrapper, so the link
  resolves inside an installed plugin cache.

Do not point a wrapper upward into the source checkout. That may work in the
clone but fails after Codex copies the plugin into its versioned cache.

The structural regression test checks the complete one-to-one contract:

```cmd
python -m pytest tests\unit\tools\test_instruction_structure\test_instruction_structure_tdd.py --no-cov -q
```

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

   The list must show `personal` with your profile as its root. If it already
   does, do not add the marketplace again.

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

## 🔄 Pick up additions and instruction changes

The junction keeps the marketplace source synchronized with the clone, but
Codex still caches the installed plugin by manifest version. After changing an
instruction, wrapper, or bundled body:

1. Validate the complete package.
2. Replace the manifest cachebuster with the plugin-creator helper.
3. Reinstall from the existing personal marketplace.
4. Start a new thread.

```cmd
python "<plugin-creator-skill>\scripts\validate_plugin.py" "<clone>\.agents\llm-shared"
python "<plugin-creator-skill>\scripts\update_plugin_cachebuster.py" "<clone>\.agents\llm-shared"
codex plugin add llm-shared@personal
```

Keep the semantic version prefix and replace only its `+codex.<cachebuster>`
suffix. Reusing the old manifest version can leave new skills absent from the
next thread even though the marketplace source is correct.

## ✅ Check the registration took

Outside any session, render the model-visible prompt:

```cmd
codex debug prompt-input
```

It must list the plugin-prefixed skills (`llm-shared:process-draft`,
`llm-shared:group-commits-msg`, ...) with no skipped-skill or
missing-frontmatter warning. Inside a fresh session, `$llm-` completes to
the same names, and asking "list your available skills from llm-shared"
returns the 24 entries, including `llm-shared:sanitize-git-history` and
`llm-shared:isolate-logos`.

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
- **A copied personal plugin source** — a directory copy becomes stale when
  the clone gains a skill; keep `%USERPROFILE%\plugins\llm-shared` as the
  junction from step 2.
- **A wrapper link outside the plugin root** — links with too many `..`
  segments may resolve only in the clone and break in the installed cache.
- **Expecting a resumed thread to refresh** — reinstalling changes future
  thread registries only; open a new thread to see a new skill.

## 🧪 The lighter route for groundhog only

`ghog init` needs none of this: it writes the project `AGENTS.md`
section and the `~/.codex/prompts/groundhog.md` custom prompt, which is
enough to trigger the fixing loop from Codex — see
[Register groundhog in a project](register-groundhog-in-a-project.md).
The plugin route is for the whole skill set.

Related: [Plug llm-shared into your project](../tutorials/01-plug-llm-shared-into-your-project.md),
[Pick up skill edits without restarting](pick-up-skill-edits-without-restarting.md),
[One body, many agents](../explanation/one-body-many-agents.md).
