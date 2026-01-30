"""Rule data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RuleSearchResult(BaseModel):
    """Search result for a rule."""

    rule_id: str = Field(..., description="Rule identifier")
    title: str = Field(..., description="Rule title")
    severity: str = Field(..., description="Rule severity (low, medium, high, unknown)")
    description: Optional[str] = Field(None, description="Short description")
    products: List[str] = Field(
        default_factory=list, description="Products this rule applies to"
    )
    file_path: str = Field(..., description="Path to rule.yml file")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "rule_id": "sshd_set_idle_timeout",
                "title": "Set SSH Idle Timeout Interval",
                "severity": "medium",
                "description": "Configure SSH to automatically terminate idle sessions",
                "products": ["rhel7", "rhel8", "rhel9", "fedora"],
                "file_path": "linux_os/guide/services/ssh/ssh_server/sshd_set_idle_timeout/rule.yml",
            }
        }


class RuleIdentifiers(BaseModel):
    """Rule identifiers."""

    cce: Optional[str] = Field(None, description="CCE identifier")
    cis: Optional[List[str]] = Field(None, description="CIS benchmark references")
    nist: Optional[List[str]] = Field(None, description="NIST control references")
    stigid: Optional[str] = Field(None, description="STIG identifier")

    class Config:
        """Pydantic config."""

        extra = "allow"  # Allow additional identifiers


class RuleReferences(BaseModel):
    """Rule references to compliance frameworks."""

    nist: List[str] = Field(default_factory=list, description="NIST SP 800-53 references")
    cis: List[str] = Field(default_factory=list, description="CIS Benchmark references")
    cui: List[str] = Field(default_factory=list, description="CUI references")
    disa: List[str] = Field(default_factory=list, description="DISA STIG references")
    isa62443: List[str] = Field(
        default_factory=list, description="ISA-62443 references"
    )
    pcidss: List[str] = Field(default_factory=list, description="PCI-DSS references")
    hipaa: List[str] = Field(default_factory=list, description="HIPAA references")

    class Config:
        """Pydantic config."""

        extra = "allow"  # Allow additional reference frameworks


class RuleRenderedContent(BaseModel):
    """Rendered content for a rule (from build artifacts)."""

    product: str = Field(..., description="Product this was rendered for")
    rendered_yaml: Optional[str] = Field(
        None, description="Fully rendered YAML (variables expanded)"
    )
    rendered_oval: Optional[str] = Field(
        None, description="Rendered OVAL check content"
    )
    rendered_remediations: Dict[str, str] = Field(
        default_factory=dict, description="Rendered remediation scripts by type"
    )
    build_path: str = Field(..., description="Path to build artifact")
    build_time: Optional[datetime] = Field(None, description="When this was built")

    # Metadata (always included, even in summary mode)
    yaml_size: int = Field(default=0, description="Size of rendered YAML in bytes")
    oval_size: int = Field(default=0, description="Size of rendered OVAL in bytes")
    remediation_sizes: Dict[str, int] = Field(
        default_factory=dict, description="Sizes of remediations by type"
    )
    has_yaml: bool = Field(default=False, description="Whether YAML is available")
    has_oval: bool = Field(default=False, description="Whether OVAL is available")
    available_remediations: list[str] = Field(
        default_factory=list, description="Available remediation types"
    )


class RuleDetails(BaseModel):
    """Detailed information about a rule."""

    rule_id: str = Field(..., description="Rule identifier")
    title: str = Field(..., description="Rule title")
    description: str = Field(..., description="Full description")
    rationale: Optional[str] = Field(None, description="Rationale for the rule")
    severity: str = Field(..., description="Severity level")
    identifiers: RuleIdentifiers = Field(
        default_factory=RuleIdentifiers, description="Rule identifiers"
    )
    references: RuleReferences = Field(
        default_factory=RuleReferences, description="Compliance framework references"
    )
    products: List[str] = Field(
        default_factory=list, description="Applicable products"
    )
    platforms: List[str] = Field(
        default_factory=list, description="Applicable platforms"
    )
    remediations: Dict[str, bool] = Field(
        default_factory=dict,
        description="Available remediations (bash, ansible, anaconda, etc.)",
    )
    checks: Dict[str, bool] = Field(
        default_factory=dict, description="Available checks (oval, etc.)"
    )
    test_scenarios: List[str] = Field(
        default_factory=list, description="Available test scenarios"
    )
    file_path: str = Field(..., description="Path to rule.yml file")
    rule_dir: str = Field(..., description="Path to rule directory")
    last_modified: Optional[datetime] = Field(
        None, description="Last modification timestamp"
    )
    template: Optional[Dict[str, Any]] = Field(
        None, description="Template information if rule uses a template"
    )
    rendered: Optional[Dict[str, RuleRenderedContent]] = Field(
        None,
        description="Rendered content from build artifacts, keyed by product. "
        "Only populated if include_rendered=True and builds exist.",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "rule_id": "sshd_set_idle_timeout",
                "title": "Set SSH Idle Timeout Interval",
                "description": "SSH allows administrators to set an idle timeout...",
                "rationale": "Terminating an idle session...",
                "severity": "medium",
                "identifiers": {"cce": "CCE-80906-3", "stigid": "RHEL-09-255030"},
                "references": {
                    "nist": ["AC-2(5)", "SC-10"],
                    "disa": ["RHEL-09-255030"],
                },
                "products": ["rhel7", "rhel8", "rhel9"],
                "platforms": ["machine"],
                "remediations": {"bash": True, "ansible": True, "anaconda": True},
                "checks": {"oval": True},
                "test_scenarios": ["correct_value.pass.sh", "wrong_value.fail.sh"],
                "file_path": "linux_os/guide/services/ssh/ssh_server/sshd_set_idle_timeout/rule.yml",
                "rule_dir": "linux_os/guide/services/ssh/ssh_server/sshd_set_idle_timeout",
            }
        }


class ValidationError(BaseModel):
    """Validation error details."""

    field: str = Field(..., description="Field or location of error")
    error: str = Field(..., description="Error message")
    line: Optional[int] = Field(None, description="Line number if applicable")
    suggestion: Optional[str] = Field(None, description="Suggested fix")


class ValidationResult(BaseModel):
    """Result of rule validation."""

    valid: bool = Field(..., description="Whether validation passed")
    errors: List[ValidationError] = Field(
        default_factory=list, description="Validation errors"
    )
    warnings: List[ValidationError] = Field(
        default_factory=list, description="Validation warnings"
    )
    fixes_applied: List[str] = Field(
        default_factory=list, description="Auto-fixes that were applied"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "valid": False,
                "errors": [
                    {
                        "field": "severity",
                        "error": "Invalid severity value 'critical'",
                        "line": 5,
                        "suggestion": "Use one of: low, medium, high, unknown",
                    }
                ],
                "warnings": [
                    {
                        "field": "references.nist",
                        "error": "NIST reference format may be incorrect",
                        "line": 12,
                    }
                ],
                "fixes_applied": [],
            }
        }
