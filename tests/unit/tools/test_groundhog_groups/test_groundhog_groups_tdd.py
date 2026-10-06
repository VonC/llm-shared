"""Group resolution filters pytest files and coverage omissions in one supplied walk."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.groundhog import groups, snapshot

_DECLARATION = "[demo]\ntests =\n    tests/**\nsources =\n    tools/**\n"


def make_project(root: Path) -> list[Path]:
    """Build test, data, conftest and source candidates."""
    (root / ".ghog-groups").write_text(_DECLARATION, encoding="utf-8")
    for name in ("tests/test_x.py", "tests/x_test.py", "tests/conftest.py", "tests/data.py",
                 "tests/data.txt", "tools/x.py", "tools/omit.py"):
        path = root / name
        path.parent.mkdir(exist_ok=True)
        path.touch()
    return snapshot.source_files(root)


def test_default_membership_and_fingerprint(tmp_path: Path) -> None:
    """Default pytest names select tests; data and conftest stay out."""
    files = make_project(tmp_path)
    scope = groups.resolve_group(tmp_path, "demo", files)
    assert scope.test_files == ("tests/test_x.py", "tests/x_test.py")
    assert scope.source_files == ("tools/omit.py", "tools/x.py")
    assert groups.list_groups(tmp_path, files) == [scope]
    assert groups.resolve_group(tmp_path, "demo", list(reversed(files))) == scope
    assert groups.resolve_group(tmp_path, "demo", files[:-1]).fingerprint != scope.fingerprint
    (tmp_path / ".ghog-groups").write_text(_DECLARATION + "    !tools/omit.py\n", encoding="utf-8")
    assert groups.resolve_group(tmp_path, "demo", files).fingerprint != scope.fingerprint


def test_snapshot_configuration_is_not_membership(tmp_path: Path) -> None:
    """The shared snapshot includes configuration alongside Python candidates."""
    make_project(tmp_path)
    config = tmp_path / "pyproject.toml"
    config.write_text('[project]\nname="demo"\n', encoding="utf-8")
    files = snapshot.source_files(tmp_path)
    assert config in files
    scope = groups.resolve_group(tmp_path, "demo", files)
    assert scope.test_files == ("tests/test_x.py", "tests/x_test.py")
    assert scope.source_files == ("tools/omit.py", "tools/x.py")


def test_project_filters_accept_sources_outside_coverage_source(tmp_path: Path) -> None:
    """Pytest patterns and coverage omit filter independently of coverage source."""
    files = make_project(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\npython_files = ["*_test.py", "conftest.py"]\n'
        '[tool.coverage.run]\nsource = ["elsewhere"]\nomit = ["*/omit.py"]\n', encoding="utf-8",
    )
    scope = groups.resolve_group(tmp_path, "demo", files)
    assert scope.test_files == ("tests/x_test.py",)
    assert scope.source_files == ("tools/x.py",)


@pytest.mark.parametrize(("declaration", "name", "cause"), [
    ("not ini", "demo", "malformed"),
    ("[Bad]\ntests=tests/**\nsources=tools/**", "Bad", "name"),
    ("[demo]\ntests=tests/**", "demo", "sources"),
    ("[demo]\nsources=tools/**", "demo", "tests"),
    (_DECLARATION, "missing", "unknown"),
    ("[demo]\ntests=nothing/**\nsources=tools/**", "demo", "test"),
    ("[demo]\ntests=tests/**\nsources=nothing/**", "demo", "source"),
    ("[demo]\ntests=\nsources=tools/**", "demo", "test"),
    ("[DEFAULT]\ntests=tests/**\n[demo]\nsources=tools/**", "demo", "DEFAULT"),
])
def test_invalid_declarations(tmp_path: Path, declaration: str, name: str, cause: str) -> None:
    """Each setup error identifies its cause, including the empty membership side."""
    files = make_project(tmp_path)
    (tmp_path / ".ghog-groups").write_text(declaration, encoding="utf-8")
    with pytest.raises(groups.GroupError, match=cause):
        groups.resolve_group(tmp_path, name, files)


def test_unreadable_declaration(tmp_path: Path) -> None:
    """Missing and undecodable declarations cannot turn into empty groups."""
    with pytest.raises(groups.GroupError, match="unreadable"):
        groups.read_declaration(tmp_path)
    (tmp_path / ".ghog-groups").write_bytes(b"\xff")
    with pytest.raises(groups.GroupError, match="unreadable"):
        groups.read_declaration(tmp_path)


def test_list_reads_declaration_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Listing multiple groups never rereads the declaration per group."""
    files = make_project(tmp_path)
    declaration = tmp_path / ".ghog-groups"
    declaration.write_text(_DECLARATION + _DECLARATION.replace("demo", "other"), encoding="utf-8")
    original = Path.read_text
    reads: list[Path] = []

    def read(path: Path, *_args: object, **_kwargs: object) -> str:
        """Count declaration reads through a text-only seam."""
        if path == declaration:
            reads.append(path)
        return original(path, encoding="utf-8")

    monkeypatch.setattr(Path, "read_text", read)
    assert [scope.name for scope in groups.list_groups(tmp_path, files)] == ["demo", "other"]
    assert reads == [declaration]
