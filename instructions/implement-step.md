# Implement step instructions

Include "Step XXXX" in the title of this conversation (replace XXXX with the step mentioned in the prompt, for example '2', for "Step 2 of the CDC gap feature").

Read carefully the markdown files in your context to understand the context.

Based on the design markdown and the plan markdown, follow instructions from [`implement-plan.prompt.md`](../.github/prompts/implement-plan.prompt.md), and implement step XXXX (see your prompt), doing a `check.bat` to see if there is any error or linter warning to fix, then (once there is no more error or warning), running `pta` to check that the focused tests pass. Focused tests are the tests created, modified, or impacted by this step. See [Run the focused tests with pta](#run-the-focused-tests-with-pta) below for the exact command and why it is coverage-safe.

Make sure no new computation would introduce any O(n^2) or O(n log(n)) process.

Make sure DDD-Hexagonal architecture is strictly respected: no violation, no smell.

Make sure no existing feature or reporting capability is impaired.

Each new test must follow the convention `...\tests\unit\xxx\yyy\...\test_filename\test_filename_tdd.py`, and you must check if a pbt is needed as well. And do not forget the `__init__.py` to create or to update, for test and non-test code.

Before writing code, write a short analysis of the issue and a brief description of the implementation. Only then write the code, following the project instructions in `CLAUDE.md` (and `copilot-instructions.md` for Copilot users), which means write the class in full (no "`# ...existing code...`" comment).

Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well.

Preserve existing code and docstrings and comments; only update them to explain and accommodate your implementation. Check if any comment is obsolete considering the current code and remove them. Do not remove comments like `# Act` unless the whole section has been removed as part of your fix. Read and follow instructions from [`preserve_code.md`](../rules/preserve_code.md).

When writing an answer in markdown, follow instructions from [`markdown.md`](../rules/markdown.md).

## Run the focused tests with pta

At the end of the step, once `check.bat` (or `c`) is clean, run `pta` to check that the focused tests pass. Focused tests are the tests created, modified, or impacted by this step.

`pta` is `pytest --testmon --no-header --no-cov -rxX`:

- `--testmon` selects only the tests affected by the changes, so the run stays on the focused tests.
- `--no-cov` turns coverage off. It overrides the `--cov=tools`, `--cov-report`, and `--cov-fail-under=100` defaults from `pyproject.toml`, so the run reports pass or fail, does not rewrite the `.coverage` the user already recorded, and does not fail on the 100% gate.

To run one test, one class, or one file on its own, use `pts <test path>`, which is `pytest --no-header --no-cov -rxX <path>`. It is coverage-off too, so it never erases the recorded coverage.

Do not run the full coverage pass during the step. `ptr` (`del .testmondata & pytest --testmon --no-header --cov-report term-missing:skip-covered`) records full coverage, but the user runs it by hand only: it is too slow and uses too many tokens for the step flow. Never call a plain `pytest`, or any command that records coverage without `--cov-append`, because the `--cov=tools` default would erase the coverage the user already recorded.

## Reach 100% coverage on each unit-tested class

This rule is for unit tests only, the ones under `src\pdfss\tests\unit`. It does not apply to integration, smoke, regression, or acceptance tests.

- One unit test file, or a set of unit test files inside a test folder named after the class under test, must reach 100% coverage of that one Python class file. Each unit-tested class file gets to 100% on its own, in one test file or several.
- Design the class file to be easy to test first: small methods, injected dependencies, no hidden side effects. Then write the unit tests so they both exercise the behaviour and reach 100% of that class file.
- A unit test folder targets a single class file. Other test types may cover several classes at once; they carry no coverage target and answer only to what they represent (integration, smoke, regression, or acceptance).
- If a legacy unit test exists, is impacted by this step, and its run does not reach 100% of the class it tests, take the chance to complete it (unit tests only) so that class file is back at 100%.
