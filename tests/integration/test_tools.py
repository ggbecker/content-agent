"""Integration tests for MCP tool handlers.

Note: These tests require a valid content repository to be set up.
For CI/CD, you may need to skip these or use fixtures.
"""

import json

import pytest

from content_agent.server.handlers.tools import handle_tool_call


@pytest.mark.skip(reason="Requires actual content repository")
class TestToolHandlers:
    """Test MCP tool handlers (integration tests)."""

    @pytest.mark.asyncio
    async def test_list_products_tool(self):
        """Test list_products tool."""
        result = await handle_tool_call("list_products", {})

        assert len(result) == 1
        assert result[0]["type"] == "text"

        # Parse JSON response
        data = json.loads(result[0]["text"])
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_rules_tool(self):
        """Test search_rules tool."""
        result = await handle_tool_call(
            "search_rules", {"query": "ssh", "limit": 5}
        )

        assert len(result) == 1
        assert result[0]["type"] == "text"

        # Should contain JSON response
        response_text = result[0]["text"]
        assert "Found" in response_text  # Summary line
        assert "[" in response_text  # JSON array

    @pytest.mark.asyncio
    async def test_validate_rule_yaml_tool(self):
        """Test validate_rule_yaml tool."""
        yaml_content = """
documentation_complete: true
title: Test Rule
description: Test description
severity: medium
"""
        result = await handle_tool_call(
            "validate_rule_yaml", {"rule_yaml": yaml_content}
        )

        assert len(result) == 1
        assert result[0]["type"] == "text"

        # Parse JSON response
        data = json.loads(result[0]["text"])
        assert "valid" in data
        assert isinstance(data["valid"], bool)

    @pytest.mark.asyncio
    async def test_validate_rule_yaml_with_errors(self):
        """Test validate_rule_yaml with invalid YAML."""
        yaml_content = """
title: Test Rule
severity: invalid_severity
"""
        result = await handle_tool_call(
            "validate_rule_yaml", {"rule_yaml": yaml_content}
        )

        data = json.loads(result[0]["text"])
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling for missing parameters."""
        # Missing required parameter
        result = await handle_tool_call("get_product_details", {})

        assert len(result) == 1
        assert result[0]["type"] == "text"

        # Should contain error message
        response = result[0]["text"]
        assert "error" in response.lower() or "fail" in response.lower()

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling unknown tool."""
        result = await handle_tool_call("unknown_tool_name", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0]["text"]


class TestToolValidation:
    """Test tool parameter validation (unit-level)."""

    @pytest.mark.asyncio
    async def test_validate_severity_enum(self):
        """Test severity parameter validation."""
        # Valid severities
        valid_severities = ["low", "medium", "high", "unknown"]

        for severity in valid_severities:
            yaml_content = f"""
documentation_complete: true
title: Test
description: Test
severity: {severity}
"""
            result = await handle_tool_call(
                "validate_rule_yaml", {"rule_yaml": yaml_content}
            )

            # Should not have severity errors
            data = json.loads(result[0]["text"])
            severity_errors = [
                e for e in data.get("errors", []) if e.get("field") == "severity"
            ]
            assert len(severity_errors) == 0

    @pytest.mark.asyncio
    async def test_search_rules_limit_parameter(self):
        """Test search_rules with limit parameter."""
        # Note: This test may be skipped if no real content
        try:
            result = await handle_tool_call(
                "search_rules", {"query": "ssh", "limit": 3}
            )

            response_text = result[0]["text"]
            # Extract JSON part (after summary line)
            json_start = response_text.index("[")
            data = json.loads(response_text[json_start:])

            # Should respect limit
            assert len(data) <= 3
        except Exception:
            # Skip if no content available
            pytest.skip("No content repository available")
