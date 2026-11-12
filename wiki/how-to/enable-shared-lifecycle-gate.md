# Enable the shared lifecycle gate

<!-- markdownlint-disable MD013 -->

## Invocation model

Prepare the consumer shell explicitly; subsequent pytest and groundhog runs in
that environment apply the selection automatically.

The gate passes lifecycle timing when CPU is at or below the test's effective
limit, including any eligible band or accepted exception. Wall time remains
measured; exceeding its configured reference alone does not fail timing.
Functional failures, selected process auditing and groundhog's separate speed
verdict still apply.

Use Python 3.12 or later with pytest in your project's environment. The gate
needs neither pytest-cov nor pytest-xdist. Start in the consumer project root
after selecting its interpreter. Replace `C:\shared` below with your llm-shared
checkout; keep that checkout available while the prepared shell is in use.

```cmd
set LLM_SHARED_PYTEST_PLUGINS=lifecycle
call C:\shared\bin\prepare_pytest_plugins.bat
python -m pytest
```

Check preparation's exit code before running tests. A successful preparation
binds `LLM_SHARED_PYTEST_ROOT` to the current project and
`LLM_SHARED_PYTEST_POLICY_DIR` to the checkout's dedicated `tools/pytest_plugins`
directory. It adds that directory and an immutable loader directory to
`PYTHONPATH`, preserving unrelated entries, and injects
`-p llm_shared_pytest_loader` into `PYTEST_ADDOPTS`. Never add the shared
repository root or its `tools` directory: consumer `tools` and `tests` packages
must keep their own identities. No consumer file is changed.

The selection is empty, `lifecycle`, `process`, or `lifecycle,process`.
To add auditing, follow [Enable the process audit](enable-shared-process-audit.md).
Prepared-shell plain pytest and every groundhog pytest stage honor selection.
Outside that environment, activation is explicit; this repository loads both
canonical policies for its own suite. Keep policy `-p` options out of tracked
consumer `addopts`. Direct `-p llm_shared_lifecycle_gate` is supported when only
the dedicated policy directory is on the import path; it does not supply the
prepared loader's binding and all-selected preflight.

## Keep strict configuration valid without selection

If you track lifecycle settings, register all four keys in root `conftest.py`
so plain pytest with `--strict-config` can read them without the gate:

```python
def pytest_addoption(parser, pluginmanager):
    if not pluginmanager.has_plugin("llm_shared_lifecycle_gate"):
        parser.addini("test_lifecycle_limit", "CPU seconds", default="0.1")
        parser.addini("test_lifecycle_wall_limit", "Wall seconds", default="1.0")
        parser.addini("test_lifecycle_cpu_band_factor", "CPU band", default="2.5")
        parser.addini("test_lifecycle_cpu_drift_runs", "Drift runs", default="3")
```

Use this exact plugin-manager guard. An older unguarded registration can
silently replace the gate defaults. With the guard, either loading order keeps
the precedence `-o` override, then project setting, then plugin default.
See [Set lifecycle limits](set-test-lifecycle-limits.md) for gradual adoption
and [the reference](../reference/test-lifecycle-limits.md) for records and clocks.

## Refresh or remove shell activation

After changing checkout or project, open a fresh project shell and prepare it.
To deselect in a prepared shell, clear `LLM_SHARED_PYTEST_PLUGINS` and run
preparation again. This removes owned binding, path and loader options while
preserving unrelated values. A stale shell, root outside the binding, missing
selected source, import error, blocked selected plugin or contract mismatch
refuses startup with pytest exit 4 before tests. Groundhog rejects a foreign
project binding before any child or proof reuse; return to the intended
project and prepare there.

The user-local cache contains only the loader, under a SHA256 content key.
Preparation verifies an existing entry and never repairs it in place. A newer
loader receives a new immutable entry. Refresh by preparing again; explicitly
remove a corrupt entry only after stopping shells that use it, then prepare.
Cache cleanup is explicit, never an automatic deletion of old entries.
Preparation failures leave the caller environment unchanged, including Windows
encoding failures. See [compatibility validation](validate-shared-pytest-compatibility.md)
for the separately provisioned real-runtime checks.
