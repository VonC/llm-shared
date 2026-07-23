#!/usr/bin/env python3
"""Lean pre-commit adapter for the staged sensitive-blob check."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from tools.sensitive_history.sensitive_commit_check import main

raise SystemExit(main(["staged"]))


# eof
