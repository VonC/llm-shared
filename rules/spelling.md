# Spelling

## Spell-check every new or modified Markdown file before asking to commit

Before presenting any choice that commits (the go-ahead menu of a grouped
commit plan, a review convergence gate, or any other confirmation that leads
to a commit), spell-check every Markdown file the commit would add or modify,
and every modified Markdown file the same workflow commits later, such as a
review transcript kept unstaged for a residual commit. Source code and other
files are never spell-checked. List the files with
`git status --porcelain -- "*.md"` rather than from memory, leave deleted files
out, and check them in one call from the project root:

```powershell
& "<LLM_SHARED_DIR>\bin\spellcheck.bat" check <file.md> [<file.md> ...]
```

The check drops any non-Markdown file it is given.

The check reports the words the VS Code Code Spell Checker extension shows in
the Problems panel, without VS Code: it merges the `cSpell` settings of the
VS Code user settings, of the checkout's `.code-workspace` files and of its
`.vscode/settings.json`, adds the dictionary of each installed language
extension (such as the French one), and runs the cspell command line on Node.

| Exit | Meaning |
| --- | --- |
| `0` | No unknown word |
| `1` | A table lists each unknown word, its `file:line:column` locations and the cSpell suggestions |
| `2` | Operational error, printed on stderr: report it and stop |

The launcher sets up Node by itself: it takes `node` from the `PATH`, else the
newest senv `%PRGS%\nodes\node<N>` link, puts it first on the `PATH` of its
npm and cspell runs, and uses cspell 10.4.1 on a Node 22.18 or later, else
cspell 9.8.0 on a Node 20.18 or later. The first run installs that cspell into
llm-shared's `venvs` folder, which needs the npm registry once. Only a machine
without a Node 20.18 or later is an operational error: install one with the
senv tools (`dwl_inst_ver node 22`), never by hand.

## Settle every reported word with the user

Every reported word is settled, inside backticks, a code block or plain text
alike: either it is added to the project's `.vscode/settings.json`, or it is
replaced in the text. On Windows, both choices also add the original reported
word to `cSpell.userWords` in `%APPDATA%\Code\User\settings.json`, even when
the word is rephrased. The user decides the project resolution word by word:

1. Show the table the check printed. Retain each original reported word and
   all its listed locations until its decision, text edits and dictionary
   updates have been verified. Keep this record across later check runs.
2. Ask one question per word, in groups of four with a blocking picker when
   the host offers one (see [`interactive_menu.md`](interactive_menu.md)).
   Each question names the word, quotes the line it appears in, and gives
   every alternative its own option: `Add to project settings.json`, then
   `Replace with <alternative>` for each alternative, at least one and up to
   three. Take the alternatives from the cSpell suggestions that fit the
   sentence; when none fits, propose your own, such as the correct spelling,
   a plain English word or a rewording of the phrase. Never offer
   `Add to project settings.json` as the only option. Put the option you
   recommend first and say why. Explain that, on Windows, every choice adds
   the original reported word to user settings, so even a corrected
   misspelling becomes globally accepted for that user. The user can type
   another replacement.
3. Apply each chosen replacement at every listed location and inspect the
   edited text to verify it matches the decision. Do this before adding the
   original words to user settings, which would hide missed replacements
   from the next spell check.
4. Add only the words approved for project addition to the project in one
   call, from the project root:

   ```powershell
   & "<LLM_SHARED_DIR>\bin\spellcheck.bat" add-words <word> [<word> ...]
   ```

   It inserts them into `cSpell.words` at their place in its order and
   changes nothing else. The current launcher updates only the project file.
   The `.vscode/settings.json` change belongs to the commit: stage it with the
   files that needed the words. The user settings file stays local.
5. On Windows, add every original reported word from the retained findings
   to user `cSpell.userWords`, including those replaced in the text, following
   the next section. Do not substitute the replacement word for the original
   reported word. Verify user membership for every original word and project
   membership for every word approved for project addition independently.
6. Restage the project changes and run the check again until it exits `0`.
   Settle any new findings through the same procedure. A clean check does
   not close an earlier finding whose decision or updates remain unverified.

Never present the commit choice while an unknown word remains, and never
make a word disappear another way: no `cSpell.ignoreRegExpList` pattern, no
`cspell:ignore` or `cspell:disable` comment, and no choice made on the user's
behalf. Edit user settings only for these original reported words and approved
project additions, following the next section.

## Keep original reported words in Windows user settings

Every original reported word presented for an add-or-rephrase decision must
be present in `cSpell.userWords` in `%APPDATA%\Code\User\settings.json`, even
when the user chooses rephrasing and the original disappears from the text.
Only a project-add decision adds that word to project `cSpell.words`.

Every approved project addition must also be present in user settings,
whether added through the launcher or another edit. Check each required list
independently: a word already present in the project may still be missing
from user settings, or the reverse. Keep the exact original spelling and case,
and do not add duplicates or copy the whole project dictionary into user
settings. The replacement word does not stand in for the original finding.

Always express the user settings path with `%APPDATA%` in instructions and
documentation, never an expanded absolute profile path. Resolve it at runtime;
in PowerShell use `$env:APPDATA`, for example:

```powershell
Join-Path -Path $env:APPDATA -ChildPath 'Code\User\settings.json'
```

Read the user settings before editing. Insert only the required missing words
into `cSpell.userWords` at their sorted positions. Do not put these additions
in the user file's `cSpell.words`. Preserve other words, comments,
unrelated settings, indentation, encoding and line endings. Create a missing
file or list when needed. Never replace the user file with the project file,
and never copy the user file into the repository or stage it.

Read back user `cSpell.userWords` to verify every original reported word and
approved project addition is present. Read back project `cSpell.words` to
verify every project-approved word is present. Also verify the selected text
replacements directly; a clean spell check alone proves neither membership
nor completed replacements, because the check merges both settings levels.
If APPDATA is missing or a required file cannot be read or updated, report
the failure and any partial change, and stop before the commit choice. Do not
substitute a guessed profile path or silently skip the user settings update.
