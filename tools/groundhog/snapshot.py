"""Source snapshot behind the ghog day noop (Q28).

A ``ghog day`` walk records a digest of the project's Python files (plus the
gate configuration files) into ``a.ghog.day.ok`` in the project's artifact
home, beside the proof it established. The next walk recomputes the digest
first: when nothing changed and the saved proof meets the request, the walk is
a noop — chained instructions that each call the walk (implement-missing-step
routing through split-large-file, for example) pay for it once. Any file
change, addition or removal moves the digest and the walk runs again;
``--force`` overrides the marker.

The digest reads file paths, sizes and mtimes only (no content), so it
stays fast on large trees; unreadable files are skipped, which biases
toward re-walking, never toward a wrong noop.

Fix: the marker moves from the project root into the review artifact home
(``.reviews`` unless ``.review-artifacts.ini`` declares another home), where
every ``a.*`` working file now lives (``rules/artifact_files.md``). The path
comes from ``tools.artifact_home.artifact_path``, which prepares the home and
moves a marker left at the root by an older run into it once. A home that
cannot be prepared reads as no marker, so the walk runs again.

Fix: the artifact home itself is left out of the digest. Helper scripts and
their outputs now live there, and editing one must not force a new walk of
the project's source. The home is resolved read-only; an invalid declaration
falls back to the default ``.reviews``.

Fix (v0.13.0 full_suite_levels, Step 1): add the key=value proof marker of the
leveled walk, still unused by the walk until Step 2 switches to it. A
:class:`ProofMarker` holds five lines (``scope``, ``fingerprint``, ``timing``,
``digest``, ``proof``); its strict reader turns any missing key, unknown
value, extra line, undecodable or legacy one-line marker into no proof; its
writer goes through a temporary file then an atomic replace, a failure logged
and never raised. Each scope has its own marker (:func:`marker_path_for`):
``a.ghog.day.ok`` for the whole suite, ``a.ghog.day.<group>.ok`` for a group.
:func:`source_files` is public so one tree walk can feed both the digest and
the group membership, and :func:`timing_fingerprint` hashes the duration gate
inputs (the active gate floor and the effective exclusion entries, line 1 of
the floor file left out).

Fix (v0.13.0 full_suite_levels, Step 2): the walk switches to the proof
marker. The one-line digest writer and its comparison are gone, so no walk
mixes the old and the new marker; a legacy one-line marker now reads as no
proof. :func:`effective_proof` is the one read of a scope's saved proof: it
computes the digest, reads that scope's marker and the timing fingerprint, and
applies ``proof.effective_saved``; the walk's noop and upgrade decision uses
it, and so will the request evidence. :func:`save_proof` rewrites the marker
with the proof a walk left valid, or removes it when that proof is
``unproven``, a home that cannot be prepared logged and never raised.
:meth:`EffectiveProof.on_sources` moves that proof to the digest a walk's
test steps run on, once check.bat may have fixed sources.
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.artifact_home import artifact_path
from tools.groundhog import exclusions, floor
from tools.groundhog.levels import FullLevel, level_from_token
from tools.groundhog.proof import effective_saved
from tools.review_artifact_configuration import ReviewArtifactConfiguration

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

LOGGER = logging.getLogger("groundhog")

# The marker written by a green ghog day walk (Q28), now the whole-suite one.
MARKER_FILE_NAME: Final = "a.ghog.day.ok"
# The scope key of the whole suite, and the prefix of a group's scope key.
WHOLE_SCOPE_KEY: Final = "whole"
GROUP_SCOPE_PREFIX: Final = "group:"
# The fixed scope fingerprint of the whole suite, which has no patterns.
WHOLE_SCOPE_FINGERPRINT: Final = hashlib.sha256(b"scope=whole").hexdigest()
# The five marker keys, one line each, in this order.
_MARKER_KEYS: Final = ("scope", "fingerprint", "timing", "digest", "proof")
# The keys holding a sha256 hex value.
_SHA_KEYS: Final = ("fingerprint", "timing", "digest")
_SHA256_RE: Final = re.compile(r"[0-9a-f]{64}")
# A group name: a lowercase letter, then lowercase letters, digits, - and _.
_GROUP_NAME_RE: Final = re.compile(r"[a-z][a-z0-9_-]*")
# Folders never part of the source snapshot.
_EXCLUDED_DIRS: Final = frozenset(
    {
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "htmlcov",
        "node_modules",
        "venv",
        "venvs",
    },
)
# Non-Python files that move the gates, part of the snapshot.
_CONFIG_FILES: Final = ("pyproject.toml", ".coveragerc", "setup.cfg", "check.bat")
# The default artifact home, excluded when the declaration cannot be read.
_DEFAULT_HOME: Final = ".reviews"


@dataclass(frozen=True)
class ProofMarker:
    """The saved proof of one scope, one key=value line per field.

    Attributes:
        scope: The scope key, ``whole`` or ``group:<name>``.
        fingerprint: The scope fingerprint the proof was earned on.
        timing: The duration gate fingerprint the proof was earned on.
        digest: The source digest the proof was earned on.
        proof: The proof level, ``none`` to ``speed``.
    """

    scope: str
    fingerprint: str
    timing: str
    digest: str
    proof: FullLevel


@dataclass(frozen=True)
class EffectiveProof:
    """The saved proof still valid for the current sources of one scope.

    Attributes:
        digest: The current source digest, the one a new marker records.
        proof: The valid saved proof, ``None`` when none holds.
    """

    digest: str
    proof: FullLevel | None

    def on_sources(self, digest: str) -> EffectiveProof:
        """Return the saved proof still valid once the sources hash to ``digest``.

        check.bat may fix sources before the test steps run: a saved proof
        holds only for the digest it was matched on, so a moved digest keeps
        none.

        Args:
            digest: The source digest the next steps run on.

        Returns:
            This proof when the digest did not move, else no saved proof on the
            new digest.
        """
        return self if digest == self.digest else EffectiveProof(digest, None)


def marker_path(root: Path) -> Path:
    """Return the day marker path for a project root.

    Args:
        root: The project root directory.

    Returns:
        The ``a.ghog.day.ok`` path in the artifact home of that root, a
        root copy left by an older run moved there first.

    Raises:
        ValueError: When the artifact home cannot be prepared.
    """
    return artifact_path(root, MARKER_FILE_NAME)


def marker_path_for(root: Path, scope_key: str) -> Path:
    """Return the proof marker path of one scope.

    Args:
        root: The project root directory.
        scope_key: ``whole`` or ``group:<name>``.

    Returns:
        ``a.ghog.day.ok`` for the whole suite, ``a.ghog.day.<name>.ok`` for a
        group, in the artifact home of that root.

    Raises:
        ValueError: When the scope key is unknown, or the artifact home
            cannot be prepared.
    """
    name = _marker_file_name(scope_key)
    if name is None:
        message = f"unknown proof scope: {scope_key!r}"
        raise ValueError(message)
    return artifact_path(root, name)


def read_proof_marker(path: Path) -> ProofMarker | None:
    """Read one proof marker strictly.

    Args:
        path: The marker path.

    Returns:
        The marker, or ``None`` when it is absent, unreadable, undecodable,
        a legacy one-line digest, or not exactly the five known keys in order
        with known values.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    return _parse_marker(text)


def write_proof_marker(path: Path, marker: ProofMarker) -> None:
    """Write one proof marker atomically: a temporary file, then a replace.

    A reader sees the old or the new marker, never a mix. A write failure is
    logged, never raised.

    Args:
        path: The marker path.
        marker: The marker to write.
    """
    side = path.with_name(f"{path.name}.tmp")
    values = (marker.scope, marker.fingerprint, marker.timing, marker.digest, marker.proof.token)
    text = "".join(f"{key}={value}\n" for key, value in zip(_MARKER_KEYS, values, strict=True))
    try:
        side.write_text(text, encoding="utf-8")
        side.replace(path)
    except OSError as error:
        LOGGER.info("ghog: could not write %s: %s", path.name, error)


def remove_proof_marker(path: Path) -> None:
    """Remove one proof marker, as an ``unproven`` walk does.

    A missing marker is fine; a removal failure is logged, never raised.

    Args:
        path: The marker path.
    """
    try:
        path.unlink(missing_ok=True)
    except OSError as error:
        LOGGER.info("ghog: could not remove %s: %s", path.name, error)


def timing_fingerprint(root: Path) -> str:
    """Digest the duration gate inputs: the gate floor and the exclusions.

    Line 1 of the floor file, the write-only auto floor, is left out, so a run
    that only records its auto floor keeps the fingerprint.

    Args:
        root: The project root directory.

    Returns:
        A hex digest over the active gate floor (line 2, else the default)
        and the effective exclusion entries, in file order.
    """
    hasher = hashlib.sha256()
    hasher.update(f"floor={floor.active_floor(floor.read_floor(root))!r}\n".encode())
    for node, seconds in exclusions.read_exclusions(root).items():
        hasher.update(f"{node} = {seconds!r}\n".encode())
    return hasher.hexdigest()


def source_digest(root: Path, files: Sequence[Path] | None = None) -> str:
    """Digest the project's Python files and gate configuration.

    Args:
        root: The project root directory.
        files: The sorted snapshot files of :func:`source_files`, when the
            caller already walked the tree; ``None`` walks it here.

    Returns:
        A hex digest over the sorted (path, mtime, size) of every
        Python file outside the excluded folders, plus the gate
        configuration files; unreadable files are skipped.
    """
    hasher = hashlib.sha256()
    for path in source_files(root) if files is None else files:
        with contextlib.suppress(OSError):
            stat = path.stat()
            rel = path.relative_to(root).as_posix()
            hasher.update(f"{rel}|{stat.st_mtime_ns}|{stat.st_size}\n".encode())
    return hasher.hexdigest()


def effective_proof(
    root: Path,
    scope_key: str,
    fingerprint: str,
    files: Sequence[Path] | None = None,
) -> EffectiveProof:
    """Read the saved proof of one scope that still holds for the sources.

    The one rule turning a marker into currently valid proof: scope,
    fingerprint and digest must all match, then a timing mismatch caps the
    proof at ``cov`` (``proof.effective_saved``). Only this scope's marker is
    read; the timing fingerprint is computed only when a marker was read.

    Args:
        root: The project root directory.
        scope_key: The scope key, ``whole`` or ``group:<name>``.
        fingerprint: The current scope fingerprint.
        files: The sorted snapshot files, when the caller already walked the
            tree; ``None`` walks it here.

    Returns:
        The current digest and the valid saved proof; no proof when the
        marker is absent, unreadable, legacy or stale, or when the artifact
        home cannot be prepared (the safe direction is to walk again).
    """
    digest = source_digest(root, files)
    try:
        marker = read_proof_marker(marker_path_for(root, scope_key))
    except (OSError, ValueError):
        return EffectiveProof(digest, None)
    if marker is None:
        return EffectiveProof(digest, None)
    saved = effective_saved(
        marker,
        scope_key=scope_key,
        fingerprint=fingerprint,
        digest=digest,
        timing=timing_fingerprint(root),
    )
    return EffectiveProof(digest, saved)


def save_proof(
    root: Path,
    scope_key: str,
    fingerprint: str,
    digest: str,
    proof: FullLevel | None,
) -> None:
    """Record the proof a walk left valid for one scope.

    The timing fingerprint is computed now, after the walk's own writes, so a
    ``speed`` walk that ratchets an exclusion keeps its own proof.

    Args:
        root: The project root directory.
        scope_key: The scope key, ``whole`` or ``group:<name>``.
        fingerprint: The scope fingerprint the proof was earned on.
        digest: The source digest the walk ran on.
        proof: The proof to record; ``None`` (``unproven``) removes the
            marker.
    """
    try:
        path = marker_path_for(root, scope_key)
    except (OSError, ValueError) as error:
        LOGGER.info("ghog: could not record the proof marker: %s", error)
        return
    if proof is None:
        remove_proof_marker(path)
        return
    marker = ProofMarker(scope_key, fingerprint, timing_fingerprint(root), digest, proof)
    write_proof_marker(path, marker)


def source_files(root: Path) -> list[Path]:
    """List the snapshot files, sorted for a stable digest.

    The one tree walk of an invocation: the digest and, from Step 3 on, the
    group membership both read this list.

    Args:
        root: The project root directory.

    Returns:
        The Python files outside the excluded folders and the artifact
        home, plus the gate configuration files that exist.
    """
    home = _artifact_home_parts(root)
    files = [
        path
        for path in root.rglob("*.py")
        if not _excluded(path, root)
        and path.relative_to(root).parts[: len(home)] != home
    ]
    files.extend(
        root / name for name in _CONFIG_FILES if (root / name).is_file()
    )
    return sorted(files)


def _artifact_home_parts(root: Path) -> tuple[str, ...]:
    """Return the artifact home as path parts below the root, without creating it.

    Args:
        root: The project root directory.

    Returns:
        The parts of the configured home relative to the root, such as
        ``(".reviews",)``, or the default home's parts when the declaration
        cannot be read.
    """
    try:
        configuration = ReviewArtifactConfiguration.load(root)
    except ValueError:
        return (_DEFAULT_HOME,)
    return configuration.home.relative_to(configuration.project_root).parts


def _excluded(path: Path, root: Path) -> bool:
    """Tell whether a file sits under an excluded folder.

    Args:
        path: The candidate file.
        root: The project root directory.

    Returns:
        True when any parent folder below the root is excluded.
    """
    return any(
        part in _EXCLUDED_DIRS for part in path.relative_to(root).parts[:-1]
    )


def _marker_file_name(scope_key: str) -> str | None:
    """Return the marker file name of one scope key.

    Args:
        scope_key: The candidate scope key.

    Returns:
        The file name, or ``None`` for an unknown key or an invalid group
        name.
    """
    if scope_key == WHOLE_SCOPE_KEY:
        return MARKER_FILE_NAME
    name = scope_key.removeprefix(GROUP_SCOPE_PREFIX)
    if name == scope_key or _GROUP_NAME_RE.fullmatch(name) is None:
        return None
    return f"a.ghog.day.{name}.ok"


def _marker_values(text: str) -> dict[str, str] | None:
    """Split a marker into its five values, checking only its shape.

    Args:
        text: The marker text.

    Returns:
        The values by key, or ``None`` unless the text is exactly the five
        ``key=value`` lines in order.
    """
    pairs = [line.partition("=") for line in text.splitlines()]
    if tuple(key for key, _, _ in pairs) != _MARKER_KEYS:
        return None
    if not all(separator for _, separator, _ in pairs):
        return None
    return {key: value for key, _, value in pairs}


def _parse_marker(text: str) -> ProofMarker | None:
    """Parse the five key=value lines of a marker strictly.

    Args:
        text: The marker text.

    Returns:
        The marker, or ``None`` on any missing, extra, reordered or
        malformed line, or any unknown value.
    """
    values = _marker_values(text)
    if values is None:
        return None
    proof = level_from_token(values["proof"])
    if proof is None or _marker_file_name(values["scope"]) is None:
        return None
    if not all(_SHA256_RE.fullmatch(values[key]) for key in _SHA_KEYS):
        return None
    return ProofMarker(
        scope=values["scope"],
        fingerprint=values["fingerprint"],
        timing=values["timing"],
        digest=values["digest"],
        proof=proof,
    )


# eof
