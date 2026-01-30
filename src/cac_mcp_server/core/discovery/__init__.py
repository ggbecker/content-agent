"""Content discovery module."""

from cac_mcp_server.core.discovery.build_artifacts import (
    get_datastream_info,
    get_rendered_rule,
    list_built_products,
    search_rendered_content,
)
from cac_mcp_server.core.discovery.controls import list_controls
from cac_mcp_server.core.discovery.products import get_product_details, list_products
from cac_mcp_server.core.discovery.profiles import get_profile_details, list_profiles
from cac_mcp_server.core.discovery.rules import get_rule_details, search_rules
from cac_mcp_server.core.discovery.templates import get_template_schema, list_templates

__all__ = [
    # Products
    "list_products",
    "get_product_details",
    # Rules
    "search_rules",
    "get_rule_details",
    # Profiles
    "list_profiles",
    "get_profile_details",
    # Templates
    "list_templates",
    "get_template_schema",
    # Controls
    "list_controls",
    # Build artifacts
    "list_built_products",
    "get_rendered_rule",
    "get_datastream_info",
    "search_rendered_content",
]
