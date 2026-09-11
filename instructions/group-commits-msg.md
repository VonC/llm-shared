# Group commits message

Your goal is to group files listed in the prompt, from least to most dependent and, for each group, to write a conventional commit message, all in a file named `a.commit` at the **project root** — the `%PRJ_DIR%\a.commit` path (`PRJ_DIR` is the project root the prompt operates on), and never an `a.commit` placed under `docs/` or any other subfolder.

The context that can inform how you will group those files can be:

- any `.md` files in your context, as well as previous prompts in your current conversation, can provide additional context for grouping files.
- `git diff --name-only --cached` to get the list of staged files, and then group them based on their dependencies.
- `git diff --cached` to get the recent evolutions done for those files listed in the prompt.

## Workflow for grouping commits

For every llm-shared utility below, resolve `<LLM_SHARED_DIR>` as the absolute
parent of the `instructions` folder that contains this canonical file. Use the
resolved full path from PowerShell; do not rely on `%LLM_SHARED_DIR%`,
`$env:LLM_SHARED_DIR`, or a guessed relative checkout. The shared launchers
self-locate and do not need an `senv.bat` pre-call.

1. Get the list of files to group.

   Group every staged file the command lists, including changes of outside origin (a concurrent edit, a tool-written file, an earlier unrelated tweak) that a `git add -A` staged alongside your own: none is skipped for not being yours, each is ranked by its own dependencies and placed in a fitting group.

   Execute the following sequence of bat commands:

   ```bat
   cd "%PRJ_DIR%"
   git diff --cached --name-only
   ```

2. Get the changes done on those files.

   Execute the following sequence of bat commands:

   ```bat
   cd "%PRJ_DIR%"
   git diff --cached
   ```

3. Group files based on their dependencies and the context you have (previous prompts, `.md` files in your context, and the changes done on those files).

   A validation plan that newly marks a step `Yes` is a trailing documentation
   group. Do not fold it into the feature, fix, test, or performance group that
   made the code change. Put it last, after all behavior and test groups, with
   the exact title `docs(<topic>): record step <n> validation`. The readiness
   checker and final batch validation enforce that exact `pw` marker for the
   group containing the completed validation plan. A different plan or
   completion-only document may instead use
   `docs(<topic>): record step <n> completion`.

4. For each group, write a conventional commit message. Each group must follow the template provided in [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md). See the next section for more details on how to write the commit message. The title `# Grouping commits by topic` from the template must be added only once, for the first group, and not for the following groups.

5. Replace the content of the project-root `a.commit` (`%PRJ_DIR%\a.commit`, never a copy under `docs/` or another subfolder) with the generated groups and commit messages. Each group must be separated by an empty line in `a.commit`.

6. Format `a.commit` with the `wrap_commit` tool so each fenced `log` block fits within 80 characters and follows the inline-backtick rules. This keeps the file canonically formatted before the user reviews it.

   Before running the formatting command, read [`../rules/run_commands.md`](../rules/run_commands.md).

   Execute the following sequence of bat commands (default parameters: 80-character width, ```log fence delimiters, backtick pass on):

   ```powershell
   Set-Location -LiteralPath "<PRJ_DIR>"
   & "<LLM_SHARED_DIR>\bin\wac.bat"
   ```

   The tool rewrites `a.commit` in place. An exit status of 0 means the file is now canonically formatted (whether or not changes were applied); a non-zero status means the file is missing or unreadable and the underlying issue must be fixed before proceeding.

7. After `a.commit` is formatted and every intended path is staged, run the
   focused read-only readiness checker, `commit-plan-check.bat --format json`,
   from the project root through its full path:

   ```powershell
   & "<LLM_SHARED_DIR>\commit-plan-check.bat" --format json
   ```

   Status `0` means the plan is mechanically ready, but it does not authorize a
   commit. Continue only to the existing human menu or an already-authorized
   batch continuation. Status `3` means the plan is not ready: use every
   returned diagnostic to repair `a.commit` or staged membership, format the
   plan again, and rerun the checker before presenting choices. Status `2`
   means the command could not make a trustworthy decision: stop and report
   the operational diagnostic without presenting choices or running a batch.

   This earlier read-only gate does not replace final batch validation. The
   final batch validates the same plan again before its first mutation.

8. Once `a.commit` is generated, formatted, and mechanically ready, display it for user review (the author may edit it first), then read [`../rules/command_prefix_char.md`](../rules/command_prefix_char.md), read [`../rules/interactive_menu.md`](../rules/interactive_menu.md) and present the go-ahead choices. Run `pw skill --after-commit <x>` (via its launcher, see [`run-pw.md`](run-pw.md)) from the project root, where `<x>` is the plan step this commit completes (the "step XXXX" of the cycle), to get the contextual next command. This lookup is read-only and exists only to build the commit-gate labels; it is not the go-ahead and it does not replace the commit. The concrete choices are:

   - `Go ahead` — commit, then stop.
   - the contextual option, when a development effort is in flight — `Go ahead, and implement step <next>` for the next plan step, or `Go ahead, and prepare-release` once every step is committed. A standalone call with no plan prints nothing and exits non-zero, so omit this row when there is no contextual option.
   - `Type something else` — let the author provide a different command or correction before committing.

   Plain `Go ahead` commits and then stops; the contextual option commits and, only after the commit succeeds, runs `<command-prefix>implement-step` on the next step or `<command-prefix>prepare-release`, with the prefix selected by `command_prefix_char.md`. Never present the contextual option as only the printed command, such as `$prepare-release`; the choice label must start with `Go ahead, and ...` so the user can see that selecting it commits first.

9. When the user selects a go-ahead entry, validate the `a.commit` file, and if it is not valid, fix any issue reported by the validation.

   To validate the `a.commit` file, you can use the following sequence of bat commands:

   ```powershell
   Set-Location -LiteralPath "<PRJ_DIR>"
   & "<LLM_SHARED_DIR>\bin\gcba.bat" --root-a-commit
   ```

   An exit status of 0 means the `a.commit` file is valid, while a non-zero exit status means there is an issue with the `a.commit` file that needs to be fixed.

   If the file is valid, there is nothing more to do: `git_batch_commit.py` will have proceeded automatically to create one commit per group, with the corresponding commit message.

   Do not manually replay the groups with `git restore --staged`, `git add`,
   or `git commit` after a go-ahead. The approved go-ahead path is exactly the
   batch commit tool above; bypassing it skips the parser/validator contract
   and risks committing a different grouping than the reviewed `a.commit`.

## Authorized code-review continuation

This is a dedicated entry used only after the code-review requestor observes
`owning-action-pending` and verifies `owning_action_authorized: true`. Run
`pw code-review-commit`; it runs the canonical batch entry with
`--root-a-commit` and `--non-interactive`, reusing the root `a.commit`
validation and batch execution above for the reviewed commit plan first. In
this route, do not present the commit choices again and do not issue private
Git commit commands.

After that reviewed batch succeeds, the continuation checks the complete
repository status. When changes remain, it runs repository-wide `git add -A`,
retains the durable owning authorization, and reports that residual grouping is
required. Generate, format, and check a replacement root `a.commit` for every
staged residual path through Steps 1 through 7 above. The existing `Commit`
choice already authorizes this bounded cleanup batch, so do not present the Step 8
menu. Then run `pw code-review-commit --residual`; it executes the replacement
plan through the same `--root-a-commit --non-interactive` batch entry.

The residual continuation must run `git status --porcelain` after that batch
and require empty output. Only a successful batch followed by a clean working
tree may call the exchange `complete`. On a batch failure or a non-clean final
status, authorization remains pending for repair and replay; do not run
`pw skill`, begin another step, or claim completion.

## Authorized consolidation continuation

Use this continuation only when
`consolidate-then-review-ask-questions.md` delegates its settled
post-consolidation working tree after the human selected `Consolidate`, or
directly invoked that consolidation skill. The consolidation instruction owns
the repository-wide staging scope, the final clean-tree check, and any bounded
recovery pass.

Generate, format, and check `a.commit` through Steps 1 through 7 above for every
staged path. The existing consolidation choice already authorizes the generated
commits, so do not present the Step 8 menu or request another go-ahead. Run
`& "<LLM_SHARED_DIR>\bin\gcba.bat" --root-a-commit --non-interactive` exactly
once, then return control to the consolidation instruction. Never issue private
Git commit commands or claim a clean tree here: consolidation verifies
`git status --porcelain` and decides whether its one recovery pass is required.

## Commit message rules for groups

Each commit message must follow the template provided in [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md).

Be mindful of empty lines mentioned in the template:

- Add an empty line between the title and the Why section.
- Add an empty line between `Why:` and its section.
- Add an empty line between the reason and the "now" state within the `Why:` section.
- Add an empty line between the end of the `Why:` section and the `What:` section.
- Add an empty line between `What:` and its section.

Reminder, conventional commit means, the title must start with `<type>[optional scope]: description`, with 52 characters max.
Types other than `fix:` and `feat:` are `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.

- The title must not exceed 52 characters.
- The body and footer lines must not exceed 80 characters, and must not be indented, no prefix spaces.
  Make sure each line in the body and footer is wrapped at 80 characters or less, which means it must go up to 80 characters and then break to the next line without indentation.

Make sure the body includes two sections, 'Why' and 'What':

- in the 'Why' section, you must have two parts separated by an empty line: read the template for guidance.
- in the 'What' section, make a list of modifications, each line starting with a dash: read the template for guidance.

Do not use words listed in the "Blacklist of words to avoid in the response" of [`blacklist.md`](../rules/blacklist.md). The same applies for the What section.
