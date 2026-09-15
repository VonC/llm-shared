"""Collect an explicit synthetic evidence snapshot from any caller directory."""

from pathlib import Path
import sys

# Locate code from this physical script only; telemetry and repository identities
# must still be supplied in the manifest as explicit absolute paths.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.wait_evidence.reports import main

if __name__ == "__main__":
    raise SystemExit(main())

# eof
