"""Rule scaffolding generation implementation."""

import logging
from pathlib import Path
from typing import List, Optional

import yaml

from content_agent.core.integration import get_content_repository
from content_agent.models import ScaffoldingResult, ValidationResult

logger = logging.getLogger(__name__)


class RuleGenerator:
    """Generator for rule boilerplate."""

    def __init__(self) -> None:
        """Initialize rule generator."""
        self.content_repo = get_content_repository()

    def generate_rule_boilerplate(
        self,
        rule_id: str,
        title: str,
        description: str,
        severity: str,
        product: str,
        location: Optional[str] = None,
        rationale: Optional[str] = None,
    ) -> ScaffoldingResult:
        """Generate basic rule structure.

        Args:
            rule_id: Rule identifier (directory name)
            title: Rule title
            description: Rule description
            severity: Rule severity (low, medium, high)
            product: Product identifier
            location: Optional custom location path (e.g., linux_os/guide/services/ssh)
            rationale: Optional rationale

        Returns:
            ScaffoldingResult
        """
        logger.info(f"Generating rule boilerplate for {rule_id}")

        try:
            # Determine rule location
            if location:
                rule_dir = self.content_repo.path / location / rule_id
            else:
                # Default location based on product
                rule_dir = self._determine_default_location(product, rule_id)

            # Check if rule already exists
            if rule_dir.exists():
                return ScaffoldingResult(
                    success=False,
                    rule_id=rule_id,
                    rule_dir=str(rule_dir.relative_to(self.content_repo.path)),
                    message=f"Rule directory already exists: {rule_dir}",
                    files_created=[],
                )

            # Create directory structure
            files_created = self._create_directory_structure(rule_dir)

            # Generate rule.yml
            rule_yml_content = self._generate_rule_yml(
                rule_id=rule_id,
                title=title,
                description=description,
                severity=severity,
                product=product,
                rationale=rationale,
            )

            rule_yml_path = rule_dir / "rule.yml"
            rule_yml_path.write_text(rule_yml_content)
            files_created.append(str(rule_yml_path.relative_to(self.content_repo.path)))

            logger.info(f"Created rule boilerplate at {rule_dir}")

            return ScaffoldingResult(
                success=True,
                rule_id=rule_id,
                rule_dir=str(rule_dir.relative_to(self.content_repo.path)),
                message=f"Rule boilerplate created successfully at {rule_dir}",
                files_created=files_created,
            )

        except Exception as e:
            logger.error(f"Failed to generate rule boilerplate: {e}")
            return ScaffoldingResult(
                success=False,
                rule_id=rule_id,
                rule_dir="",
                message=f"Failed to generate rule: {e}",
                files_created=[],
            )

    def _determine_default_location(self, product: str, rule_id: str) -> Path:
        """Determine default location for rule based on product.

        Args:
            product: Product identifier
            rule_id: Rule identifier

        Returns:
            Path to rule directory
        """
        # Most products use linux_os/guide structure
        # Determine category from rule_id naming pattern
        if "sshd_" in rule_id or rule_id.startswith("ssh_"):
            base_path = "linux_os/guide/services/ssh/ssh_server"
        elif "audit_" in rule_id or "auditd_" in rule_id:
            base_path = "linux_os/guide/system/auditing"
        elif "package_" in rule_id:
            base_path = "linux_os/guide/system/software/integrity"
        elif "kernel_" in rule_id:
            base_path = "linux_os/guide/system/bootloader-grub2"
        elif "account_" in rule_id or "accounts_" in rule_id:
            base_path = "linux_os/guide/system/accounts"
        elif "service_" in rule_id:
            base_path = "linux_os/guide/services"
        elif "file_" in rule_id or "permissions_" in rule_id:
            base_path = "linux_os/guide/system/permissions"
        else:
            # Default to a generic location
            base_path = "linux_os/guide/system/misc"

        return self.content_repo.path / base_path / rule_id

    def _create_directory_structure(self, rule_dir: Path) -> List[str]:
        """Create rule directory structure.

        Args:
            rule_dir: Rule directory path

        Returns:
            List of created directory paths
        """
        created = []

        # Create main rule directory
        rule_dir.mkdir(parents=True, exist_ok=True)
        created.append(str(rule_dir.relative_to(self.content_repo.path)))

        # Create subdirectories for remediations and checks
        subdirs = ["bash", "ansible", "oval", "tests"]

        for subdir in subdirs:
            subdir_path = rule_dir / subdir
            subdir_path.mkdir(exist_ok=True)
            created.append(str(subdir_path.relative_to(self.content_repo.path)))

            # Create .gitkeep to preserve empty directories
            gitkeep = subdir_path / ".gitkeep"
            gitkeep.touch()

        return created

    def _generate_rule_yml(
        self,
        rule_id: str,
        title: str,
        description: str,
        severity: str,
        product: str,
        rationale: Optional[str] = None,
    ) -> str:
        """Generate rule.yml content.

        Args:
            rule_id: Rule identifier
            title: Rule title
            description: Rule description
            severity: Rule severity
            product: Product identifier
            rationale: Optional rationale

        Returns:
            YAML content as string
        """
        rule_data = {
            "documentation_complete": True,
            "title": title,
            "description": description,
            "rationale": rationale or "TODO: Provide rationale for this rule",
            "severity": severity,
            "identifiers": {
                "cce": "TODO: Obtain CCE identifier",
            },
            "references": {
                "nist": ["TODO: Add NIST references"],
            },
            "platform": "machine",
            "products": [product],
        }

        # Convert to YAML with nice formatting
        yaml_str = yaml.dump(
            rule_data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

        # Add header comment
        header = f"""# Rule: {rule_id}
# Generated by content-agent
#
# This is a basic rule template. You should:
# 1. Complete the TODO items
# 2. Add appropriate remediations in bash/ and ansible/ directories
# 3. Add OVAL checks in oval/ directory
# 4. Add test scenarios in tests/ directory
#
---
"""

        return header + yaml_str


def generate_rule_boilerplate(
    rule_id: str,
    title: str,
    description: str,
    severity: str,
    product: str,
    location: Optional[str] = None,
    rationale: Optional[str] = None,
) -> ScaffoldingResult:
    """Generate basic rule structure.

    Args:
        rule_id: Rule identifier
        title: Rule title
        description: Rule description
        severity: Rule severity
        product: Product identifier
        location: Optional custom location
        rationale: Optional rationale

    Returns:
        ScaffoldingResult
    """
    generator = RuleGenerator()
    return generator.generate_rule_boilerplate(
        rule_id=rule_id,
        title=title,
        description=description,
        severity=severity,
        product=product,
        location=location,
        rationale=rationale,
    )
