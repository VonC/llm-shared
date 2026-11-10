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
alike: either it is added to the project's `.vscode/settings.json` and, on
Windows, the user's `%APPDATA%\Code\User\settings.json`, or it is replaced in
the text. The user decides which, word by word:

1. Show the table the check printed.
2. Ask one question per word, in groups of four with a blocking picker when
   the host offers one (see [`interactive_menu.md`](interactive_menu.md)).
   Each question names the word, quotes the line it appears in, and gives
   every alternative its own option: `Add to settings.json`, then
   `Replace with <alternative>` for each alternative, at least one and up to
   three. Take the alternatives from the cSpell suggestions that fit the
   sentence; when none fits, propose your own, such as the correct spelling,
   a plain English word or a rewording of the phrase. Never offer
   `Add to settings.json` as the only option. Put the option you recommend
   first and say why. Explain that the add option applies to both the project
   and user settings on Windows. The user can type another replacement.
3. Add the accepted words to the project in one call, from the project root:

   ```powershell
   & "<LLM_SHARED_DIR>\bin\spellcheck.bat" add-words <word> [<word> ...]
   ```

   It inserts them into `cSpell.words` at their place in its order and
   changes nothing else. The current launcher updates only the project file.
   On Windows, also add those same approved words to `cSpell.userWords` in
   `%APPDATA%\Code\User\settings.json`, following the next section. The
   addition is complete only after both files contain the words. The
   `.vscode/settings.json` change belongs to the commit: stage it with the
   files that needed the words. The user settings file stays local.
4. Replace the other words at every listed location, restage, and run the
   check again until it exits `0`.

Never present the commit choice while an unknown word remains, and never
make a word disappear another way: no `cSpell.ignoreRegExpList` pattern, no
`cspell:ignore` or `cspell:disable` comment, and no choice made on the user's
behalf. Edit user settings only to add the words approved for the project.

## Keep approved project additions in Windows user settings

Every approved addition to the project's `cSpell.words` must also be present
in `cSpell.userWords` in `%APPDATA%\Code\User\settings.json`. This applies whether
the project addition is made through the launcher or another edit. Add each
approved word to each list independently: a word already present in the
project may still be missing from user settings, or the reverse. Keep the
exact spelling and case, and do not add duplicates or copy the whole project
dictionary into user settings.

Always express the user settings path with `%APPDATA%` in instructions and
documentation, never an expanded absolute profile path. Resolve it at runtime;
in PowerShell use `$env:APPDATA`, for example:

```powershell
Join-Path -Path $env:APPDATA -ChildPath 'Code\User\settings.json'
```

Read the user settings before editing. Insert only the approved missing words
into `cSpell.userWords` at their sorted positions. Do not put these additions
in the user file's `cSpell.words`. Preserve other words, comments,
unrelated settings, indentation, encoding and line endings. Create a missing
file or list when needed. Never replace the user file with the project file,
and never copy the user file into the repository or stage it.

Read back both lists to verify every approved word is present before treating
the addition as complete; a clean spell check alone does not prove this,
because the check merges both settings levels. If APPDATA is missing or either
file cannot be read or updated, report the failure and any partial change,
and stop before the commit choice. Do not substitute a guessed profile path
or silently skip the user settings update.
