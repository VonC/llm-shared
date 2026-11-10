# Enable the shared process audit

<!-- markdownlint-disable MD013 -->

## Invocation model

Prepare the consumer shell explicitly; the selected audit then runs inside
pytest, including groundhog test stages, without a separate audit command.

Select your project's Python 3.12 or later environment, enter its root, and run:

```cmd
set LLM_SHARED_PYTEST_PLUGINS=process
call C:\shared\bin\prepare_pytest_plugins.bat
python -m pytest --strict-markers
```

Replace `C:\shared` with the llm-shared checkout. Check preparation succeeds
before continuing. Select `lifecycle,process` to apply both independent policies.
The [activation guide](enable-shared-lifecycle-gate.md) covers shell boundaries,
import paths, cache verification, deselection and startup exit 4. Explicit
`-p llm_shared_process_audit` is also supported with the dedicated policy
directory on the import path. Optional xdist and coverage packages are unnecessary.

## Declare a justified test permission

Register the marker independently in normal pytest configuration, so strict
runs remain valid without the audit:

```toml
[tool.pytest.ini_options]
markers = ["process_allowed(reason): justified process creation"]
```

Apply it to the individual function or parametrized case:

```python
@pytest.mark.process_allowed(reason="exercise the external command protocol")
def test_external_command():
    ...
```

Reasons must be nonempty strings. Class/module inherited permissions and
conflicting declarations are startup errors. A test permission covers its call
and function-scoped fixture operations; it does not authorize broader fixtures.

## Authorize one fixture's operations

Put a dictionary in the collected test module or defining `conftest.py`, using
the decorated fixture object as the key:

```python
import pytest

@pytest.fixture(scope="module")
def service(request):
    server = start_external_service()
    request.addfinalizer(server.stop)
    yield server

LLM_SHARED_PROCESS_FIXTURES = {service: "exercise the service protocol"}
```

This declaration needs no shared imports and no ini key. It is harmless when
the audit is absent. It authorizes only that fixture's setup, registered
finalizers and yield teardown. Fixtures it requests need their own permission.
A test using the fixture receives no permission for its own call.

Ownership uses a live operation token on the executing thread. Cached fixture
access, another thread or a copied context cannot borrow the fixture token.
Nested pytest sessions have independent permissions. When both fixture and
test could authorize an operation, fixture credit wins.

## Read the report and retain timing accountability

The report lists exercised test and fixture permissions, their reasons and
whether an event used them. Unused permissions produce `WARNING unused`;
fixtures that were not requested do not enter the report. Remove obsolete declarations.
Under xdist, the controller validates all initial worker collections before
setup, aggregates permission usage and reports once. Invalid declarations,
inconsistent collection or missing worker evidence fail closed.

A permission only allows process creation. With the lifecycle gate selected,
setup and teardown remain timed, including shared fixtures charged to the
test that performs their operations. Parent process CPU and elapsed lifecycle
time are measured; child CPU and a detached child's later lifetime are outside
that window. Keep real executable probes in the separate compatibility harness
when the carrying suite requires process-free tests.
