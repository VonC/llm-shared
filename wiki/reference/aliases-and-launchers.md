# Aliases and bin launchers

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 The Doskey aliases loaded by `senv.bat` plus the `bin\*.bat` launchers
they wrap. The aliases exist only in an interactive `cmd`; the launchers
work from any shell — each self-locates the llm-shared folder and its
bundled Python from its own path.

## Invocation model

Aliases are primarily human shortcuts in an interactive shell. AI workflows use
the full launchers so behavior does not depend on session-local alias state.
Call either form directly for an intentional standalone operation or to diagnose
the corresponding launcher.

## 🧰 Workflow aliases

| Alias | Runs | Purpose |
| --- | --- | --- |
| `pw` | `bin\prompt_workflow.bat` | next-step prompt through menu, `handoff`, or `skill`; stateless path lookup through `document` |
| `gcmp` | `bin\gcmp.bat` | write `a.diff`, clear `a.commit`, build the `/group-commits-msg` prompt to the clipboard |
| `gcba` | `bin\gcba.bat --root-a-commit` | validate `a.commit`, then replay the grouped commits |
| `grmc` | `scripts\update-merge-commit-msg\git-reword-merge.sh` | rewrite the current merge commit from `a.commit` |
| `gp` | `git push` | push shortcut |
| `brel` | `tools\dev_workflow\t_build.bat rel` | release build: drop `-SNAPSHOT`, commit, tag `vX.Y.Z` |

## Codex plugin maintenance

| Alias | Runs | Purpose |
| --- | --- | --- |
| `llmup` | `bin\update_llm_shared_plugin.bat` | validate `.agents\llm-shared` and its cache-relative redirects, replace its manifest cachebuster, reinstall `llm-shared@personal`, verify the installed cache copy, and print its installed row |

`llmup` requires an interactive `cmd` initialized by `senv.bat`. The launcher
uses `uv run --isolated --no-project --with PyYAML` for plugin validation, so
the active project's environment is not changed. It locates the standalone
Codex executable first and falls back to `codex.exe` on `PATH`. A successful
run still needs a new Codex thread before the refreshed skill registry appears.

## 🧪 Test aliases (all backed by ghog)

| Alias | Runs | Purpose |
| --- | --- | --- |
| `ghog` | `bin\ghog.bat` | the groundhog reset tool; `ghog day` walks check, affected, full |
| `ptr` | `ghog full` | reset `.testmondata`, full suite with the coverage gate |
| `pta` | `ghog affected` | testmon-selected tests with appended coverage |
| `ptanc` | `ghog affected --no-cov` | the fast focused pass, coverage off |
| `pts` | `ghog single <test files>` | named files in focus, compared with the last full-run baseline |
| `c` | `bin\python_check.bat` | the compile, lint and big-file gate on its own |
| `ruffc` | `ruff check` | lint right after code generation |
| `covg` | `bin\covg.bat` | map uncovered lines to functions, build a test-writing prompt |

## 📋 Clipboard aliases

| Alias | Runs | Purpose |
| --- | --- | --- |
| `tth` | `bin\tth.bat` | trim an exported Claude or Codex conversation to the ask, the opening, and the closing answer of every turn, back to the clipboard |

`tth` reads the clipboard when it gets no file argument, and always publishes
its result to the clipboard. It always drops every line before the first prompt
stamped with today's date, and takes an optional `YYYYMMDD` date to match a
second day, so `tth 20260903` trims the clipboard and `tth export.md 20260903`
trims a file; the alias forwards every argument. See
[the trim-thinking command reference](trim-thinking-command.md).

## ⚙️ Other public launchers

| Launcher | Wraps | Purpose |
| --- | --- | --- |
| `wac.bat` | `tools\wrap_commit.py` | reflow and format a commit message (`--no-delimiters` for a single message) |
| `oqm.bat` | `tools\open_questions_md.py` | manage open-questions sections: `--create`, `--strip`, `--append` |
| `new_draft.bat` | `tools\new_draft.py` | rename a draft and create its effort branch or worktree |
| `ghd.bat` | `tools\git_history_dashboard\build.py` | build the commit-history dashboard |
| `sensitive_history_scan.bat` | `tools\sensitive_history\sensitive_history_scan.py` | report sensitive terms across commit, tag, path, and blob history |
| `git_history_diagrams.bat` | `tools\git_history_diagrams\generate_git_history_diagrams.py` | generate or check the prepare-release SVG histories |
| `mds.ps1` | `tools\serve_docs\serve_docs.py` | serve a markdown folder as a local website and open the browser (PowerShell so Ctrl-C stops it without cmd's terminate-batch question) |
| `tth.bat` | `tools\trim_thinking_cli.py` | trim an exported conversation from a file or the clipboard, result to the clipboard |
| `python_check.bat` | vulture, big-file check, `enforce_eof.py` | the check station of the walk |
| `python_check_types.bat` | type checking | the typing gate |
| `commit-plan-check.bat` | `tools\commit_plan_check.py` | read-only readiness verdict for the root `a.commit` against the staged set, `--format json` for machine use |
| `rvw_status.bat` | `tools\review_status_cli.py` | migration-aware schema-2 status for every active review without resuming it |
| `review_exchange.bat` | `tools\review_exchange_cli.py` | shared review state, publication, wait, confirmation, and recovery operations |
| `spec_review_request.bat` | specification request renderer | build a specification-review request and transcript summary |
| `spec_review_answer.bat` | specification answer renderer | build a specification-review answer and transcript summary |
| `code_review_request.bat` | code request renderer | capture the reviewed index and build a code-review request |
| `code_review_evidence.bat` | code evidence CLI | capture, compare, retain, and retire immutable review evidence |
| `code_review_answer.bat` | code answer renderer | validate evidence and build a code-review answer |

The `shscan` alias calls `sensitive_history_scan.bat --root "%PRJ_DIR%"`.
Reports written below the repository must use an ignored path such as
`a.sensitive.history-scan.local.md`.

The `ghdiag` alias calls `git_history_diagrams.bat`. Use `ghdiag --check` to
verify that committed history diagrams match their declarative scenarios.

## 📦 Dependency shortcuts

| Alias | Runs | Purpose |
| --- | --- | --- |
| `pcomp` | `tools\uv_run.py lock` | refresh `uv.lock`, cert-aware |
| `pupg` | `tools\uv_run.py lock --upgrade` | bump locked versions, cert-aware |
| `psync` | `tools\uv_run.py sync` | apply the lockfile, cert-aware |

`uv_run.py` picks a TLS strategy (corporate PEM via `SSL_CERT_FILE`, then
`--system-certs`, then default roots) and retries on certificate errors —
useful behind a corporate proxy; plain `uv` skips the retry path.

Related: [Independent review mode contract](independent-review-mode-contract.md),
[Run pw from any shell](../how-to/run-pw-from-any-shell.md),
[ghog commands and exit codes](ghog-commands-and-exit-codes.md).
