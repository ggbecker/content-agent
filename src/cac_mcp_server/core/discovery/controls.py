"""Control framework discovery implementation."""

import logging
from pathlib import Path
from typing import List

from cac_mcp_server.core.integration import get_content_repository

logger = logging.getLogger(__name__)


class ControlDiscovery:
    """Control framework discovery."""

    def __init__(self) -> None:
        """Initialize control discovery."""
        self.content_repo = get_content_repository()

    def list_controls(self) -> List[str]:
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


def list_controls() -> List[str]:
    """List available control frameworks.

    Returns:
        List of control framework names
    """
    discovery = ControlDiscovery()
    return discovery.list_controls()
