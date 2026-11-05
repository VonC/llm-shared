# Every Suite Gets a Stopwatch

- Type: feature-request
- Test group: whole suite

## Why the gate should leave llm-shared's own suite

llm-shared's tests run under a gate. Each test lifecycle, setup through
teardown, stays under a CPU ceiling (`test_lifecycle_limit`, 0.1 s) and a wall
limit (`test_lifecycle_wall_limit`, 1 s). A test already proven under its
ceiling on this checkout passes a load spike up to a stability band, and no
test may start a process. The gate lives in `tests/simulation_policy.py` and
`tests/lifecycle_cpu_record.py`, loaded by `tests/conftest.py`, so it judges
llm-shared's own suite and nothing else.

The shared instruction `instructions/write-fast-python-tests.md` already tells
the agent of every project to keep each lifecycle under those two keys. In a
consuming project nothing reads them: no over-budget test fails, and the
groundhog `speed` verdict looks at call time only, flagging a call only when it
is both a statistical outlier and above the project's duration floor. A project
that follows the instruction has no way to prove it does.

## What a consuming project can import today

Checked on 2026-11-03, the answer is nothing:

- llm-shared is never installed. Its `pyproject.toml` sets `package = false`;
  its tools run in place, through the `bin\*.bat` launchers, in llm-shared's
  own virtual environment.
- groundhog runs from that environment, but it spawns the project's own
  `pytest`, found on the `PATH` the project's `senv.bat` prepares. The tests
  run in the project's interpreter, with the project's import path.
- None of the seven consuming projects checked puts llm-shared on that path:
  no `PYTHONPATH` entry, no `.pth` file in its environment. A `-p tools.<name>`
  option fails there with a module-not-found error.
- Adding llm-shared's root to the path would not fix it. Six of those projects
  have a top-level `tools` package of their own and one a `tests` package; the
  project's package comes first on the path and hides llm-shared's, or the
  reverse.
- The gate imports two other llm-shared modules,
  `tools.review_artifact_configuration` and `tools.review_exchange_models`, to
  find the review artifact home that holds its record.
- Those projects run pytest 9.1, one of them on Python 3.12 and the others on
  3.13. One has pytest-xdist; six have Hypothesis.

## Intent

- One shared plugin, opt-in per project. A project that does nothing sees no
  change in any test run.
- Two separate opt-ins, both through `-p`, in the project's `addopts` or on
  one command line:
  - the lifecycle gate, with its CPU band and per-checkout record;
  - the process audit. It installs a Python audit hook that stays for the rest
    of the process, so a project whose tests still start processes can take
    the gate without it, and add the audit once its tests are converted.
- The plugin has an import name of its own, never `tools` or `tests`, so it
  can sit on the path of a project that has packages with those names. Its
  files live under llm-shared's `tools/`.
- It runs in the consuming project's interpreter: on the oldest Python and
  pytest a consuming project uses (Python 3.12 and pytest 9.1 today), with or
  without pytest-xdist, with or without Hypothesis.
- It carries what it needs. At test time it imports no other llm-shared
  module; it brings its own lookup of the artifact home, with the same rule as
  today: the home `.review-artifacts.ini` names, else `.reviews`, and only an
  existing home whose `.gitignore` is exactly `*`, else nothing is recorded.
- Today's behaviour, unchanged: the four `test_lifecycle_*` ini keys with
  their defaults and precedence, the usage error on a value that would switch
  the gate off, the band and drift guard, the record
  `a.test-lifecycle-cpu.local.json` with its `nodes` and `exceptions`, the
  end-of-run summary, and one record write per run on the xdist controller.
- llm-shared's own suite becomes the first user: `tests/conftest.py` loads the
  shared plugins instead of its own copies, so one implementation remains,
  under llm-shared's 100% coverage gate.
- One documented way to make the plugin importable from a consuming project,
  working for a plain `pytest` in the project's shell and for every groundhog
  stage alike. Ways to weigh: an editable path dependency in the project's
  development dependency group; a dedicated plugin directory that `senv.bat`
  and groundhog add to the child's path; the project's `conftest.py` adding
  that directory itself.
- The documentation follows: the test lifecycle reference and how-to pages
  describe the plugins for any project, a how-to shows a consuming project
  opting in, and `write-fast-python-tests.md` says where the budget is
  enforced and how a project turns it on.
- No consuming project is named in the plugins, their tests or their
  documentation.
