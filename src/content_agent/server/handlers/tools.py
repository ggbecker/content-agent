"""MCP tool handlers."""

import json
import logging
from typing import Any, Dict, List, Optional

from content_agent.core import discovery, scaffolding

logger = logging.getLogger(__name__)


# Tool definitions
TOOLS = [
    # Discovery tools
    {
        "name": "list_products",
        "description": "List all available products in the ComplianceAsCode/content repository",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_product_details",
        "description": "Get detailed information about a specific product",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Product identifier (e.g., rhel9, fedora, ocp4)",
                }
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "search_rules",
        "description": "Search for rules by keyword, product, or severity",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (matches rule ID, title, description)",
                },
                "product": {
                    "type": "string",
                    "description": "Filter by product ID",
                },
                "severity": {
                    "type": "string",
                    "description": "Filter by severity (low, medium, high, unknown)",
                    "enum": ["low", "medium", "high", "unknown"],
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 50)",
                    "default": 50,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_rule_details",
        "description": "Get complete information about a specific rule. Automatically includes rendered content metadata from build artifacts if available (low token usage by default).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule_id": {
                    "type": "string",
                    "description": "Rule identifier",
                },
                "include_rendered": {
                    "type": "boolean",
                    "description": "Include rendered content from builds (default: true). Automatically detects and includes info about rendered YAML, OVAL, and remediations.",
                    "default": True,
                },
                "product": {
                    "type": "string",
                    "description": "Optional product filter for rendered content. If specified, only includes rendered content for this product.",
                },
                "rendered_detail": {
                    "type": "string",
                    "description": "Detail level for rendered content: 'metadata' (default, ~2k tokens - sizes and availability only) or 'full' (~18k tokens - includes complete rendered text). Use 'full' only when you need to see actual rendered content.",
                    "enum": ["metadata", "full"],
                    "default": "metadata",
                },
            },
            "required": ["rule_id"],
        },
    },
    {
        "name": "list_templates",
        "description": "List all available rule templates",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_template_schema",
        "description": "Get parameter schema for a template",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "description": "Template name",
                }
            },
            "required": ["template_name"],
        },
    },
    {
        "name": "list_profiles",
        "description": "List profiles for a product or all products",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "Optional product filter",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_profile_details",
        "description": "Get detailed information about a profile",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_id": {
                    "type": "string",
                    "description": "Profile identifier",
                },
                "product": {
                    "type": "string",
                    "description": "Product identifier",
                },
            },
            "required": ["profile_id", "product"],
        },
    },
    # Scaffolding tools
    {
        "name": "generate_rule_boilerplate",
        "description": "Generate basic rule structure with boilerplate files",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule_id": {
                    "type": "string",
                    "description": "Rule identifier (will be used as directory name)",
                },
                "title": {
                    "type": "string",
                    "description": "Rule title",
                },
                "description": {
                    "type": "string",
                    "description": "Rule description",
                },
                "severity": {
                    "type": "string",
                    "description": "Rule severity",
                    "enum": ["low", "medium", "high", "unknown"],
                },
                "product": {
                    "type": "string",
                    "description": "Primary product for this rule",
                },
                "location": {
                    "type": "string",
                    "description": "Optional custom location path (e.g., linux_os/guide/services/ssh)",
                },
                "rationale": {
                    "type": "string",
                    "description": "Optional rationale for the rule",
                },
            },
            "required": ["rule_id", "title", "description", "severity", "product"],
        },
    },
    {
        "name": "validate_rule_yaml",
        "description": "Validate rule.yml YAML content",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rule_yaml": {
                    "type": "string",
                    "description": "YAML content to validate",
                },
                "check_references": {
                    "type": "boolean",
                    "description": "Whether to check reference format (default: true)",
                    "default": True,
                },
                "auto_fix": {
                    "type": "boolean",
                    "description": "Whether to attempt auto-fixing issues (default: false)",
                    "default": False,
                },
            },
            "required": ["rule_yaml"],
        },
    },
    {
        "name": "generate_rule_from_template",
        "description": "Generate rule using a template (Phase 3 feature)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "description": "Template name",
                },
                "parameters": {
                    "type": "object",
                    "description": "Template parameters",
                },
                "rule_id": {
                    "type": "string",
                    "description": "Rule identifier",
                },
                "product": {
                    "type": "string",
                    "description": "Product identifier",
                },
            },
            "required": ["template_name", "parameters", "rule_id", "product"],
        },
    },
    # Build artifacts tools
    {
        "name": "list_built_products",
        "description": "List products that have been built and have artifacts available in build/ directory",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_rendered_rule",
        "description": "Get fully rendered rule content from build directory (after Jinja template processing and variable expansion). Shows the actual content that goes into the datastream.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "Product identifier (e.g., rhel9, fedora)",
                },
                "rule_id": {
                    "type": "string",
                    "description": "Rule identifier",
                },
            },
            "required": ["product", "rule_id"],
        },
    },
    {
        "name": "get_datastream_info",
        "description": "Get information about a built datastream for a product",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "description": "Product identifier",
                },
            },
            "required": ["product"],
        },
    },
    {
        "name": "search_rendered_content",
        "description": "Search in rendered build artifacts (useful for finding actual values after template expansion, searching in final content)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "product": {
                    "type": "string",
                    "description": "Optional product filter",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 50)",
                    "default": 50,
                },
            },
            "required": ["query"],
        },
    },
]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle tool call.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        List of content items (text or image)

    Raises:
        ValueError: If tool not found or execution fails
    """
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    try:
        # Discovery tools
        if name == "list_products":
            products = discovery.list_products()
            result = [p.model_dump(mode='json') for p in products]
            return [{"type": "text", "text": json.dumps(result, indent=2)}]

        elif name == "get_product_details":
            product_id = arguments["product_id"]
            product = discovery.get_product_details(product_id)
            if not product:
                return [{"type": "text", "text": f"Product not found: {product_id}"}]
            return [{"type": "text", "text": json.dumps(product.model_dump(mode='json'), indent=2)}]

        elif name == "search_rules":
            query = arguments.get("query")
            product = arguments.get("product")
            severity = arguments.get("severity")
            limit = arguments.get("limit", 50)

            rules = discovery.search_rules(
                query=query, product=product, severity=severity, limit=limit
            )
            result = [r.model_dump(mode='json') for r in rules]
            summary = f"Found {len(rules)} rules matching search criteria.\n\n"
            return [{"type": "text", "text": summary + json.dumps(result, indent=2)}]

        elif name == "get_rule_details":
            rule_id = arguments["rule_id"]
            include_rendered = arguments.get("include_rendered", True)
            product = arguments.get("product")
            rendered_detail = arguments.get("rendered_detail", "metadata")

            rule = discovery.get_rule_details(
                rule_id, include_rendered, product, rendered_detail
            )
            if not rule:
                return [{"type": "text", "text": f"Rule not found: {rule_id}"}]

            # Add informative message about rendered content
            result_json = json.dumps(rule.model_dump(mode='json'), indent=2)
            if include_rendered and rule.rendered:
                products_with_rendered = list(rule.rendered.keys())
                detail_msg = (
                    "metadata only (use rendered_detail='full' to see actual content)"
                    if rendered_detail == "metadata"
                    else "full content"
                )
                summary = (
                    f"Rule details for '{rule_id}' with rendered {detail_msg} "
                    f"from {len(products_with_rendered)} product(s): {', '.join(products_with_rendered)}\n\n"
                )
                return [{"type": "text", "text": summary + result_json}]
            elif include_rendered:
                summary = f"Rule details for '{rule_id}' (no build artifacts found)\n\n"
                return [{"type": "text", "text": summary + result_json}]
            else:
                return [{"type": "text", "text": result_json}]

        elif name == "list_templates":
            templates = discovery.list_templates()
            result = [t.model_dump(mode='json') for t in templates]
            return [{"type": "text", "text": json.dumps(result, indent=2)}]

        elif name == "get_template_schema":
            template_name = arguments["template_name"]
            schema = discovery.get_template_schema(template_name)
            if not schema:
                return [{"type": "text", "text": f"Template not found: {template_name}"}]
            return [{"type": "text", "text": json.dumps(schema.model_dump(mode='json'), indent=2)}]

        elif name == "list_profiles":
            product = arguments.get("product")
            profiles = discovery.list_profiles(product=product)
            result = [p.model_dump(mode='json') for p in profiles]
            return [{"type": "text", "text": json.dumps(result, indent=2)}]

        elif name == "get_profile_details":
            profile_id = arguments["profile_id"]
            product = arguments["product"]
            profile = discovery.get_profile_details(profile_id, product)
            if not profile:
                return [
                    {
                        "type": "text",
                        "text": f"Profile not found: {profile_id} in {product}",
                    }
                ]
            return [{"type": "text", "text": json.dumps(profile.model_dump(mode='json'), indent=2)}]

        # Scaffolding tools
        elif name == "generate_rule_boilerplate":
            result = scaffolding.generate_rule_boilerplate(
                rule_id=arguments["rule_id"],
                title=arguments["title"],
                description=arguments["description"],
                severity=arguments["severity"],
                product=arguments["product"],
                location=arguments.get("location"),
                rationale=arguments.get("rationale"),
            )
            return [{"type": "text", "text": json.dumps(result.model_dump(mode='json'), indent=2)}]

        elif name == "validate_rule_yaml":
            result = scaffolding.validate_rule_yaml(
                yaml_content=arguments["rule_yaml"],
                check_references=arguments.get("check_references", True),
                auto_fix=arguments.get("auto_fix", False),
            )
            return [{"type": "text", "text": json.dumps(result.model_dump(mode='json'), indent=2)}]

        elif name == "generate_rule_from_template":
            result = scaffolding.generate_rule_from_template(
                template_name=arguments["template_name"],
                parameters=arguments["parameters"],
                rule_id=arguments["rule_id"],
                product=arguments["product"],
            )
            return [{"type": "text", "text": json.dumps(result.model_dump(mode='json'), indent=2)}]

        # Build artifacts tools
        elif name == "list_built_products":
            products = discovery.list_built_products()
            summary = f"Found {len(products)} products with build artifacts.\n\n"
            result = {"products": products, "count": len(products)}
            return [{"type": "text", "text": summary + json.dumps(result, indent=2)}]

        elif name == "get_rendered_rule":
            product = arguments["product"]
            rule_id = arguments["rule_id"]
            rendered = discovery.get_rendered_rule(product, rule_id)
            if not rendered:
                return [
                    {
                        "type": "text",
                        "text": f"Rendered rule not found: {rule_id} for product {product}.\n"
                        f"Make sure the product has been built (./build_product {product}).",
                    }
                ]
            return [{"type": "text", "text": json.dumps(rendered.model_dump(mode='json'), indent=2)}]

        elif name == "get_datastream_info":
            product = arguments["product"]
            info = discovery.get_datastream_info(product)
            if not info:
                return [
                    {
                        "type": "text",
                        "text": f"Datastream info not available for product: {product}",
                    }
                ]
            return [{"type": "text", "text": json.dumps(info.model_dump(mode='json'), indent=2)}]

        elif name == "search_rendered_content":
            query = arguments["query"]
            product = arguments.get("product")
            limit = arguments.get("limit", 50)

            results = discovery.search_rendered_content(query, product, limit)
            result = [r.model_dump(mode='json') for r in results]
            summary = f"Found {len(results)} matches in rendered build artifacts.\n\n"
            return [{"type": "text", "text": summary + json.dumps(result, indent=2)}]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        error_msg = f"Tool execution failed: {str(e)}"
        return [{"type": "text", "text": error_msg}]


def list_tools() -> List[Dict[str, Any]]:
    """List available tools.

    Returns:
        List of tool definitions
    """
    return TOOLS
