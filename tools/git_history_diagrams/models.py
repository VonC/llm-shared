"""Data model shared by Git-history scenarios and the SVG renderer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Lane:
    """One named branch lane."""

    key: str
    label: str
    y: int
    color: str


@dataclass(frozen=True)
class Commit:
    """One commit node positioned in a branch lane."""

    key: str
    label: str
    x: int
    lane: str


@dataclass(frozen=True)
class Edge:
    """A parent, merge, or replay relationship between two commits."""

    start: str
    end: str
    kind: str = "history"
    label: str = ""


@dataclass(frozen=True)
class Scenario:
    """A complete Git-history diagram."""

    slug: str
    title: str
    caption: str
    lanes: tuple[Lane, ...]
    commits: tuple[Commit, ...]
    edges: tuple[Edge, ...]


# eof
