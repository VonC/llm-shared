"""uv workspaces and Python local links are rejected before any write.

Step 5 of v0.14.0 version-sources: `[tool.uv.workspace]` in a participating
file fails, with or without a lock; a tool-only project root whose `members`,
net of `exclude`, match a declared component fails, and one whose members
match none stays outside participation. A lock whose `[manifest]` lists
members fails, so does a `workspace = true` source. A `path` source, or a
`file:` reference in dependencies, optional dependencies or dependency
groups, that resolves into another participating root fails naming both
components, also through detection with `.release.ini` components; one that
resolves elsewhere, and Git or URL sources, stay external and unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    RootSettings,
    pyproject_toml,
    uv_lock,
    version_project,
    version_txt,
    write_file,
)
from tools.release_workflow.sources import detection, python
from tools.release_workflow.sources.model import FileView, SourceError

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import Detection

_LINK = "local links between participating components are unsupported"


def _settings(root: Path) -> RootSettings:
    """Declare the `api` and `web` components below the project root."""
    for name in ("api", "web"):
        (root / name).mkdir(exist_ok=True)
    return RootSettings(root, components={"api": root / "api", "web": root / "web"})


def _manifest(dependencies: str = "[]", extra: str = "") -> bytes:
    """Build the `api` component manifest with its dependencies and more tables."""
    return f'[project]\nname = "api"\nversion = "0.13.0"\ndependencies = {dependencies}\n{extra}'.encode()


def _detect_api(root: Path, manifest: bytes) -> Detection:
    """Write the manifest at the `api` component root and detect there."""
    settings = _settings(root)
    write_file(root, "api/pyproject.toml", manifest)
    return python.ADAPTER.detect(root / "api", FileView(), settings)


@pytest.mark.parametrize("lock", [True, False])
def test_a_participating_workspace_root_fails(tmp_path: Path, *, lock: bool) -> None:
    """A project declaring a workspace is unsupported, whether or not it is locked."""
    write_file(tmp_path, "pyproject.toml", pyproject_toml(extra='\n[tool.uv.workspace]\nmembers = ["packages/*"]\n'))
    if lock:
        write_file(tmp_path, "uv.lock", uv_lock())
    with pytest.raises(SourceError, match=r"pyproject\.toml declares \[tool\.uv\.workspace\]: uv workspaces are unsupported"):
        python.ADAPTER.detect(tmp_path, FileView(), RootSettings(tmp_path))


@pytest.mark.parametrize(("members", "component"), [('["*"]', "api"), ('["./API/", "docs"]', "api")])
def test_a_tool_only_root_workspace_including_a_component_fails(tmp_path: Path, members: str, component: str) -> None:
    """Members net of `exclude` that match a component root fail, naming it; case follows the filesystem."""
    settings = _settings(tmp_path)
    write_file(tmp_path, "pyproject.toml", f'[tool.uv.workspace]\nmembers = {members}\nexclude = ["web"]\n'.encode())
    match = rf"\[tool\.uv\.workspace\] members include \[component:{component}\] \({component}\): uv workspaces are unsupported"
    with pytest.raises(SourceError, match=match):
        python.ADAPTER.detect(tmp_path, FileView(), settings)


@pytest.mark.parametrize("workspace", ['members = ["packages/*"]\n', 'members = ["*"]\nexclude = ["*"]\n', "members = []\n"])
def test_a_tool_only_root_workspace_without_components_stays_outside(tmp_path: Path, workspace: str) -> None:
    """A workspace whose members include no participating root is only listed."""
    settings = _settings(tmp_path)
    write_file(tmp_path, "pyproject.toml", f"[tool.uv.workspace]\n{workspace}".encode())
    found = python.ADAPTER.detect(tmp_path, FileView(), settings)
    assert (found.sources, [record.status for record in found.visible]) == ((), ["not-participating tool-only"])


def test_a_tool_only_workspace_below_the_project_root_is_only_listed(tmp_path: Path) -> None:
    """Only the project root's workspace members are compared with the component roots."""
    found = _detect_api(tmp_path, b'[tool.uv.workspace]\nmembers = ["../*"]\n')
    assert (found.sources, [record.path.parent for record in found.visible]) == ((), [tmp_path / "api"])


def test_a_shared_workspace_lock_fails(tmp_path: Path) -> None:
    """A lock whose manifest lists members serves a workspace."""
    write_file(tmp_path, "pyproject.toml", pyproject_toml())
    write_file(tmp_path, "uv.lock", uv_lock().replace(b"\n\n", b'\n\n[manifest]\nmembers = ["demo-app", "lib"]\n\n', 1))
    with pytest.raises(SourceError, match=r"uv\.lock: \[manifest\] lists workspace members: a shared workspace lock is unsupported"):
        python.ADAPTER.detect(tmp_path, FileView(), RootSettings(tmp_path))


def test_a_workspace_reference_fails(tmp_path: Path) -> None:
    """`workspace = true` is never read as a path."""
    with pytest.raises(SourceError, match=r"\[tool\.uv\.sources\] lib is a workspace reference: uv workspaces are unsupported"):
        _detect_api(tmp_path, _manifest(extra="[tool.uv.sources]\nlib = { workspace = true }\n"))


@pytest.mark.parametrize(("dependencies", "extra", "location", "other"), [
    ("[]", '[tool.uv.sources]\nweb = { path = "../web", editable = true }\n', r"\[tool\.uv\.sources\] web path '\.\./web'", r"\[component:web\]"),
    ("[]", "[tool.uv.sources]\nweb = [{ path = '../WEB/', marker = \"sys_platform == 'win32'\" }, { index = \"pypi\" }]\n",
     r"\[tool\.uv\.sources\] web path", r"\[component:web\]"),
    ('["web @ file:../web"]', "", r"\[project\] dependencies 'web @ file:\.\./web'", r"\[component:web\]"),
    ("[]", '[project.optional-dependencies]\nall = ["web @ file:///${PROJECT_ROOT}/../web ; python_version >= \'3.13\'"]\n',
     r"\[project\.optional-dependencies\] all", r"\[component:web\]"),
    ("[]", '[dependency-groups]\ndev = [{ include-group = "x" }, "root @ ROOT_URI"]\nx = []\n', r"\[dependency-groups\] dev 'root @ file:", "the project root"),
])
def test_local_links_into_another_participating_root_fail(tmp_path: Path, dependencies: str, extra: str, location: str, other: str) -> None:
    """A path or `file:` destination that is a participating root fails, naming both components."""
    manifest = _manifest(dependencies, extra.replace("ROOT_URI", tmp_path.as_uri()))
    with pytest.raises(SourceError, match=rf"api[\\/]pyproject\.toml: {location}.* links \[component:api\] to {other} .*{_LINK}"):
        _detect_api(tmp_path, manifest)


def test_a_link_between_declared_components_fails_through_detection(git_sandbox: GitSandbox) -> None:
    """With `.release.ini` components, the settings name both ends of the link."""
    ini = "[component:api]\nroot = api\n[component:web]\nroot = web\n"
    files = {"version.txt": version_txt("0.13.0"), "api/pyproject.toml": _manifest('["web @ file:../web"]'),
             "web/pyproject.toml": pyproject_toml(name="web")}
    with pytest.raises(SourceError, match=rf"links \[component:api\] to \[component:web\] .*{_LINK}"):
        detection.detect(version_project(git_sandbox, files, ini), FileView())


def test_external_references_stay_unchanged(tmp_path: Path) -> None:
    """Git, URL, index and outside paths are external: the component's version is located as usual."""
    extra = ('[tool.uv.sources]\ngit-lib = { git = "https://github.com/example/lib" }\nwheel = { url = "https://example.org/w.whl" }\n'
             'near = { path = "../vendor/near" }\nfar = { path = "../../outside" }\nmirror = { index = "pypi" }\n'
             '[dependency-groups]\ndev = ["vendored @ file:../vendor/lib", "remote @ https://example.org/r.whl", "requests>=2"]\n')
    found = _detect_api(tmp_path, _manifest('["near", "far", "plain @ file:../vendor/plain"]', extra))
    assert [(source.field, source.value, source.root) for source in found.sources] == [("project.version", "0.13.0", tmp_path / "api")]


# eof
