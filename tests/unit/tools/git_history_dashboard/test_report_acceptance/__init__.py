"""Package markers for the git-history dashboard acceptance tests.

Step 5 (v0.8.0): holds test_report_acceptance_tdd.py, which builds a real
multi-repo report from throwaway git repositories and asserts the whole chain --
the combined payload (``projects``, ``by_project`` summing to the top level,
``by_author``), the filled ``__TITLE__`` and ``__ANALYSIS__`` slots with no
pdfsplitter string, the analysis round-trip (generated refreshes, notes kept),
and the ``--no-open`` suppress flag.
"""

# eof
