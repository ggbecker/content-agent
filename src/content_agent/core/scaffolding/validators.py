"""Rule validation implementation."""

import logging
import re
from typing import List

import yaml

from content_agent.models import ValidationError, ValidationResult

logger = logging.getLogger(__name__)


class RuleValidator:
    """Validator for rule.yml files."""

    # Valid severity values
    VALID_SEVERITIES = {"low", "medium", "high", "unknown"}

    # Required top-level fields
    REQUIRED_FIELDS = {"documentation_complete", "title", "description"}

    # Optional but recommended fields
    RECOMMENDED_FIELDS = {"rationale", "severity", "references"}

    def __init__(self) -> None:
        """Initialize rule validator."""
        pass

    def validate_yaml(
        self,
        yaml_content: str,
        check_references: bool = True,
        auto_fix: bool = False,
    ) -> ValidationResult:
        """Validate rule YAML content.

        Note: This validator is designed for NEW rules being created during scaffolding.
        It uses yaml.safe_load() which does not expand Jinja2 templates. If you need to
        validate existing rules from ComplianceAsCode/content that contain Jinja2 macros
        ({{{ }}}), the templates will be treated as literal strings in the validation.

        Args:
            yaml_content: YAML content to validate
            check_references: Whether to check reference format
            auto_fix: Whether to attempt auto-fixing issues

        Returns:
            ValidationResult
        """
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        fixes_applied: List[str] = []

        try:
            # Parse YAML
            data = yaml.safe_load(yaml_content)

            if not isinstance(data, dict):
                errors.append(
                    ValidationError(
                        field="root",
                        error="Rule YAML must be a dictionary/object",
                        suggestion="Ensure the file contains valid YAML with key-value pairs",
                    )
                )
                return ValidationResult(
                    valid=False, errors=errors, warnings=warnings, fixes_applied=fixes_applied
                )

            # Check required fields
            errors.extend(self._check_required_fields(data))

            # Check recommended fields
            warnings.extend(self._check_recommended_fields(data))

            # Validate severity
            if "severity" in data:
                severity_errors = self._validate_severity(data["severity"])
                errors.extend(severity_errors)

            # Validate references
            if check_references and "references" in data:
                ref_warnings = self._validate_references(data["references"])
                warnings.extend(ref_warnings)

            # Validate identifiers
            if "identifiers" in data:
                id_warnings = self._validate_identifiers(data["identifiers"])
                warnings.extend(id_warnings)

            # Check for common mistakes
            warnings.extend(self._check_common_mistakes(data))

        except yaml.YAMLError as e:
            errors.append(
                ValidationError(
                    field="yaml",
                    error=f"YAML parsing error: {e}",
                    suggestion="Fix YAML syntax errors",
                )
            )
        except Exception as e:
            errors.append(
                ValidationError(
                    field="validation",
                    error=f"Validation error: {e}",
                )
            )

        valid = len(errors) == 0
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            fixes_applied=fixes_applied,
        )

    def _check_required_fields(self, data: dict) -> List[ValidationError]:
        """Check for required fields.

        Args:
            data: Parsed YAML data

        Returns:
            List of validation errors
        """
        errors = []

        for field in self.REQUIRED_FIELDS:
            if field not in data:
                errors.append(
                    ValidationError(
                        field=field,
                        error=f"Required field '{field}' is missing",
                        suggestion=f"Add '{field}' field to the rule",
                    )
                )
            elif not data[field]:
                errors.append(
                    ValidationError(
                        field=field,
                        error=f"Required field '{field}' is empty",
                        suggestion=f"Provide a value for '{field}'",
                    )
                )

        return errors

    def _check_recommended_fields(self, data: dict) -> List[ValidationError]:
        """Check for recommended fields.

        Args:
            data: Parsed YAML data

        Returns:
            List of validation warnings
        """
        warnings = []

        for field in self.RECOMMENDED_FIELDS:
            if field not in data:
                warnings.append(
                    ValidationError(
                        field=field,
                        error=f"Recommended field '{field}' is missing",
                        suggestion=f"Consider adding '{field}' field",
                    )
                )

        return warnings

    def _validate_severity(self, severity: str) -> List[ValidationError]:
        """Validate severity value.

        Args:
            severity: Severity value

        Returns:
            List of validation errors
        """
        errors = []

        if severity not in self.VALID_SEVERITIES:
            errors.append(
                ValidationError(
                    field="severity",
                    error=f"Invalid severity value '{severity}'",
                    suggestion=f"Use one of: {', '.join(sorted(self.VALID_SEVERITIES))}",
                )
            )

        return errors

    def _validate_references(self, references: dict) -> List[ValidationError]:
        """Validate reference format.

        Args:
            references: References dict

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check NIST format
        if "nist" in references:
            nist_refs = references["nist"]
            if isinstance(nist_refs, list):
                for ref in nist_refs:
                    if not self._is_valid_nist_reference(ref):
                        warnings.append(
                            ValidationError(
                                field="references.nist",
                                error=f"NIST reference '{ref}' may have incorrect format",
                                suggestion="Use format like 'AC-2(5)' or 'SC-10'",
                            )
                        )

        return warnings

    def _is_valid_nist_reference(self, ref: str) -> bool:
        """Check if NIST reference is valid format.

        Args:
            ref: Reference string

        Returns:
            True if valid format
        """
        # NIST format: XX-## or XX-##(##)
        pattern = r"^[A-Z]{2}-\d+(\(\d+\))?$"
        return bool(re.match(pattern, ref))

    def _validate_identifiers(self, identifiers: dict) -> List[ValidationError]:
        """Validate identifier format.

        Args:
            identifiers: Identifiers dict

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check CCE format
        if "cce" in identifiers:
            cce = identifiers["cce"]
            if isinstance(cce, list) and cce:
                cce = cce[0]
            if isinstance(cce, str) and not self._is_valid_cce(cce):
                warnings.append(
                    ValidationError(
                        field="identifiers.cce",
                        error=f"CCE identifier '{cce}' may have incorrect format",
                        suggestion="Use format like 'CCE-12345-6'",
                    )
                )

        return warnings

    def _is_valid_cce(self, cce: str) -> bool:
        """Check if CCE is valid format.

        Args:
            cce: CCE string

        Returns:
            True if valid format
        """
        # CCE format: CCE-#####-#
        pattern = r"^CCE-\d{5}-\d$"
        return bool(re.match(pattern, cce))

    def _check_common_mistakes(self, data: dict) -> List[ValidationError]:
        """Check for common mistakes.

        Args:
            data: Parsed YAML data

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check for platform vs platforms
        if "platform" in data and "platforms" in data:
            warnings.append(
                ValidationError(
                    field="platform/platforms",
                    error="Both 'platform' and 'platforms' are defined",
                    suggestion="Use only 'platform' field",
                )
            )

        # Check for empty lists
        for field in ["products", "platforms"]:
            if field in data and isinstance(data[field], list) and not data[field]:
                warnings.append(
                    ValidationError(
                        field=field,
                        error=f"Field '{field}' is an empty list",
                        suggestion=f"Either remove '{field}' or add values",
                    )
                )

        return warnings


def validate_rule_yaml(
    yaml_content: str,
    check_references: bool = True,
    auto_fix: bool = False,
) -> ValidationResult:
    """Validate rule YAML content.

    Args:
        yaml_content: YAML content to validate
        check_references: Whether to check reference format
        auto_fix: Whether to attempt auto-fixing issues

    Returns:
        ValidationResult
    """
    validator = RuleValidator()
    return validator.validate_yaml(yaml_content, check_references, auto_fix)
