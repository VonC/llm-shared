# How to set the test lifecycle limits

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The lifecycle gate runs in this repository's suite and in consumer runs that
[select it](enable-shared-lifecycle-gate.md), including groundhog stages.
Use this guide when a project needs a
different CPU ceiling or band, when one run needs other limits, or when a test
must stay slower than its ceiling after a real attempt to speed it up.

🧪 Goal: set the CPU ceiling, the stability band and the drift guard for a
project, override them for one run, and accept a slow test as a reviewed
exception. Every key and file format is listed in the
[test lifecycle limits reference](../reference/test-lifecycle-limits.md).

## Set the project's limits

1. Open the project's `pyproject.toml` and find `[tool.pytest.ini_options]`.
2. Set the keys the project needs; a key left out keeps its plugin default:

   ```toml
   [tool.pytest.ini_options]
   test_lifecycle_limit = "0.1"
   test_lifecycle_cpu_band_factor = "2.5"
   test_lifecycle_cpu_drift_runs = "3"
   test_lifecycle_wall_limit = "1.0"
   ```

3. Run the suite, for example `ghog day --full=speed`. A value that would
   switch the gate off stops pytest at once with exit code 4 and names the key.

Lowering the ceiling takes effect on the next run: a proof earned above the new
ceiling no longer holds, so those tests are strict until a run brings them
under it. Raising the ceiling is a project decision like raising any budget;
it must not conceal an individual slow test. For initial adoption, choose a
temporary higher project limit based on measured costs, then reduce it
gradually as offenders are fixed. CPU at or below the effective limit passes
lifecycle timing even when wall time exceeds `test_lifecycle_wall_limit`.
Keep that wall setting as a reporting reference. Keep both settings finite and positive; no
disabled, report-only or grace mode exists.

To enumerate all offenders, use a complete run without file, keyword or marker
selection and without `-x` or `--maxfail`. An affected or early-stopped run
cannot establish the complete inventory.

## Override the limits for one run

Pass `-o <key>=<value>` to pytest; the value beats `pyproject.toml` for that run
only:

```bat
python -m pytest tests/unit/tools/test_example.py -o test_lifecycle_cpu_band_factor=1
```

A factor of 1 turns the band off for that run, so every test is held to its
ceiling. A run with a looser ceiling still updates the record, but the proofs
it earns above the project's ceiling grant no band on later runs.

## Accept a slow test as an exception

Do this only after a real attempt to speed the test up, as
[Fix a slow test flagged as an outlier](fix-a-slow-test.md) and
`instructions/write-fast-python-tests.md` describe.

1. Measure the lifecycle CPU: the failure message gives `CPU=<seconds>`.
2. Open `.reviews/a.test-lifecycle-cpu.local.json`, or the record in the
   project's configured artifact home.
3. Add the test under `exceptions`, keyed by its node id without any
   `@<group>` suffix, with all three fields:

   ```json
   "exceptions": {
     "tests/unit/tools/test_example.py::test_cold_grammar": {
       "cpu": 0.3,
       "attempted": "cached the grammar per session",
       "reason": "the first parse imports the grammar package"
     }
   }
   ```

4. Run the test again. Its ceiling is now the recorded `cpu`; once a run proves
   it at or under that ceiling, the band applies to it as to any other test.

The record is per checkout and untracked, so an exception stays on the machine
where it was measured. Every run lists it in the `lifecycle CPU band`
summary; an entry missing a field is listed as rejected and grants nothing.

## Read what the band tolerated

At the end of each run, the `lifecycle CPU band` section shows how many
lifecycles were measured, every band pass with its CPU and band top, and every
proof the drift guard removed. A test that keeps appearing as a band pass, or
whose proof was lost, is drifting: profile it before it fails.

Related: [Why fast tests keep the work they assert](../explanation/why-fast-tests-keep-the-work-they-assert.md).
