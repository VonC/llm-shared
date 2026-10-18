# Set up the shared Python tools

Use this guide to run llm-shared's executable helpers or contribute to its
Python tools. Reading the Markdown skills alone requires no Python setup.
Dependencies are declared in [`pyproject.toml`](../../pyproject.toml) and pinned
in [`uv.lock`](../../uv.lock); the project uses the `dev` dependency group.

## Invocation model

A human prepares this environment once per machine and decides on dependency
upgrades. An AI working in the checkout may run the documented launchers,
checks and dependency reports when asked, following the
[shell execution policy](../../rules/run_commands.md); installing Python or uv
and changing `uv.lock` stay the user's decisions.

## Prepare the environment for the Windows launchers

Work from the llm-shared checkout. Install Python in the range declared by
`requires-python` in `pyproject.toml` (currently Python 3.13) and
[uv](https://docs.astral.sh/uv/). If uv is missing, bootstrap it with:

```text
python -m pip install uv
```

If you already use the repository's Windows environment tooling, run its
root `senv.bat` in your configured console. It expects the local `PRGS`
tool layout and `switchpy`; it selects a Python and prepares the project
environment. For agent tool shells, follow the authoritative
[shell execution policy](../../rules/run_commands.md).

For a manual setup without that console tooling, run these commands in
PowerShell from the llm-shared root:

```powershell
$env:UV_PROJECT_ENVIRONMENT = 'venvs/python_3.13'
uv sync --locked --python 3.13
```

Keep that environment selection when running subsequent uv commands in the
same checkout. The Windows launchers locate Python under
`venvs/python_3*/Scripts/python.exe`; a default `.venv` alone does not supply
that launcher layout. If several such environments exist, launchers select the
first name in descending directory-name order, so keep the selected environment
current. The helpers themselves run in place; llm-shared is not installed as
a Python package.

## Maintain the dependency lock and installed tools

Run the command that matches the change you want:

| Task | Command |
| --- | --- |
| Refresh the lock after editing `pyproject.toml` | `uv lock` |
| Upgrade within the declared constraints | `uv lock --upgrade` |
| Install the locked environment | `uv sync --locked` |
| Add a development dependency | `uv add --dev <package>` |

The configured-console shortcuts `pcomp`, `pupg`, and `psync` call the
certificate-aware `tools/uv_run.py` wrapper. When a corporate proxy needs a
custom certificate, use the wrapper with an explicitly configured
`SSL_CERT_FILE` after environment setup. See the
[dependency shortcut reference](../reference/aliases-and-launchers.md#-dependency-shortcuts)
for its fallback order. Plain `uv` does not use that wrapper's retry logic.

## Check dependency state without applying an upgrade

| Question | Command | Network needed |
| --- | --- | --- |
| Do the environment, lock, and project declarations agree? | `uv sync --locked --check` | No |
| What upgrades are allowed by the dependency graph? | `uv lock --upgrade --dry-run` | Yes |
| Which installed packages have newer releases? | `uv pip list --outdated` | Yes |

An outdated package can still be constrained by another dependency. Use the
lock dry run to assess project upgrades; the installed-package list alone does
not establish that they are compatible.

## Verify documentation changes

From a PowerShell or cmd console in the repository, run:

```text
markdown-check.bat
```

The [Markdown checker reference](../reference/markdown-checker.md) describes
its tracked-file inventory, rules, and baseline. For code work, follow the
project's [Groundhog workflow](../../instructions/groundhog.md) and its checks.
