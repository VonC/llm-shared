"""The evidence bundle is strict schema 1 JSON whose listed files are verified on every read and whose checks refuse gaps.

Step 6 of v0.14.0 git-cliff-provisioning (design "Outputs and
classification" and "Statuses"; design decisions Q11 and Q13; plan decisions
Q08 and Q16).

- A written bundle reads back equal; `bundle.json` holds exactly its members,
  without `review` until the user's decision.
- The reader is strict: an unknown or missing member, a repeated key, another
  schema, a mistyped or malformed value is refused.
- The `files` member lists the SHA-256 of `cliff.toml` and both trust records;
  a changed, missing or unlisted file is refused on read.
- Code review round 1: read reconciles each trust record with the identity
  the inputs name. Round 2: the inputs record llm-shared's tags with their
  commits; the completeness checks moved to `test_git_cliff_bundle_checks`
  with `bundle_checks`.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import TYPE_CHECKING, cast

import pytest

from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    BASELINE,
    DIFFERING,
    PIN,
    SAMPLE_RANGES,
    place_bundle,
    sample_inputs,
)
from tools.release_workflow.git_cliff.bundle import (
    BUNDLE_FILE,
    CLIFF_TOML,
    BundleError,
    file_digests,
    listed_files,
    read,
    trust_name,
    write,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_LOCATION = f"tools/release_workflow/git_cliff/bundles/{PIN}"
_MEMBERS = {"schema", "inputs", "outputs", "classification", "audit", "observed_statuses", "files"}


def _document(directory: Path) -> dict[str, object]:
    """Read `bundle.json` as plain JSON."""
    loaded: dict[str, object] = json.loads((directory / BUNDLE_FILE).read_bytes())
    return loaded


def _rewrite(directory: Path, change: Callable[[dict[str, object]], None]) -> None:
    """Change the plain JSON document in place and write it back."""
    document = _document(directory)
    change(document)
    (directory / BUNDLE_FILE).write_text(json.dumps(document), encoding="utf-8")


def _member(container: dict[str, object], key: str) -> dict[str, object]:
    """Return an object member of a plain JSON object."""
    return cast("dict[str, object]", container[key])


def _entries(container: dict[str, object], key: str) -> list[dict[str, object]]:
    """Return a list of objects member of a plain JSON object."""
    return cast("list[dict[str, object]]", container[key])


def test_a_written_bundle_reads_back_equal_without_a_review_member(tmp_path: Path) -> None:
    """The model round-trips; until a decision exists, `review` is absent from the file."""
    bundle = place_bundle(tmp_path)
    assert read(tmp_path) == bundle
    assert set(_document(tmp_path)) == _MEMBERS
    assert bundle.pin == PIN
    assert bundle.baseline == BASELINE
    assert (tmp_path / BUNDLE_FILE).read_bytes().endswith(b"}\n")


def test_a_bundle_without_audit_reads_back_and_a_missing_bundle_is_named(tmp_path: Path) -> None:
    """A first run writes `audit: null` and no hand entries; a directory without `bundle.json` cannot be read."""
    bundle = place_bundle(tmp_path, classification=(), audit=None, observed_statuses=())
    assert _document(tmp_path)["audit"] is None
    assert read(tmp_path) == bundle
    with pytest.raises(BundleError, match="cannot be read"):
        read(tmp_path / "absent")


def test_the_listed_files_are_the_cliff_toml_copy_and_both_trust_records() -> None:
    """The `files` member names exactly three files."""
    assert listed_files(PIN, BASELINE) == (CLIFF_TOML, trust_name(PIN), trust_name(BASELINE))
    assert trust_name(BASELINE) == "trust.2.7.0.json"


def _extra_member(document: dict[str, object]) -> None:
    """Add a member schema 1 does not know."""
    document["extra"] = 1


def _missing_member(document: dict[str, object]) -> None:
    """Remove the outputs."""
    del document["outputs"]


def _other_schema(document: dict[str, object]) -> None:
    """Claim another schema."""
    document["schema"] = 2


def _drop_commit(document: dict[str, object]) -> None:
    """Remove the frozen commit from the inputs."""
    del _member(document, "inputs")["llm_shared_commit"]


def _mistype_size(document: dict[str, object]) -> None:
    """Write a candidate size as a string."""
    _entries(_member(document, "inputs"), "candidates")[0]["size"] = "12"


def _bad_digest(document: dict[str, object]) -> None:
    """Write a malformed `cliff.toml` digest."""
    _member(_member(document, "inputs"), "cliff_toml")["sha256"] = "XYZ"


def _bad_repository(document: dict[str, object]) -> None:
    """Name an unknown repository in a range."""
    _entries(_member(document, "inputs"), "ranges")[0]["repository"] = "elsewhere"


def _bad_hunk(document: dict[str, object]) -> None:
    """Write a hunk that is not text."""
    _entries(document, "outputs")[1]["hunks"] = [3]


def _bad_status(document: dict[str, object]) -> None:
    """Write a negative status."""
    _member(_member(_entries(document, "outputs")[0], "results"), PIN)["status"] = -1


def _bad_audit(document: dict[str, object]) -> None:
    """Write an exclusion that is not a boolean."""
    _member(document, "audit")["excludes_69"] = "yes"


def _outputs_object(document: dict[str, object]) -> None:
    """Write the outputs as an object instead of a list."""
    document["outputs"] = {}


def _review_list(document: dict[str, object]) -> None:
    """Write a review that is not an object."""
    document["review"] = []


def _other_files(document: dict[str, object]) -> None:
    """List another set of files."""
    document["files"] = {CLIFF_TOML: "0" * 64}


@pytest.mark.parametrize("change", [
    pytest.param(_extra_member, id="unknown-member"),
    pytest.param(_missing_member, id="missing-member"),
    pytest.param(_other_schema, id="schema"),
    pytest.param(_drop_commit, id="missing-input"),
    pytest.param(_mistype_size, id="mistyped"),
    pytest.param(_bad_digest, id="malformed-digest"),
    pytest.param(_bad_repository, id="repository"),
    pytest.param(_bad_hunk, id="hunk"),
    pytest.param(_bad_status, id="status"),
    pytest.param(_bad_audit, id="audit"),
    pytest.param(_review_list, id="review"),
    pytest.param(_outputs_object, id="outputs-not-list"),
])
def test_the_reader_refuses_any_other_shape(change: Callable[[dict[str, object]], None], tmp_path: Path) -> None:
    """A strict schema 1 reader: every member present and of its own form, nothing else."""
    place_bundle(tmp_path)
    _rewrite(tmp_path, change)
    with pytest.raises(BundleError, match=BUNDLE_FILE):
        read(tmp_path)


def test_a_repeated_key_and_a_document_that_is_not_an_object_are_refused(tmp_path: Path) -> None:
    """Duplicate keys are ambiguous; a list is not a bundle."""
    place_bundle(tmp_path)
    content = (tmp_path / BUNDLE_FILE).read_text(encoding="utf-8")
    (tmp_path / BUNDLE_FILE).write_text(content.replace('"schema": 1,', '"schema": 1, "schema": 1,', 1), encoding="utf-8")
    with pytest.raises(BundleError, match="Duplicate"):
        read(tmp_path)
    (tmp_path / BUNDLE_FILE).write_text("[]", encoding="utf-8")
    with pytest.raises(BundleError, match="not an object"):
        read(tmp_path)


@pytest.mark.parametrize("name", [CLIFF_TOML, trust_name(PIN), trust_name(BASELINE)])
def test_a_listed_file_changed_after_the_bundle_recorded_it_is_refused_on_read(name: str, tmp_path: Path) -> None:
    """Each listed digest is checked against the file beside the bundle."""
    place_bundle(tmp_path)
    (tmp_path / name).write_bytes(b"tampered\n")
    with pytest.raises(BundleError, match=rf"{name}.*SHA-256"):
        read(tmp_path)


def test_a_missing_or_unlisted_file_is_refused_on_read(tmp_path: Path) -> None:
    """A listed file must exist, and the listing must name exactly the three files."""
    place_bundle(tmp_path)
    (tmp_path / trust_name(BASELINE)).unlink()
    with pytest.raises(BundleError, match=trust_name(BASELINE)):
        read(tmp_path)
    place_bundle(tmp_path / "other")
    _rewrite(tmp_path / "other", _other_files)
    with pytest.raises(BundleError, match="files"):
        read(tmp_path / "other")


def test_the_bundle_records_a_relative_source_and_the_ranges_it_ran(tmp_path: Path) -> None:
    """The input manifest keeps the source path of `cliff.toml`, its digest and each range."""
    place_bundle(tmp_path)
    inputs = _member(_document(tmp_path), "inputs")
    assert inputs["cliff_toml"] == {"source": "tools/dev_workflow/cliff.toml", "sha256": hashlib.sha256((tmp_path / CLIFF_TOML).read_bytes()).hexdigest(),
                                    "dev_workflow_commit": sample_inputs().cliff_toml.dev_workflow_commit}
    assert inputs["ranges"] == [{"repository": case.repository, "range": case.range} for case in SAMPLE_RANGES]
    assert _entries(inputs, "ranges")[:2] == [{"repository": "llm-shared", "range": None}, {"repository": "llm-shared", "range": "v0.1.0..HEAD"}]
    assert DIFFERING.key == "fixture v0.1.0..v0.2.0-SNAPSHOT"


def test_read_reconciles_each_trust_record_with_the_identity_the_inputs_name(tmp_path: Path) -> None:
    """A recorded identity its trust record does not hold, or a trust record that is not one, is refused on read."""
    inputs = sample_inputs()
    other = dataclasses.replace(inputs.candidates[0], sha256="0" * 64)
    place_bundle(tmp_path / "identity", inputs=dataclasses.replace(inputs, candidates=(other, inputs.candidates[1])))
    with pytest.raises(BundleError, match=r"trust\.2\.7\.0\.json records"):
        read(tmp_path / "identity")
    bundle = place_bundle(tmp_path / "invalid")
    (tmp_path / "invalid" / trust_name(BASELINE)).write_bytes(b"{}\n")
    write(tmp_path / "invalid", dataclasses.replace(bundle, files=file_digests(tmp_path / "invalid", PIN, BASELINE)))
    with pytest.raises(BundleError, match="invalid"):
        read(tmp_path / "invalid")


# eof
