"""Control file generation implementation."""

import logging
from pathlib import Path

import yaml

from content_agent.core.integration import get_content_repository
from content_agent.models.control import (
    ControlFile,
    ControlGenerationResult,
    ControlRequirement,
    ExtractedRequirement,
)

logger = logging.getLogger(__name__)


class ControlGenerator:
    """Generator for control file structures."""

    def __init__(self) -> None:
        """Initialize control generator."""
        self.content_repo = get_content_repository()

    def generate_control_structure(
        self,
        policy_id: str,
        policy_title: str,
        requirements: list[ExtractedRequirement],
        output_dir: Path | None = None,
        nested_by_section: bool = True,
        source_document: str | None = None,
        description: str | None = None,
    ) -> ControlGenerationResult:
        """Generate control file structure with individual requirement files.

        Creates:
        - controls/<policy_id>/section1/req1.yml
        - controls/<policy_id>/section1/req2.yml
        - controls/<policy_id>.yml (parent with includes)

        Args:
            policy_id: Policy identifier
            policy_title: Policy title
            requirements: List of extracted requirements
            output_dir: Optional output directory (defaults to controls/)
            nested_by_section: Whether to nest files by section

        Returns:
            ControlGenerationResult with file paths and status
        """
        logger.info(f"Generating control structure for {policy_id}")

        try:
            # Determine output directory
            if output_dir is None:
                output_dir = self.content_repo.path / "controls"
            else:
                output_dir = Path(output_dir)

            policy_dir = output_dir / policy_id
            parent_file_path = output_dir / f"{policy_id}.yml"

            # Check if already exists
            if policy_dir.exists() or parent_file_path.exists():
                return ControlGenerationResult(
                    policy_id=policy_id,
                    parent_file_path=parent_file_path,
                    requirement_files=[],
                    total_requirements=0,
                    sections=[],
                    success=False,
                    errors=[
                        f"Control structure already exists: {policy_dir} or {parent_file_path}"
                    ],
                    warnings=[],
                )

            # Create directory structure
            policy_dir.mkdir(parents=True, exist_ok=True)

            # Convert ExtractedRequirement to ControlRequirement
            control_requirements = self._convert_to_control_requirements(requirements)

            # Group by section if nested
            if nested_by_section:
                sections = self._group_by_section(control_requirements)
            else:
                sections = {"default": control_requirements}

            # Generate individual requirement files
            requirement_files = []
            created_sections = []

            for section_id, section_reqs in sections.items():
                if nested_by_section and section_id != "default":
                    section_dir = policy_dir / section_id
                    section_dir.mkdir(parents=True, exist_ok=True)
                    created_sections.append(section_id)
                else:
                    section_dir = policy_dir

                for idx, req in enumerate(section_reqs, 1):
                    # Generate filename from requirement ID or index
                    filename = self._generate_filename(req, idx)
                    file_path = section_dir / filename

                    # Generate requirement file
                    success = self.generate_requirement_file(req, file_path)
                    if success:
                        # Store relative path from policy_dir
                        if nested_by_section and section_id != "default":
                            rel_path = f"{section_id}/{filename}"
                        else:
                            rel_path = filename
                        requirement_files.append(rel_path)

            # Generate parent control file
            parent_success = self.generate_parent_control_file(
                policy_id=policy_id,
                policy_title=policy_title,
                requirement_files=requirement_files,
                output_path=parent_file_path,
                source_document=source_document or "Unknown",
                description=description,
            )

            if not parent_success:
                return ControlGenerationResult(
                    policy_id=policy_id,
                    parent_file_path=parent_file_path,
                    requirement_files=[policy_dir / f for f in requirement_files],
                    total_requirements=len(control_requirements),
                    sections=created_sections,
                    success=False,
                    errors=["Failed to generate parent control file"],
                    warnings=[],
                )

            logger.info(
                f"Created control structure with {len(requirement_files)} requirements"
            )

            return ControlGenerationResult(
                policy_id=policy_id,
                parent_file_path=parent_file_path,
                requirement_files=[policy_dir / f for f in requirement_files],
                total_requirements=len(control_requirements),
                sections=created_sections,
                success=True,
                errors=[],
                warnings=[],
            )

        except Exception as e:
            logger.error(f"Failed to generate control structure: {e}")
            return ControlGenerationResult(
                policy_id=policy_id,
                parent_file_path=Path(),
                requirement_files=[],
                total_requirements=0,
                sections=[],
                success=False,
                errors=[str(e)],
                warnings=[],
            )

    def generate_requirement_file(
        self, requirement: ControlRequirement, file_path: Path
    ) -> bool:
        """Generate individual requirement control file.

        Args:
            requirement: Control requirement
            file_path: Path to write file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create YAML content
            content = {
                "id": requirement.id,
                "title": requirement.title,
                "description": requirement.description,
                "status": requirement.status,
            }

            # Add optional fields if present
            if requirement.rules:
                content["rules"] = requirement.rules

            if requirement.related_rules:
                content["related_rules"] = requirement.related_rules

            if requirement.references:
                content["references"] = requirement.references

            if requirement.notes:
                content["notes"] = requirement.notes

            # Write YAML file
            with open(file_path, "w") as f:
                yaml.dump(
                    content,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

            logger.debug(f"Created requirement file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create requirement file {file_path}: {e}")
            return False

    def generate_parent_control_file(
        self,
        policy_id: str,
        policy_title: str,
        requirement_files: list[str],
        output_path: Path,
        description: str | None = None,
        source_document: str | None = None,
    ) -> bool:
        """Generate parent control file with includes.

        Args:
            policy_id: Policy identifier
            policy_title: Policy title
            requirement_files: List of relative paths to requirement files
            output_path: Path to write parent file
            description: Optional policy description
            source_document: Optional source document path/URL

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent control file content
            content = {
                "id": policy_id,
                "title": policy_title,
                "description": description or f"Control framework for {policy_title}",
            }

            if source_document:
                content["source_document"] = source_document

            # Add includes
            content["includes"] = requirement_files

            # Write YAML file
            with open(output_path, "w") as f:
                yaml.dump(
                    content,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

            logger.info(f"Created parent control file: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create parent control file {output_path}: {e}")
            return False

    def _convert_to_control_requirements(
        self, extracted: list[ExtractedRequirement]
    ) -> list[ControlRequirement]:
        """Convert ExtractedRequirement to ControlRequirement.

        Args:
            extracted: List of extracted requirements

        Returns:
            List of control requirements
        """
        requirements = []

        for idx, req in enumerate(extracted, 1):
            # Generate ID if not present
            req_id = req.potential_id or f"REQ-{idx:03d}"

            # Extract title from first line or use ID
            title_parts = req.text.split("\n", 1)
            title = title_parts[0][:100] if title_parts else req_id

            control_req = ControlRequirement(
                id=req_id,
                title=title,
                description=req.text,
                section=req.section_id,
            )

            requirements.append(control_req)

        return requirements

    def _group_by_section(
        self, requirements: list[ControlRequirement]
    ) -> dict[str, list[ControlRequirement]]:
        """Group requirements by section.

        Args:
            requirements: List of requirements

        Returns:
            Dictionary mapping section ID to requirements
        """
        sections: dict[str, list[ControlRequirement]] = {}

        for req in requirements:
            section_id = req.section or "default"
            # Clean section ID for filesystem
            section_id = self._clean_section_id(section_id)

            if section_id not in sections:
                sections[section_id] = []
            sections[section_id].append(req)

        return sections

    def _clean_section_id(self, section_id: str) -> str:
        """Clean section ID for use as directory name.

        Args:
            section_id: Section identifier

        Returns:
            Cleaned section ID
        """
        # Replace special characters with underscores
        clean = "".join(c if c.isalnum() or c in "-_" else "_" for c in section_id)
        # Remove consecutive underscores
        clean = "_".join(filter(None, clean.split("_")))
        # Limit length
        return clean[:50].lower()

    def _generate_filename(self, requirement: ControlRequirement, index: int) -> str:
        """Generate filename for requirement.

        Args:
            requirement: Control requirement
            index: Index in section

        Returns:
            Filename (e.g., "req_001.yml" or "ac_2_5.yml")
        """
        # Try to use requirement ID
        if requirement.id and requirement.id != f"REQ-{index:03d}":
            # Clean ID for filename
            clean_id = "".join(
                c if c.isalnum() or c in "-_" else "_" for c in requirement.id.lower()
            )
            clean_id = "_".join(filter(None, clean_id.split("_")))
            return f"{clean_id}.yml"

        # Fall back to index-based name
        return f"req_{index:03d}.yml"
