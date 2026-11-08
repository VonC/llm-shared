# Spell check command reference

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📊 `bin\spellcheck.bat` runs `tools\spell_check.py` with llm-shared's own
Python. It reports the words the VS Code Code Spell Checker extension shows,
without VS Code, and adds accepted words to a project's settings. The rule
that runs it before every commit question is
[`rules/spelling.md`](../../rules/spelling.md).

## Invocation model

The commit gates call it: `group-commits-msg` and the code review requestor.
Call it directly from a project root to check any file.

## ⌨️ Commands

| Command | Effect |
| --- | --- |
| `spellcheck.bat check [--root DIR] [--format markdown\|json] FILE...` | Spell-check the Markdown files among `FILE...`, given relative to the root (default: the current folder); any other file is dropped, and with none left nothing runs |
| `spellcheck.bat add-words [--root DIR] WORD...` | Insert the words into the `cSpell.words` list of `DIR\.vscode\settings.json` |

`--format json` prints a list of `{"word", "locations", "suggestions"}`
objects instead of the Markdown table.

## 🔢 Exit codes

| Exit | `check` | `add-words` |
| --- | --- | --- |
| `0` | No unknown word | Words added, or already listed |
| `1` | Unknown words listed on stdout | Not used |
| `2` | Operational error on stderr | Unreadable settings or an empty word |

## ⚙️ Settings the check merges

| Level | Source | Keys read |
| --- | --- | --- |
| User | `%APPDATA%\Code\User\settings.json` | every `cSpell.*` key below |
| Workspace | each `<root>\.vscode\*.code-workspace` file, its `settings` object | same |
| Folder | `<root>\.vscode\settings.json` | same |
| Language extensions | `%USERPROFILE%\.vscode\extensions\streetsidesoftware.code-spell-checker-<language>-<version>\static\cspell-ext.json`, newest version of each | imported as a whole |

The lists `words`, `userWords`, `flagWords`, `ignoreWords`, `ignorePaths` and
`ignoreRegExpList` are joined across levels. The values `language`,
`allowCompoundWords`, `caseSensitive` and `minWordLength` come from the most
specific level that sets them. The settings files may hold comments and
trailing commas.

## 🧩 Runtime

| Item | Value |
| --- | --- |
| cspell | `10.4.1` on a Node 22.18 or later, else `9.8.0` on a Node 20.18 or later; installed on first use into `<LLM_SHARED_DIR>\venvs\cspell_<version>` with the npm of the chosen Node |
| Node | `node` from the `PATH` first, then `%PRGS%\nodes\node<N>\node.exe`, highest `N` first; the first that runs cspell 10, else the first that runs cspell 9; put first on the `PATH` of npm and cspell |
| Report | cspell's JSON reporter, with up to five suggestions per word, preferred ones first |
| Temporary file | the merged configuration, written to the system temporary folder and removed after the run |

## ✍️ `add-words` layout

Each new word is inserted before the first listed word that sorts after it,
ignoring accents and case, with a lowercase word before its capitalized twin
(`rescope` before `Rescope`). The list keeps its indentation and line endings;
a file without `cSpell.words` gets the key last, and a missing file is
created.
