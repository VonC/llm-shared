# Validate shared pytest compatibility

<!-- markdownlint-disable MD013 -->

## Invocation model

Run setup explicitly for each checkout. Validation runs directly when requested
and automatically before opted-in groundhog day and full commands.

Provision the independent environment explicitly in **each** new llm-shared
clone or worktree, then validate it:

```cmd
bin\lifecycle_compatibility.bat --setup
bin\lifecycle_compatibility.bat
```

Setup uses `uv` and creates `venvs/python_3.12_lifecycle_compatibility/` from
that checkout's `tools/lifecycle_compatibility/requirements-py312.txt` exact
pins. This environment belongs to the checkout; it does not replace the main
project interpreter. Ordinary validation never installs missing prerequisites.
For an existing prepared environment, set `LLM_SHARED_LIFECYCLE_PYTHON` to its
absolute `python.exe` path. Both the default and override routes probe the
actual Python 3.12 version and pinned dependencies before running any scenario.
Missing or unsuitable prerequisites produce setup instructions and fail.

## Require fresh validation in groundhog

This repository declares:

```toml
[tool.llm-shared.lifecycle-compatibility]
enabled = true
```

Groundhog uses the fixed project-relative `bin/lifecycle_compatibility.bat`
entrypoint for opted-in projects. Fresh day and direct-full preflights run
before proof reuse. A missing table or literal `enabled = false` requires no
preflight; a missing `enabled` key also disables it. Malformed tables and
enabled values that are not booleans are setup errors. Consumers remain independent and need not opt into this
repository's compatibility harness to use either pytest policy.

Plain pytest can verify selected policy behavior but does not establish the
full groundhog compatibility contract. The real harness runs isolated projects,
bounded child-process probes, optional-package absence and two-worker barrier
checks outside the audited suite. Validation never silently substitutes the
main interpreter for the independent Python 3.12 environment.

On Windows, the same full harness runs eleven calling-shell checks with delayed
expansion off and on: punctuation and OEM paths, atomic refusals, drive-root
callers, exclusive concurrent transfers and concurrent preparations. Other
platforms report these shell checks as not run. To retain private observations,
pass `--evidence <fresh-private-directory>` to the launcher. Evidence includes
environment snapshots and caller paths; choose a directory outside tracked docs.
Ordinary automatic validation cleans its temporary evidence.

Prepared cases can publish immutable loaders in the default user-local cache.
Use the explicit cache cleanup described in
[enable the shared lifecycle gate](enable-shared-lifecycle-gate.md) when needed.

Consult the [acceptance evidence](../../docs/v0.14.0/acceptance.v0.14.0.shared_lifecycle_gate.md)
for observed platform/version results. Portable behavior is intended; Linux
and macOS remain unvalidated until real evidence is obtained there.
