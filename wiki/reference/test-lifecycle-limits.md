# Test lifecycle limits reference

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🧪 The suite's pytest plugin `tests/simulation_policy.py` judges every test
lifecycle, setup through teardown, against a CPU limit and a wall-clock limit.
Every limit is a project setting. This page lists the settings, how one test's
CPU limit is chosen, the per-checkout record behind the CPU stability band,
exception entries and the end-of-run summary. For the reasons, see
[Why fast tests keep the work they assert](../explanation/why-fast-tests-keep-the-work-they-assert.md);
to change a value or accept a slow test, follow
[Set the test lifecycle limits](../how-to/set-test-lifecycle-limits.md).

## Invocation model

Nobody calls the gate. `tests/conftest.py` loads `tests/simulation_policy.py`
as a pytest plugin, so every pytest run of this suite applies it, including
each groundhog stage. The project sets the values in its pytest configuration;
one run can override them on the command line.

## Settings and their defaults

| Ini key | Plugin default | Accepted value | Meaning |
| --- | --- | --- | --- |
| `test_lifecycle_limit` | `0.1` | seconds above 0 | default CPU ceiling of one lifecycle |
| `test_lifecycle_cpu_band_factor` | `2.5` | a number of at least 1 | a proven test may use this multiple of its ceiling |
| `test_lifecycle_cpu_drift_runs` | `3` | a whole number of at least 1 | consecutive measured runs above the ceiling that cost the proof |
| `test_lifecycle_wall_limit` | `1.0` | seconds above 0 | wall-clock limit of one lifecycle; no band applies |

A value is read in this order, the first found wins:

1. `-o <key>=<value>` on the pytest command line, for one run;
2. `[tool.pytest.ini_options]` in the project's `pyproject.toml`, or its
   `pytest.ini`;
3. the plugin default above.

This repository sets `test_lifecycle_limit = "0.1"`,
`test_lifecycle_cpu_band_factor = "2.5"` and
`test_lifecycle_cpu_drift_runs = "3"` in `pyproject.toml`, and keeps the
default wall limit.

A value outside the accepted range would switch the gate off, so pytest
refuses it before collecting, with exit code 4 and a message naming the key:

```text
ERROR: test_lifecycle_cpu_band_factor = '0.5' in the pytest configuration: expected a multiple of at least 1
```

## How one test's CPU limit is chosen

1. **Ceiling.** The test's ceiling is `test_lifecycle_limit`, or the `cpu` of
   its accepted exception when that is higher. An exception never lowers it.
2. **Proof.** The proof holds when the record marks the test proven and the
   CPU of the run that earned it is at or below the current ceiling. A proof
   earned under a looser ceiling, from an `-o` run or before the project
   lowered its value, does not hold.
3. **Limit.** A test whose proof holds may use its band top, ceiling times
   `test_lifecycle_cpu_band_factor`. Any other test is held to its ceiling.

With the defaults:

| Test | Ceiling | Proof holds | CPU limit |
| --- | --- | --- | --- |
| no exception, never proven | 0.1 s | no | 0.1 s |
| no exception, proven | 0.1 s | yes | 0.25 s |
| exception at 0.3 s, not proven | 0.3 s | no | 0.3 s |
| exception at 0.3 s, proven | 0.3 s | yes | 0.75 s |

The wall limit is the same for every test. A lifecycle over either limit
fails, unless it already failed for another reason. Its message gives both
clocks and the basis of the CPU limit, for example
`ceiling 0.100s, not proven here, band top 0.250s`.

## How a measured run updates the proof

A measured run is a lifecycle whose call passed and where nothing else failed.
A failing or skipped test neither proves itself nor counts toward the drift
guard.

| Run CPU | Proof before the run | Proof after the run |
| --- | --- | --- |
| at or below the ceiling | any | proven, drift count 0, earned at this CPU |
| above the ceiling | none, or no longer holding | not proven |
| above the ceiling | holds, drift count + 1 below `test_lifecycle_cpu_drift_runs` | proven, drift count + 1 |
| above the ceiling | holds, drift count + 1 reaches `test_lifecycle_cpu_drift_runs` | not proven, listed as a lost proof |

A run above the band top fails and still counts toward the drift guard.

## The per-checkout record

The record is `a.test-lifecycle-cpu.local.json` in the review artifact home
(`.reviews` unless `.review-artifacts.ini` names another). It is untracked and
belongs to one checkout, because timings depend on the machine.

- The plugin writes it only when the home already exists and its `.gitignore`
  is exactly `*`. Otherwise every test stays strict and the summary says
  nothing was recorded.
- Every pytest process reads it once at start. Under xdist only the controller
  writes it, once at session end, re-reading it first and replacing it whole.
- A missing record means every test starts strict. A damaged record keeps every
  test strict and stays untouched; the summary names the problem.

```json
{
  "schema": 1,
  "about": "nodes: written by tests/simulation_policy.py after each measured run. ...",
  "exceptions": {
    "tests/unit/tools/test_example.py::test_cold_grammar": {
      "cpu": 0.3,
      "attempted": "cached the grammar per session",
      "reason": "the first parse imports the grammar package"
    }
  },
  "nodes": {
    "tests/unit/tools/test_example.py::test_cold_grammar": {"proven": true, "over_runs": 0, "cpu": 0.28125, "proven_cpu": 0.28125},
    "tests/unit/tools/test_example.py::test_parse": {"proven": true, "over_runs": 1, "cpu": 0.125, "proven_cpu": 0.046875}
  }
}
```

Keys are pytest node ids without the xdist `@<group>` suffix, so a test keeps
one entry across serial and distributed runs.

| Object | Owner | Field | Meaning |
| --- | --- | --- | --- |
| `nodes` | the plugin | `proven` | the test holds a proof |
| `nodes` | the plugin | `over_runs` | consecutive measured runs above the ceiling |
| `nodes` | the plugin | `cpu` | lifecycle CPU of the last measured run |
| `nodes` | the plugin | `proven_cpu` | CPU of the run that earned the proof; absent in older records, which fall back to `cpu` |
| `exceptions` | the person accepting a slow test | `cpu` | measured lifecycle CPU, above 0; becomes the test's ceiling when higher than the default |
| `exceptions` | the person accepting a slow test | `attempted` | the improvement already attempted |
| `exceptions` | the person accepting a slow test | `reason` | why the cost stays |

The plugin keeps `exceptions` and any other top-level key as written. An
exception entry missing one of its three fields, or with a `cpu` that is not a
positive number, is rejected: it grants nothing and is listed at the end of
every run.

## End-of-run summary

Every run ends with a `lifecycle CPU band` section:

| Line | Shown when |
| --- | --- |
| `record <path>: <n> measured, <m> in the band, <k> lost proof` | always; `none` as the path when nothing can be recorded |
| `band pass: <node> CPU=<s>s, <basis> <ceiling>s, proven here, band applies, band top <top>s` | a proven test used more than its ceiling, within its band top |
| `proof lost after <n> runs above the ceiling: <node>` | the drift guard removed a proof in this run |
| `accepted exception: <node> CPU=<s>s; attempted: <text>; reason: <text>` | for every accepted exception |
| `rejected exception, needs cpu, attempted and reason: <node>` | for every rejected exception |
| `no ignored artifact home; nothing recorded` | no home, or a home Git could track |
| `record problem: <text>` | the record could not be read or written |

Related: [ghog commands and exit codes](ghog-commands-and-exit-codes.md),
[Artifact files and naming conventions](artifact-files.md).
