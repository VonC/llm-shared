# How to settle spelling before a commit

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The commit gates run these steps for you: `group-commits-msg` before its
go-ahead menu and the code review requestor before its `Commit` choice. Use
this guide directly to check files outside those gates, or to see what the
agent does at them.

📊 Goal: every new or modified Markdown file of a commit reports no unknown
word, with each finding either accepted in project settings or replaced.
On Windows, every original reported word presented for a decision also goes
into user settings, even when replaced. Source code is not spell-checked.

## 🧰 Before the first check

1. Nothing to set up on a machine with senv Node: the launcher finds Node
   (22.18 or later for cspell 10, else 20.18 or later for cspell 9) and puts
   it first on the `PATH` of its own runs. Only if it reports
   `cspell needs Node 20.18 or later`, install one through senv:

   ```cmd
   dwl_inst_ver node 22
   ```

2. The first check installs the pinned cspell into llm-shared's `venvs`
   folder by itself, which needs the npm registry once.

## 📋 Steps

1. List the Markdown files the commit adds or modifies:

   ```cmd
   git status --porcelain -- "*.md"
   ```

2. From the project root, check them in one call:

   ```powershell
   & "<LLM_SHARED_DIR>\bin\spellcheck.bat" check docs\v0.14.0\review.code.md wiki\README.md
   ```

   Exit `0` means no unknown word; finish any outstanding decisions and
   verification from earlier runs before treating the work as complete.
   Exit `1` prints a table:

   ```text
   | Word | Where | cSpell suggestions |
   | --- | --- | --- |
   | `collectreport` | `docs/v0.14.0/review.code.md:938:12` | collecteront |
   ```

3. Retain the original words and listed locations until all their decisions,
   edits and dictionary updates are verified, across later check runs too.
   For each word, the agent asks one question that names the word, quotes
   its line and lists its alternatives: add it to project settings or replace
   it with one of up to three alternatives, the cSpell suggestions that fit
   or a rewording of its own when none does. Choose one, or type your own
   replacement. On Windows, every choice also adds the original reported
   word to user `cSpell.userWords`: even a corrected misspelling becomes
   globally accepted for you.

4. Apply each chosen replacement at every listed location. Inspect the edited
   text directly before user dictionary additions can hide missed replacements
   from subsequent spell checks.

5. Add only the words approved for project addition in one call:

   ```powershell
   & "<LLM_SHARED_DIR>\bin\spellcheck.bat" add-words collectreport addfinalizer
   ```

   The words land at their place in the project's `cSpell.words`. The current
   launcher updates only that file. Stage `.vscode/settings.json` with the
   files that needed the words.

6. On Windows, edit `%APPDATA%\Code\User\settings.json` to add every original
   reported word from the retained findings, including those replaced, to
   `cSpell.userWords`, preserving the existing settings and comments. Use the
   environment variable to resolve the path, never an expanded profile path;
   in PowerShell use `$env:APPDATA`. Follow the
   [user settings procedure](../../rules/spelling.md#keep-original-reported-words-in-windows-user-settings).

   Keep the exact original spelling and case, without duplicates; do not
   substitute the replacement word for the original finding. Read back user
   settings for every original word and project settings for every
   project-approved word independently, even when one list already contains
   it. If an update fails, report the failure and any partial change before
   continuing. Keep user settings local.

7. Restage the project changes and run step 2 again until it exits `0`.
   Resolve any new findings through the same procedure. A clean check does
   not replace direct verification of earlier text edits and dictionary
   membership.

## 🚫 What not to do

- Do not skip a word because it sits in backticks or a code block.
- Do not add an ignore pattern or a `cspell:ignore` comment.
- Do not leave a project-approved word only in user settings: the project
  list must also contain it so other clones share it.
- Do not skip the Windows user settings update when a word was rephrased.

For the reasons behind the check, see
[Why the spell check mirrors VS Code](../explanation/why-the-spell-check-mirrors-vs-code.md);
for every option and exit code, see
[Spell check command](../reference/spell-check-command.md).
