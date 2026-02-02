"""Data models for control files and policy documents."""

from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ControlRequirement(BaseModel):
    """Single control requirement extracted from a policy document."""

    id: str = Field(
        ...,
        description="Requirement ID (e.g., 'AC-2(5)', '1.1.1')",
    )
    title: str = Field(
        ...,
        description="Requirement title or short description",
    )
    description: str = Field(
        ...,
        description="Full requirement text (exact from source, no rewording)",
    )
    rules: list[str] = Field(
        default_factory=list,
        description="Rule IDs that implement this control",
    )
    related_rules: list[str] = Field(
        default_factory=list,
        description="Rule IDs that are related but not directly implementing",
    )
    status: Literal[
        "automated",
        "partially_automated",
        "manual",
        "not_applicable",
        "pending",
    ] = Field(
        default="pending",
        description="Implementation status of this control",
    )
    references: dict[str, list[str]] = Field(
        default_factory=dict,
        description="External references (NIST, CIS, etc.)",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes or comments",
    )
    levels: list[str] = Field(
        default_factory=list,
        description="Compliance levels (e.g., ['low', 'medium', 'high'])",
    )
    section: Optional[str] = Field(
        default=None,
        description="Section identifier this requirement belongs to",
    )


class ControlLevel(BaseModel):
    """Compliance level definition (e.g., Level 1, Level 2)."""

    id: str = Field(..., description="Level identifier (e.g., 'high', 'medium', 'low')")
    title: Optional[str] = Field(
        default=None,
        description="Level title",
    )
    description: Optional[str] = Field(
        default=None,
        description="Level description",
    )
    inherits_from: Optional[str] = Field(
        default=None,
        description="Parent level ID this level inherits from",
    )


class ControlFile(BaseModel):
    """Control framework file representation.

    Supports both legacy format (with description, source_document, includes)
    and ComplianceAsCode format (with policy, source, controls_dir, version).
    """

    id: str = Field(..., description="Policy/framework ID")
    title: str = Field(..., description="Policy/framework name")

    # ComplianceAsCode format fields
    policy: Optional[str] = Field(
        default=None,
        description="Policy name (same as title in CAC format)",
    )
    version: Optional[str] = Field(
        default=None,
        description="Version string (e.g., 'v3r1')",
    )
    source: Optional[str] = Field(
        default=None,
        description="Source URL (CAC format)",
    )
    controls_dir: Optional[str] = Field(
        default=None,
        description="Directory containing individual control files (CAC format)",
    )

    # Legacy format fields (optional for backward compatibility)
    description: Optional[str] = Field(
        default=None,
        description="Policy description",
    )
    source_document: Optional[str] = Field(
        default=None,
        description="Source file path or URL (legacy format)",
    )
    includes: list[str] = Field(
        default_factory=list,
        description="Paths to included control files (legacy format)",
    )

    # Common fields
    controls: list[ControlRequirement] = Field(
        default_factory=list,
        description="List of control requirements",
    )
    levels: Optional[list[ControlLevel]] = Field(
        default=None,
        description="Compliance levels if applicable",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class DocumentSection(BaseModel):
    """Section extracted from a policy document."""

    id: str = Field(..., description="Section identifier")
    title: str = Field(..., description="Section title")
    level: int = Field(..., description="Heading level (1-6)")
    content: str = Field(..., description="Section content text")
    subsections: list["DocumentSection"] = Field(
        default_factory=list,
        description="Nested subsections",
    )
    parent_id: Optional[str] = Field(
        default=None,
        description="Parent section ID if nested",
    )


class ExtractedRequirement(BaseModel):
    """Requirement extracted from document before structuring."""

    text: str = Field(..., description="Exact requirement text from document")
    section_id: str = Field(..., description="Section this requirement belongs to")
    section_title: str = Field(..., description="Section title")
    potential_id: Optional[str] = Field(
        default=None,
        description="Potential requirement ID if detected",
    )
    context: Optional[str] = Field(
        default=None,
        description="Surrounding context or notes",
    )


class ParsedDocument(BaseModel):
    """Parsed security policy document."""

    title: str = Field(..., description="Document title")
    sections: list[DocumentSection] = Field(
        default_factory=list,
        description="Document sections hierarchy",
    )
    requirements: list[ExtractedRequirement] = Field(
        default_factory=list,
        description="Extracted requirements",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Document metadata (author, date, version, etc.)",
    )
    source_path: Optional[str] = Field(
        default=None,
        description="Source file path or URL",
    )
    source_type: Literal["pdf", "markdown", "text", "html"] = Field(
        ...,
        description="Source document type",
    )
    parsed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when document was parsed",
    )


class RuleSuggestion(BaseModel):
    """AI-suggested rule mapping for a requirement."""

    rule_id: str = Field(..., description="Suggested rule ID")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)",
    )
    reasoning: str = Field(
        ...,
        description="Explanation for why this rule was suggested",
    )
    match_type: Literal["exact_ref", "keyword", "semantic", "description"] = Field(
        ...,
        description="Type of match that led to this suggestion",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the suggestion",
    )


class ControlGenerationResult(BaseModel):
    """Result of control file generation."""

    policy_id: str = Field(..., description="Generated policy ID")
    parent_file_path: Path = Field(..., description="Path to parent control file")
    requirement_files: list[Path] = Field(
        default_factory=list,
        description="Paths to individual requirement files",
    )
    total_requirements: int = Field(..., description="Total requirements generated")
    sections: list[str] = Field(
        default_factory=list,
        description="Section identifiers created",
    )
    success: bool = Field(..., description="Whether generation was successful")
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Any warnings generated",
    )


class ControlValidationResult(BaseModel):
    """Result of control file validation."""

    valid: bool = Field(..., description="Whether validation passed")
    errors: list[str] = Field(
        default_factory=list,
        description="Validation errors",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Validation warnings",
    )
    file_path: Optional[Path] = Field(
        default=None,
        description="Path to validated file",
    )


class ControlReviewReport(BaseModel):
    """Report from reviewing generated control files."""

    policy_id: str = Field(..., description="Policy ID being reviewed")
    total_requirements: int = Field(..., description="Total requirements")
    requirements_with_rules: int = Field(
        ...,
        description="Requirements with at least one rule mapped",
    )
    requirements_without_rules: int = Field(
        ...,
        description="Requirements with no rules mapped",
    )
    validation_result: ControlValidationResult = Field(
        ...,
        description="Validation results",
    )
    text_comparisons: list[dict[str, str]] = Field(
        default_factory=list,
        description="Text comparison results",
    )
    rule_suggestions: dict[str, list[RuleSuggestion]] = Field(
        default_factory=dict,
        description="AI rule suggestions per requirement",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues found during review",
    )


class ControlUpdateResult(BaseModel):
    """Result of updating an existing control file."""

    file_path: Path = Field(..., description="Path to updated control file")
    requirements_added: int = Field(
        ...,
        description="Number of requirements added",
    )
    requirements_updated: int = Field(
        ...,
        description="Number of requirements updated",
    )
    requirements_unchanged: int = Field(
        ...,
        description="Number of requirements unchanged",
    )
    success: bool = Field(..., description="Whether update was successful")
    errors: list[str] = Field(
        default_factory=list,
        description="Errors encountered",
    )
