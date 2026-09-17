"""Run the native-wake prototype from this script's physical checkout."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.wait_evidence.probe_cli import main  # noqa: E402 - Physical checkout bootstrap.

if __name__ == "__main__":
    raise SystemExit(main())

# eof
