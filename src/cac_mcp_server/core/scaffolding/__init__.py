"""Rule scaffolding module."""

from cac_mcp_server.core.scaffolding.rule_generator import generate_rule_boilerplate
from cac_mcp_server.core.scaffolding.template_generator import (
    generate_rule_from_template,
)
from cac_mcp_server.core.scaffolding.validators import validate_rule_yaml

__all__ = [
    "generate_rule_boilerplate",
    "generate_rule_from_template",
    "validate_rule_yaml",
]
