"""Git-history dashboard tool, shared across projects via llm-shared.

This package holds ``build.py``, which exports a project's commit history
with ``git log``, aggregates it, and renders a standalone
``dashboard.html``. The tool ships here in ``llm-shared`` but always
operates on the *calling* project, resolved through the shared
``find_project_root`` helper (``PRJ_DIR``-aware).

The ``__init__`` makes the directory an importable package so the build
helpers can be exercised from the test suite.
"""


# eof
