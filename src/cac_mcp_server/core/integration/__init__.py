"""Content repository integration."""

from cac_mcp_server.core.integration.content_manager import (
    ContentRepository,
    get_content_repository,
    initialize_content_repository,
)
from cac_mcp_server.core.integration.ssg_modules import (
    SSGModules,
    get_ssg_modules,
    initialize_ssg_modules,
)

__all__ = [
    "ContentRepository",
    "get_content_repository",
    "initialize_content_repository",
    "SSGModules",
    "get_ssg_modules",
    "initialize_ssg_modules",
]
