# Why the spell check mirrors VS Code

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The commit gates run the check: `group-commits-msg` before its go-ahead menu,
and the code review requestor before its `Commit` choice. The AI runs it and
asks; the human decides, word by word, what is accepted and what is replaced.
Run it directly when a file needs checking outside a commit.

📊 The person who approves a commit reads its files in VS Code, where the
Code Spell Checker extension underlines every unknown word and lists it in the
Problems panel. An agent that commits without seeing that panel leaves those
findings for the next person to clean, and they reach the history first.

## 🪞 The same findings, without VS Code

The extension keeps its findings inside VS Code: no API or command line gives
the Problems panel to another program. It is built on `cspell-lib`, the engine
of the `cspell` command line from the same authors, so cspell reports the
same words once it receives the same settings. Those settings are what VS Code
merges for the extension:

- the user settings: the languages (`en,fr`) and the user's own words,
- the `.code-workspace` files of the checkout,
- the project's `.vscode/settings.json` words,
- the dictionary of each installed language extension, such as French.

`spellcheck.bat` rebuilds that merge into one temporary cspell configuration.
Leaving a level out changes the answer: without the user's words, a review
transcript that shows 8 problems in VS Code reports 57.

## 📄 Documentation, not source code

The check reads Markdown files only. Source code is full of library function
names that no dictionary holds and no reader would want spelled differently;
checking it would turn each commit question into a list of API names. The
tool drops any other file it is given.

## 🧭 Every word is settled, backticks or not

cSpell reads code spans and code blocks like any other text, so a pytest hook
name such as `collectreport` in backticks is reported too. No pattern skips
those spans: a word the reader sees underlined is either accepted into the
project's `.vscode/settings.json`, where every clone of the project shares it,
or replaced. The suggestions cSpell offers for code names are often useless
(`collecteront` for `collectreport`), which is why the user, not the agent,
picks between the two.

## 🐢 A pinned cspell on a recent Node

The check pins cspell 10, the major version of the extension's engine, and
installs it once in llm-shared's ignored `venvs` folder. It needs Node 22.18
or later, taken from the `PATH` or from the senv `%PRGS%\nodes\node<N>`
links, so a machine updates Node through senv like any other tool. Calling
`node.exe` directly, instead of `npx` or `switchnode`, keeps one check of a
commit's files to a few seconds.

To run the check, see
[Settle spelling before a commit](../how-to/settle-spelling-before-a-commit.md);
for its commands and exit codes, see
[Spell check command](../reference/spell-check-command.md).
