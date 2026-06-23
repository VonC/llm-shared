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
- ``build.py``: the ``git log`` export, the CSV parse, and the ``write_dashboard``
  write; it re-exports the moved names so callers stay unaffected.
- ``cli.py`` (Step 2): the multi-repo orchestration -- target resolution, the
  per-repo export loop, the browser open, and the run summary; ``build.main``
  delegates to it.
- ``analysis.py`` (Step 3): the regenerated ``analysis.generated.md``, the
  kept-once per-project notes, and the ``uv``-backed markdown-to-HTML seam that
  fills the template's ``__ANALYSIS__`` slot.

The ``__init__`` makes the directory an importable package so the helpers can be
exercised from the test suite.
"""


# eof
