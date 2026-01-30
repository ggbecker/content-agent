"""Wrapper for SSG Python modules from ComplianceAsCode/content.

This module provides a safe interface to import and use SSG modules after
the content repository has been added to the Python path.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SSGModules:
    """Wrapper for accessing SSG Python modules."""

    def __init__(self) -> None:
        """Initialize SSG modules wrapper."""
        self._modules_loaded = False
        self._ssg = None
        self._build_yaml = None
        self._products = None
        self._rules = None
        self._templates = None
        self._profiles = None
        self._controls = None
        self._yaml = None
        self._constants = None

    def load_modules(self) -> None:
        """Load SSG Python modules.

        Raises:
            ImportError: If SSG modules cannot be imported
        """
        if self._modules_loaded:
            return

        try:
            logger.info("Loading SSG Python modules")

            # Core SSG modules
            import ssg
            import ssg.build_yaml
            import ssg.constants
            import ssg.controls
            import ssg.products
            import ssg.profiles
            import ssg.rules
            import ssg.templates
            import ssg.yaml

            self._ssg = ssg
            self._build_yaml = ssg.build_yaml
            self._constants = ssg.constants
            self._products = ssg.products
            self._rules = ssg.rules
            self._templates = ssg.templates
            self._profiles = ssg.profiles
            self._controls = ssg.controls
            self._yaml = ssg.yaml

            self._modules_loaded = True
            logger.info("SSG modules loaded successfully")

        except ImportError as e:
            logger.error(f"Failed to import SSG modules: {e}")
            raise ImportError(
                f"Failed to import SSG modules. Ensure content repository is initialized.\n"
                f"Error: {e}"
            ) from e

    @property
    def build_yaml(self) -> Any:
        """Get ssg.build_yaml module.

        Returns:
            ssg.build_yaml module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._build_yaml

    @property
    def products(self) -> Any:
        """Get ssg.products module.

        Returns:
            ssg.products module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._products

    @property
    def rules(self) -> Any:
        """Get ssg.rules module.

        Returns:
            ssg.rules module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._rules

    @property
    def templates(self) -> Any:
        """Get ssg.templates module.

        Returns:
            ssg.templates module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._templates

    @property
    def profiles(self) -> Any:
        """Get ssg.profiles module.

        Returns:
            ssg.profiles module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._profiles

    @property
    def controls(self) -> Any:
        """Get ssg.controls module.

        Returns:
            ssg.controls module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._controls

    @property
    def yaml(self) -> Any:
        """Get ssg.yaml module.

        Returns:
            ssg.yaml module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._yaml

    @property
    def constants(self) -> Any:
        """Get ssg.constants module.

        Returns:
            ssg.constants module

        Raises:
            ImportError: If modules not loaded
        """
        if not self._modules_loaded:
            raise ImportError("SSG modules not loaded. Call load_modules() first.")
        return self._constants


# Global SSG modules instance
_ssg_modules: Optional[SSGModules] = None


def get_ssg_modules() -> SSGModules:
    """Get the global SSG modules instance.

    Returns:
        SSGModules instance

    Raises:
        RuntimeError: If not initialized
    """
    if _ssg_modules is None:
        raise RuntimeError("SSG modules not initialized. Call initialize_ssg_modules() first.")
    return _ssg_modules


def initialize_ssg_modules() -> SSGModules:
    """Initialize the global SSG modules instance.

    Returns:
        SSGModules instance
    """
    global _ssg_modules
    _ssg_modules = SSGModules()
    _ssg_modules.load_modules()
    return _ssg_modules
