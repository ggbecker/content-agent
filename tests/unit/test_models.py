"""Unit tests for data models."""

import json
from datetime import datetime

import pytest

from content_agent.models import (
    ProductDetails,
    ProductSummary,
    RuleDetails,
    RuleIdentifiers,
    RuleReferences,
    RuleSearchResult,
    ScaffoldingResult,
    TemplateParameter,
    TemplateSchema,
    ValidationError,
    ValidationResult,
)


class TestProductModels:
    """Test product-related models."""

    def test_product_summary_creation(self):
        """Test ProductSummary creation."""
        product = ProductSummary(
            product_id="rhel9",
            name="Red Hat Enterprise Linux 9",
            product_type="rhel",
            version="9",
        )

        assert product.product_id == "rhel9"
        assert product.name == "Red Hat Enterprise Linux 9"
        assert product.product_type == "rhel"
        assert product.version == "9"

    def test_product_summary_json_serialization(self):
        """Test ProductSummary JSON serialization."""
        product = ProductSummary(
            product_id="rhel9",
            name="Red Hat Enterprise Linux 9",
            product_type="rhel",
        )

        json_str = json.dumps(product.model_dump())
        assert "rhel9" in json_str
        assert "Red Hat Enterprise Linux 9" in json_str

    def test_product_details_with_stats(self):
        """Test ProductDetails with statistics."""
        product = ProductDetails(
            product_id="rhel9",
            name="RHEL 9",
            product_type="rhel",
            profiles=["ospp", "stig"],
            benchmark_root="linux_os/guide",
            product_dir="products/rhel9",
        )

        assert len(product.profiles) == 2
        assert "ospp" in product.profiles


class TestRuleModels:
    """Test rule-related models."""

    def test_rule_search_result_creation(self):
        """Test RuleSearchResult creation."""
        rule = RuleSearchResult(
            rule_id="sshd_set_idle_timeout",
            title="Set SSH Idle Timeout",
            severity="medium",
            products=["rhel9"],
            file_path="linux_os/guide/services/ssh/rule.yml",
        )

        assert rule.rule_id == "sshd_set_idle_timeout"
        assert rule.severity == "medium"

    def test_rule_identifiers(self):
        """Test RuleIdentifiers model."""
        identifiers = RuleIdentifiers(
            cce="CCE-12345-6",
            nist=["AC-2(5)", "SC-10"],
            stigid="RHEL-09-255030",
        )

        assert identifiers.cce == "CCE-12345-6"
        assert len(identifiers.nist) == 2

    def test_rule_references(self):
        """Test RuleReferences model."""
        references = RuleReferences(
            nist=["AC-2(5)", "SC-10"],
            disa=["RHEL-09-255030"],
        )

        assert len(references.nist) == 2
        assert len(references.disa) == 1
        assert len(references.cis) == 0  # Default empty

    def test_rule_details_complete(self):
        """Test complete RuleDetails."""
        rule = RuleDetails(
            rule_id="sshd_set_idle_timeout",
            title="Set SSH Idle Timeout",
            description="Configure SSH timeout",
            severity="medium",
            identifiers=RuleIdentifiers(cce="CCE-12345-6"),
            references=RuleReferences(nist=["AC-2(5)"]),
            products=["rhel9"],
            platforms=["machine"],
            remediations={"bash": True, "ansible": True},
            checks={"oval": True},
            test_scenarios=["correct.pass.sh", "wrong.fail.sh"],
            file_path="linux_os/guide/services/ssh/rule.yml",
            rule_dir="linux_os/guide/services/ssh",
        )

        assert rule.rule_id == "sshd_set_idle_timeout"
        assert rule.remediations["bash"] is True
        assert len(rule.test_scenarios) == 2


class TestValidationModels:
    """Test validation-related models."""

    def test_validation_error(self):
        """Test ValidationError model."""
        error = ValidationError(
            field="severity",
            error="Invalid severity value",
            line=5,
            suggestion="Use low, medium, or high",
        )

        assert error.field == "severity"
        assert error.line == 5

    def test_validation_result_success(self):
        """Test ValidationResult for successful validation."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            fixes_applied=[],
        )

        assert result.valid is True
        assert len(result.errors) == 0

    def test_validation_result_with_errors(self):
        """Test ValidationResult with errors."""
        errors = [
            ValidationError(field="title", error="Title is required"),
            ValidationError(field="severity", error="Invalid severity"),
        ]

        result = ValidationResult(
            valid=False,
            errors=errors,
            warnings=[],
            fixes_applied=[],
        )

        assert result.valid is False
        assert len(result.errors) == 2


class TestScaffoldingModels:
    """Test scaffolding-related models."""

    def test_scaffolding_result_success(self):
        """Test ScaffoldingResult for successful generation."""
        result = ScaffoldingResult(
            success=True,
            rule_id="new_rule",
            rule_dir="linux_os/guide/system/new_rule",
            message="Rule created successfully",
            files_created=[
                "linux_os/guide/system/new_rule/rule.yml",
                "linux_os/guide/system/new_rule/bash/",
            ],
        )

        assert result.success is True
        assert result.rule_id == "new_rule"
        assert len(result.files_created) == 2

    def test_scaffolding_result_failure(self):
        """Test ScaffoldingResult for failed generation."""
        result = ScaffoldingResult(
            success=False,
            rule_id="new_rule",
            rule_dir="",
            message="Rule already exists",
            files_created=[],
        )

        assert result.success is False
        assert result.message == "Rule already exists"


class TestTemplateModels:
    """Test template-related models."""

    def test_template_parameter(self):
        """Test TemplateParameter model."""
        param = TemplateParameter(
            name="parameter",
            type="string",
            required=True,
            description="SSH parameter name",
            default="ClientAliveInterval",
        )

        assert param.name == "parameter"
        assert param.required is True

    def test_template_schema(self):
        """Test TemplateSchema model."""
        schema = TemplateSchema(
            name="sshd_lineinfile",
            description="SSH daemon configuration",
            parameters=[
                TemplateParameter(
                    name="parameter",
                    type="string",
                    required=True,
                    description="Parameter name",
                )
            ],
            example_usage={"parameter": "ClientAliveInterval", "value": "300"},
        )

        assert schema.name == "sshd_lineinfile"
        assert len(schema.parameters) == 1
        assert schema.example_usage["parameter"] == "ClientAliveInterval"


class TestModelSerialization:
    """Test model JSON serialization."""

    def test_product_summary_roundtrip(self):
        """Test ProductSummary JSON roundtrip."""
        original = ProductSummary(
            product_id="rhel9",
            name="RHEL 9",
            product_type="rhel",
        )

        # Serialize
        json_data = original.model_dump()
        json_str = json.dumps(json_data)

        # Deserialize
        loaded_data = json.loads(json_str)
        loaded = ProductSummary(**loaded_data)

        assert loaded.product_id == original.product_id
        assert loaded.name == original.name

    def test_rule_details_roundtrip(self):
        """Test RuleDetails JSON roundtrip."""
        original = RuleDetails(
            rule_id="test_rule",
            title="Test Rule",
            description="Test description",
            severity="high",
            products=["rhel9"],
            platforms=["machine"],
            file_path="test/rule.yml",
            rule_dir="test/",
        )

        # Serialize
        json_data = original.model_dump()
        json_str = json.dumps(json_data, default=str)  # Handle datetime

        # Deserialize
        loaded_data = json.loads(json_str)
        loaded = RuleDetails(**loaded_data)

        assert loaded.rule_id == original.rule_id
        assert loaded.severity == original.severity
