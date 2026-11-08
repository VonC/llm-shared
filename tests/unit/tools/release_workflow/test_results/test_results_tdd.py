"""Results separate data and diagnostics and preserve original failures.

Step 1 of v0.14.0 version-sources: status 3, an incomplete restoration, is a
public status like 0, 1 and 2; any other value still becomes 1 with its
original value in a diagnostic.
"""

from __future__ import annotations

import io

import pytest

from tools.release_workflow.results import OperationResult, configure_stream, render


@pytest.mark.parametrize("status", [0, 1, 2, 3])
def test_render(status: int) -> None:
    """Unicode data and warnings go to separate LF streams."""
    out, err = io.StringIO(), io.StringIO()
    assert render(OperationResult(status, "données\r\n", ("warning\r\nline",)), stdout=out, stderr=err) == status
    assert out.getvalue() == "données\n"
    assert err.getvalue() == "warning\nline\n"


@pytest.mark.parametrize("status", [4, 23])
def test_unexpected_child_status(status: int) -> None:
    """An unexpected native code becomes failure with its original detail."""
    out, err = io.StringIO(), io.StringIO()
    assert render(OperationResult(status, diagnostics=("original child failure",)), stdout=out, stderr=err) == 1
    assert f"native status {status}; returning 1" in err.getvalue()
    assert "original child failure" in err.getvalue()
    assert not out.getvalue()


def test_real_stream_encoding() -> None:
    """Actual text wrappers are reconfigured even when the inherited codec differs."""
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding="ascii", newline="\r\n")
    configure_stream(stream)
    stream.write("é\n")
    stream.flush()
    assert buffer.getvalue() == "é\n".encode()
    stream.detach()

# eof
