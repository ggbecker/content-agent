"""Data models for cac-content-mcp-server."""

from cac_mcp_server.models.build import (
    BuildArtifact,
    BuildJobId,
    BuildJobStatus,
    BuildJobType,
    BuildStatus,
    DatastreamInfo,
    RenderedRule,
    RenderSearchResult,
)
from cac_mcp_server.models.product import ProductDetails, ProductStats, ProductSummary
from cac_mcp_server.models.profile import (
    ProfileDetails,
    ProfileSummary,
    ScaffoldingResult,
    TemplateParameter,
    TemplateSchema,
    TemplateSummary,
)
from cac_mcp_server.models.rule import (
    RuleDetails,
    RuleIdentifiers,
    RuleReferences,
    RuleRenderedContent,
    RuleSearchResult,
    ValidationError,
    ValidationResult,
)
from cac_mcp_server.models.test import (
    TestJobId,
    TestJobStatus,
    TestResults,
    TestScenarioResult,
    TestScenarioStatus,
)

__all__ = [
    # Build models
    "BuildArtifact",
    "BuildJobId",
    "BuildJobStatus",
    "BuildJobType",
    "BuildStatus",
    "DatastreamInfo",
    "RenderedRule",
    "RenderSearchResult",
    # Product models
    "ProductDetails",
    "ProductStats",
    "ProductSummary",
    # Profile models
    "ProfileDetails",
    "ProfileSummary",
    "ScaffoldingResult",
    "TemplateParameter",
    "TemplateSchema",
    "TemplateSummary",
    # Rule models
    "RuleDetails",
    "RuleIdentifiers",
    "RuleReferences",
    "RuleRenderedContent",
    "RuleSearchResult",
    "ValidationError",
    "ValidationResult",
    # Test models
    "TestJobId",
    "TestJobStatus",
    "TestResults",
    "TestScenarioResult",
    "TestScenarioStatus",
]
