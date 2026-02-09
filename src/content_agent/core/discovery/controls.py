"""Control framework discovery implementation."""

import logging
from pathlib import Path

import yaml

from content_agent.core.integration import get_content_repository
from content_agent.models.control import ControlFile, ControlRequirement

logger = logging.getLogger(__name__)


class ControlDiscovery:
    """Control framework discovery."""

    def __init__(self) -> None:
        """Initialize control discovery."""
        self.content_repo = get_content_repository()

    def list_controls(self) -> list[str]:
        """List available control frameworks.

        Returns:
            List of control framework names
        """
        logger.debug("Listing control frameworks")
        controls = []

        controls_dir = self.content_repo.path / "controls"
        if not controls_dir.exists():
            return []

        for control_file in controls_dir.glob("*.yml"):
            controls.append(control_file.stem)

        controls.sort()
        logger.info(f"Found {len(controls)} control frameworks")
        return controls

    def get_control_details(self, control_id: str) -> ControlFile | None:
        """Parse and return complete control file details.

        Args:
            control_id: Control framework identifier

        Returns:
            ControlFile with parsed details, or None if not found
        """
        logger.debug(f"Getting details for control: {control_id}")

        controls_dir = self.content_repo.path / "controls"
        control_file = controls_dir / f"{control_id}.yml"

        if not control_file.exists():
            logger.warning(f"Control file not found: {control_file}")
            return None

        return self.parse_control_file(control_file)

    def parse_control_file(self, file_path: Path) -> ControlFile | None:
        """Parse control YAML into structured model.

        Args:
            file_path: Path to control file

        Returns:
            ControlFile object, or None if parsing fails
        """
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)

            # Parse included files if present
            if "includes" in data and data["includes"]:
                # Load included requirement files
                controls = []
                base_dir = file_path.parent / file_path.stem

                for include_path in data["includes"]:
                    full_path = base_dir / include_path
                    if full_path.exists():
                        req = self._parse_requirement_file(full_path)
                        if req:
                            controls.append(req)
                    else:
                        logger.warning(f"Included file not found: {full_path}")

                data["controls"] = controls

            # Parse control file
            return ControlFile(**data)

        except Exception as e:
            logger.error(f"Failed to parse control file {file_path}: {e}")
            return None

    def search_controls(
        self,
        query: str,
        control_id: str | None = None,
    ) -> list[ControlRequirement]:
        """Search within control files for requirements.

        Args:
            query: Search query (matches title, description)
            control_id: Optional control framework to search within

        Returns:
            List of matching control requirements
        """
        logger.debug(f"Searching controls: query='{query}', control_id={control_id}")

        results = []

        # Determine which controls to search
        if control_id:
            control = self.get_control_details(control_id)
            controls_to_search = [control] if control else []
        else:
            control_ids = self.list_controls()
            controls_to_search = [self.get_control_details(cid) for cid in control_ids]
            controls_to_search = [c for c in controls_to_search if c is not None]

        # Search through controls
        query_lower = query.lower()

        for control in controls_to_search:
            for req in control.controls:
                # Search in title and description
                if (
                    query_lower in req.title.lower()
                    or query_lower in req.description.lower()
                    or query_lower in req.id.lower()
                ):
                    results.append(req)

        logger.info(f"Found {len(results)} matching requirements")
        return results

    def _parse_requirement_file(self, file_path: Path) -> ControlRequirement | None:
        """Parse individual requirement file.

        Args:
            file_path: Path to requirement file

        Returns:
            ControlRequirement object, or None if parsing fails
        """
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)

            return ControlRequirement(**data)

        except Exception as e:
            logger.error(f"Failed to parse requirement file {file_path}: {e}")
            return None


def list_controls() -> list[str]:
    """List available control frameworks.

    Returns:
        List of control framework names
    """
    discovery = ControlDiscovery()
    return discovery.list_controls()


def get_control_details(control_id: str) -> ControlFile | None:
    """Get control framework details.

    Args:
        control_id: Control framework identifier

    Returns:
        ControlFile with details, or None if not found
    """
    discovery = ControlDiscovery()
    return discovery.get_control_details(control_id)


def search_controls(query: str, control_id: str | None = None) -> list[ControlRequirement]:
    """Search control requirements.

    Args:
        query: Search query
        control_id: Optional control framework to search within

    Returns:
        List of matching requirements
    """
    discovery = ControlDiscovery()
    return discovery.search_controls(query, control_id)
