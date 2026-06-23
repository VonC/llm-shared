"""Git-history dashboard tool, shared across projects via llm-shared.

This package exports a project's commit history with ``git log``, aggregates it,
and renders a standalone ``dashboard.html``. The tool ships here in
``llm-shared`` but always operates on the *calling* project, resolved through the
shared ``find_project_root`` helper (``PRJ_DIR``-aware).

Step 1 (v0.8.0) split the single ``build.py`` into three modules so the hub has
room to grow for the multi-project work:

- ``aggregate.py``: the data model (``Commit``, ``DashboardData``,
  ``Highlights``) and the commit aggregation.
- ``render.py``: the placeholder substitution into ``template.html``.
- ``build.py``: the ``git log`` export, the CSV parse, the build orchestration,
  and the CLI; it re-exports the moved names so callers stay unaffected.

The ``__init__`` makes the directory an importable package so the build helpers
can be exercised from the test suite.
"""


# eof
