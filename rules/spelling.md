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
replaced in the text. The user decides which, word by word:

1. Show the table the check printed.
2. Ask one question per word, in groups of four with a blocking picker when
   the host offers one (see [`interactive_menu.md`](interactive_menu.md)):
   `Add to settings.json`, then `Replace with <suggestion>` for up to three
   cSpell suggestions. The user can type another replacement.
3. Add the accepted words in one call, from the project root:

   ```powershell
   & "<LLM_SHARED_DIR>\bin\spellcheck.bat" add-words <word> [<word> ...]
   ```

   It inserts them into `cSpell.words` at their place in its order and
   changes nothing else. The `.vscode/settings.json` change belongs to the
   commit: stage it with the files that needed the words.
4. Replace the other words at every listed location, restage, and run the
   check again until it exits `0`.

Never present the commit choice while an unknown word remains, and never
make a word disappear another way: no `cSpell.ignoreRegExpList` pattern, no
`cspell:ignore` or `cspell:disable` comment, no edit to the user's own VS Code
settings, and no choice made on the user's behalf.
