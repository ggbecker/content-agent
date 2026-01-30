#!/usr/bin/env python3
"""Example usage of build artifacts feature.

This script demonstrates how to use the build artifacts discovery functionality
to access rendered content from build directories.
"""

import sys
from pathlib import Path

# Add src to path (adjust if needed)
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def example_build_artifacts():
    """Example usage of build artifacts feature."""
    from cac_mcp_server.core.integration import (
        initialize_content_repository,
    )
    from cac_mcp_server.core import discovery

    # Initialize content repository
    # Use environment variable or provide path
    import os
    content_path = os.environ.get("CAC_MCP_CONTENT__REPOSITORY", "/path/to/content")
    content_repo = initialize_content_repository(Path(content_path))

    print("Build Artifacts Feature Examples")
    print("=" * 70)

    # Example 1: List built products
    print("\nExample 1: List Built Products")
    print("-" * 70)
    products = discovery.list_built_products()
    print(f"Built products: {products}")

    if not products:
        print("\n⚠️  No built products found!")
        print("Run: ./build_product <product>")
        return

    # Example 2: Get datastream info
    print("\nExample 2: Get Datastream Info")
    print("-" * 70)
    product = products[0]
    info = discovery.get_datastream_info(product)
    if info:
        print(f"Product: {info.product}")
        print(f"Datastream path: {info.datastream_path}")
        print(f"File size: {info.file_size:,} bytes")
        print(f"Build time: {info.build_time}")
        print(f"Profiles: {info.profiles_count}")
        print(f"Rules: {info.rules_count}")
        print(f"Exists: {info.exists}")

    # Example 3: Get rendered rule
    print("\nExample 3: Get Rendered Rule")
    print("-" * 70)
    rule_id = "accounts_password_minlen_login_defs"  # Common rule
    rendered = discovery.get_rendered_rule(product, rule_id)

    if rendered:
        print(f"Rule ID: {rendered.rule_id}")
        print(f"Product: {rendered.product}")
        print(f"Build path: {rendered.build_path}")
        print(f"\nHas rendered YAML: {rendered.rendered_yaml is not None}")
        print(f"Has rendered OVAL: {rendered.rendered_oval is not None}")
        print(f"Remediations: {list(rendered.rendered_remediations.keys())}")

        if rendered.rendered_yaml:
            print("\nRendered YAML (first 500 chars):")
            print(rendered.rendered_yaml[:500])

        if "bash" in rendered.rendered_remediations:
            print("\nBash remediation (first 300 chars):")
            print(rendered.rendered_remediations["bash"][:300])
    else:
        print(f"Rule '{rule_id}' not found in build for {product}")

    # Example 4: Search rendered content
    print("\nExample 4: Search Rendered Content")
    print("-" * 70)
    query = "password"
    results = discovery.search_rendered_content(query, product=product, limit=5)

    print(f"Found {len(results)} matches for '{query}' in {product}:")
    for result in results:
        print(f"\n  Rule: {result.rule_id}")
        print(f"  Match type: {result.match_type}")
        print(f"  Snippet: {result.match_snippet[:100]}...")

    # Example 5: Compare source vs rendered
    print("\nExample 5: Compare Source vs Rendered")
    print("-" * 70)
    rule_id = "sshd_set_idle_timeout"

    # Get source
    source = discovery.get_rule_details(rule_id)
    if source:
        print(f"Source description: {source.description[:200]}...")

    # Get rendered
    rendered = discovery.get_rendered_rule(product, rule_id)
    if rendered and rendered.rendered_yaml:
        import yaml
        rendered_data = yaml.safe_load(rendered.rendered_yaml)
        if "description" in rendered_data:
            print(f"\nRendered description: {rendered_data['description'][:200]}...")

    print("\n" + "=" * 70)
    print("Examples completed!")


if __name__ == "__main__":
    try:
        example_build_artifacts()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
