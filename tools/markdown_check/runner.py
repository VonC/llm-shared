"""Git inventory, source evaluation, baseline comparison, and diagnostics."""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Never

from tools.markdown_check.baseline import (
    BaselineError,
    load_baseline,
    normalize_repository_path,
)
from tools.markdown_check.classifier import (
    DocumentClassification,
    DocumentKind,
    classify_document,
    resolve_markdown_target,
)
from tools.markdown_check.policy import MarkdownPolicy, PolicyError, load_policy
from tools.markdown_check.rules import (
    check_ls001,
    check_ls002,
    check_ls003,
    check_md001,
    check_md009,
    check_md012,
    check_md024,
    check_md025,
    check_md032,
    check_md033,
    check_md034,
    check_md038,
    check_md040,
    check_md050,
)
from tools.markdown_check.source import parse_markdown

if TYPE_CHECKING:
    from tools.markdown_check.models import Finding, MarkdownSource

InventoryLoader = Callable[[Path], tuple[str, ...]]
SourceReader = Callable[[PurePosixPath], str]
_FAILURE_EXIT = 1


class InventoryError(RuntimeError):
    """Git could not provide a safe fixed Markdown inventory."""


def _inventory_fail(message: str) -> Never:
    """Raise one consistently constructed inventory error."""
    raise InventoryError(message)


@dataclass(frozen=True, slots=True)
class CheckerResult:
    """Stable output streams and process status for one complete run."""

    stdout: tuple[str, ...]
    stderr: tuple[str, ...]
    exit_code: int


def tracked_markdown_paths(root: Path) -> tuple[str, ...]:
    """Run exactly one `git ls-files` query and normalize Markdown paths."""
    git = shutil.which("git")
    if git is None:
        _inventory_fail("git executable was not found")
    completed = subprocess.run(  # noqa: S603
        [git, "-C", str(root), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        diagnostic = completed.stderr.decode("utf-8", errors="replace").strip()
        _inventory_fail(diagnostic or "git ls-files failed")
    try:
        raw_paths = completed.stdout.decode("utf-8").split("\0")
        paths = {
            normalize_repository_path(path)
            for path in raw_paths
            if path and PurePosixPath(path.replace("\\", "/")).suffix.lower() == ".md"
        }
    except (UnicodeError, BaselineError) as error:
        message = f"invalid git ls-files inventory: {error}"
        raise InventoryError(message) from error
    return tuple(sorted(paths))


def _refine_classification(
    source: MarkdownSource,
    classification: DocumentClassification,
    inventory: frozenset[str],
) -> DocumentClassification:
    """Require one syntactic bounded pointer target to exist in the snapshot."""
    if classification.reason != "bounded-pointer":
        return classification
    if any(
        (target := resolve_markdown_target(source.path, link.target)) is not None
        and target.as_posix() in inventory
        for link in source.links
    ):
        return classification
    return DocumentClassification(DocumentKind.STRUCTURED, "missing-pointer-target")


def _evaluate(
    source: MarkdownSource,
    classification: DocumentClassification,
    policy: MarkdownPolicy,
) -> tuple[Finding, ...]:
    """Run only enabled implemented rules against one parsed source."""
    findings: list[Finding] = []
    simple = {
        "MD001": check_md001,
        "MD009": check_md009,
        "MD012": check_md012,
        "MD024": check_md024,
        "MD025": check_md025,
        "MD032": check_md032,
        "MD034": check_md034,
        "MD038": check_md038,
        "MD040": check_md040,
        "MD050": check_md050,
        "LS003": check_ls003,
    }
    for rule, evaluator in simple.items():
        if rule in policy.enabled_rules:
            findings.extend(evaluator(source))
    if "MD033" in policy.enabled_rules:
        findings.extend(check_md033(source, allowed_elements=policy.allowed_html))
    if "LS001" in policy.enabled_rules:
        findings.extend(check_ls001(source, classification))
    if "LS002" in policy.enabled_rules:
        findings.extend(check_ls002(source, classification))
    return tuple(findings)


def _render(finding: Finding) -> str:
    """Render the stable path:line rule diagnostic contract."""
    return f"{finding.path}:{finding.line}: {finding.rule}: {finding.reason}"


class CheckerRunner:
    """Compose policy, inventory, one source read, rules, and baseline."""

    def __init__(
        self,
        root: Path,
        *,
        inventory_loader: InventoryLoader = tracked_markdown_paths,
        source_reader: SourceReader | None = None,
    ) -> None:
        """Bind one repository and injectable filesystem boundaries."""
        self._root = root.resolve()
        self._inventory_loader = inventory_loader
        self._source_reader = source_reader or self._read_source

    def _read_source(self, path: PurePosixPath) -> str:
        """Read one tracked path once as strict UTF-8 inside the repository."""
        candidate = (self._root / Path(*path.parts)).resolve()
        if not candidate.is_relative_to(self._root):
            message = f"tracked path escapes repository: {path.as_posix()}"
            raise OSError(message)
        return candidate.read_text(encoding="utf-8")

    def run(
        self,
        *,
        policy_path: Path | None = None,
        baseline_path: Path | None = None,
    ) -> CheckerResult:
        """Evaluate one immutable inventory and return deterministic streams."""
        policy_file = policy_path or self._root / ".markdownlint.json"
        baseline_file = baseline_path or self._root / ".markdownlint-baseline.json"
        try:
            policy = load_policy(policy_file)
            baseline = load_baseline(baseline_file)
            paths = self._inventory_loader(self._root)
            inventory = frozenset(normalize_repository_path(path) for path in paths)
        except (PolicyError, BaselineError, InventoryError) as error:
            return CheckerResult((), (f"markdown-check: {error}",), _FAILURE_EXIT)
        findings: list[Finding] = []
        for display_path in sorted(inventory):
            path = PurePosixPath(display_path)
            try:
                markdown = self._source_reader(path)
            except (OSError, UnicodeError) as error:
                return CheckerResult(
                    (),
                    (f"markdown-check: cannot read {display_path}: {error}",),
                    _FAILURE_EXIT,
                )
            source = parse_markdown(path, markdown)
            classification = _refine_classification(
                source,
                classify_document(source),
                inventory,
            )
            findings.extend(_evaluate(source, classification, policy))
        ordered = tuple(
            sorted(
                findings,
                key=lambda item: (item.path, item.line, item.rule, item.reason),
            ),
        )
        comparison = baseline.compare(ordered)
        return CheckerResult(
            tuple(_render(finding) for finding in comparison.blocked_findings),
            comparison.advisories,
            _FAILURE_EXIT if comparison.blocked_findings else 0,
        )


__all__ = ["CheckerResult", "CheckerRunner", "InventoryError", "tracked_markdown_paths"]


# eof
