"""Shared source-model and pure-rule surface for repository Markdown checks."""

from tools.markdown_check.classifier import (
    DocumentClassification,
    DocumentKind,
    classify_document,
)
from tools.markdown_check.models import Finding, MarkdownSource
from tools.markdown_check.rules import evaluate_rules
from tools.markdown_check.source import parse_markdown

__all__ = [
    "DocumentClassification",
    "DocumentKind",
    "Finding",
    "MarkdownSource",
    "classify_document",
    "evaluate_rules",
    "parse_markdown",
]


# eof
