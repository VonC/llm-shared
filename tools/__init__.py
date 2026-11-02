"""Utility scripts for code maintenance, formatting, and linting fixes.

This package contains modules for API inspection, guardrail checking, result
dumping, review support, workflow-routing submodules, and shared models that
prevent circular dependencies between the main scripts.
Review scope capture adapters share groundhog's validator and proof rules.
Package exports load on demand so a release child does not import the unrelated
review and Markdown graph. Static imports retain the same public type surface.
"""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools._models import (
        FileAnalysis,
        ImportRecord,
        JSONFileAnalysis,
        JSONInspectionPayload,
        Layer,
        find_project_root,
        infer_layer,
        project_name,
        resolve_paths,
        safe_relative,
        serialize_file_analysis,
    )
    from tools.review_exchange_models import (
        Actor,
        ArchiveKind,
        ArtifactPaths,
        ArtifactState,
        ConfirmationOutcome,
        CoordinationStatus,
        ExchangeIdentity,
        FamilyPolicy,
        IncompleteTransitionKind,
        ReviewConfiguration,
        ReviewContext,
        ReviewDisposition,
        ReviewExchangeError,
        ReviewFamily,
        ReviewRole,
    )
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_models_envelope import Envelope
    from tools.review_exchange_publication import ReviewExchangePublicationMixin
    from tools.spec_review_answer import (
        SpecificationAnswerRender,
        SpecificationAssessment,
        render_specification_answer,
    )
    from tools.spec_review_request import (
        SpecificationRequestRender,
        SpecificationRoundInput,
        render_specification_request,
        specification_context,
    )

_EXPORT_MODULES = {
    **dict.fromkeys(("FileAnalysis", "ImportRecord", "JSONFileAnalysis", "JSONInspectionPayload", "Layer",
                     "find_project_root", "infer_layer", "project_name", "resolve_paths", "safe_relative",
                     "serialize_file_analysis"), "tools._models"),
    **dict.fromkeys(("Actor", "ArchiveKind", "ArtifactPaths", "ArtifactState", "ConfirmationOutcome", "CoordinationStatus",
                     "ExchangeIdentity", "FamilyPolicy", "IncompleteTransitionKind", "ReviewConfiguration", "ReviewContext",
                     "ReviewDisposition", "ReviewExchangeError", "ReviewFamily", "ReviewRole"), "tools.review_exchange_models"),
    "CoordinationRecord": "tools.review_exchange_models_coordination",
    "Envelope": "tools.review_exchange_models_envelope",
    "ReviewExchangePublicationMixin": "tools.review_exchange_publication",
    **dict.fromkeys(("SpecificationAnswerRender", "SpecificationAssessment", "render_specification_answer"), "tools.spec_review_answer"),
    **dict.fromkeys(("SpecificationRequestRender", "SpecificationRoundInput", "render_specification_request",
                     "specification_context"), "tools.spec_review_request"),
}


def __getattr__(name: str) -> object:
    """Resolve the original public object once, preserving ordinary submodule imports."""
    module = _EXPORT_MODULES.get(name)
    if module is None:
        message = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(message)
    value = getattr(import_module(module), name)
    globals()[name] = value
    return value


__all__ = [
    "Actor",
    "ArchiveKind",
    "ArtifactPaths",
    "ArtifactState",
    "ConfirmationOutcome",
    "CoordinationRecord",
    "CoordinationStatus",
    "Envelope",
    "ExchangeIdentity",
    "FamilyPolicy",
    "FileAnalysis",
    "ImportRecord",
    "IncompleteTransitionKind",
    "JSONFileAnalysis",
    "JSONInspectionPayload",
    "Layer",
    "ReviewConfiguration",
    "ReviewContext",
    "ReviewDisposition",
    "ReviewExchangeError",
    "ReviewExchangePublicationMixin",
    "ReviewFamily",
    "ReviewRole",
    "SpecificationAnswerRender",
    "SpecificationAssessment",
    "SpecificationRequestRender",
    "SpecificationRoundInput",
    "find_project_root",
    "infer_layer",
    "project_name",
    "render_specification_answer",
    "render_specification_request",
    "resolve_paths",
    "safe_relative",
    "serialize_file_analysis",
    "specification_context",
]


# eof
