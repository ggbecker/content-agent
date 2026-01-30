# Build Artifacts Feature Design

## Overview

Add support for accessing rendered build artifacts from `build/<product>` directories. These files contain the final content after Jinja template processing and variable expansion, which is crucial for understanding what users actually see.

## Motivation

- Source files in the repository contain Jinja templates with custom delimiters (`{{{`, `{%`, `{{#`)
- Build process renders these templates with actual values
- Build artifacts show the final, expanded content that goes into datastreams
- After an initial build, these artifacts can be consulted many times without rebuilding
- For MCP server (reading latest master), one build per product is sufficient

## Architecture

### 1. Build Path Management

Add build directory configuration to `ContentRepository`:

```python
class ContentRepository:
    @property
    def build_path(self) -> Path:
        """Get build directory path (usually content/build)."""
        return self._repo_path / "build"

    def get_product_build_path(self, product: str) -> Optional[Path]:
        """Get build path for a specific product."""
        product_build = self.build_path / product
        return product_build if product_build.exists() else None
```

### 2. New Discovery Module: `build_artifacts.py`

Create `src/cac_mcp_server/core/discovery/build_artifacts.py`:

```python
class BuildArtifactsDiscovery:
    """Discovery and access for build artifacts."""

    def list_built_products(self) -> List[str]:
        """List products that have been built."""

    def get_rendered_rule(self, product: str, rule_id: str) -> Optional[RenderedRule]:
        """Get rendered rule content from build directory."""

    def get_rendered_profile(self, product: str, profile_id: str) -> Optional[RenderedProfile]:
        """Get rendered profile from build directory."""

    def get_datastream_info(self, product: str) -> Optional[DatastreamInfo]:
        """Get information about built datastream."""

    def search_rendered_content(self, query: str, product: Optional[str] = None) -> List[RenderResult]:
        """Search in rendered build artifacts."""
```

### 3. New Data Models

Add to `src/cac_mcp_server/models/build.py`:

```python
@dataclass
class RenderedRule:
    """Rendered rule content from build directory."""
    rule_id: str
    product: str
    rendered_yaml: str  # Fully rendered YAML
    rendered_oval: Optional[str]  # Rendered OVAL content
    rendered_remediations: Dict[str, str]  # bash, ansible, etc.
    build_path: str

@dataclass
class DatastreamInfo:
    """Information about a built datastream."""
    product: str
    datastream_path: str
    file_size: int
    build_time: datetime
    profiles_included: List[str]
    rules_count: int
```

### 4. New MCP Tools

Add to `tools.py`:

```python
{
    "name": "list_built_products",
    "description": "List products that have been built and have artifacts available",
},
{
    "name": "get_rendered_rule",
    "description": "Get fully rendered rule content from build directory (after Jinja processing)",
    "inputSchema": {
        "properties": {
            "product": {"type": "string"},
            "rule_id": {"type": "string"}
        }
    }
},
{
    "name": "search_rendered_content",
    "description": "Search in rendered build artifacts (useful for finding actual values after template expansion)",
    "inputSchema": {
        "properties": {
            "query": {"type": "string"},
            "product": {"type": "string"}  # optional
        }
    }
},
{
    "name": "get_datastream_info",
    "description": "Get information about a built datastream",
    "inputSchema": {
        "properties": {
            "product": {"type": "string"}
        }
    }
}
```

### 5. New MCP Resources

Add to `resources.py`:

```python
{
    "uri": "cac://build/products",
    "name": "Built Products",
    "description": "List of products with build artifacts"
},
{
    "uri": "cac://build/{product}/rules/{rule_id}",
    "name": "Rendered Rule",
    "description": "Fully rendered rule content from build directory"
},
{
    "uri": "cac://build/{product}/datastream",
    "name": "Datastream Info",
    "description": "Information about built datastream"
}
```

### 6. Build Trigger Tool (Optional)

Add capability to trigger builds if needed:

```python
{
    "name": "build_product_for_artifacts",
    "description": "Build a product to generate artifacts for consultation (one-time operation)",
    "inputSchema": {
        "properties": {
            "product": {"type": "string"},
            "datastream_only": {"type": "boolean", "default": True}
        }
    }
}
```

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
1. Add build path properties to `ContentRepository`
2. Create `build_artifacts.py` discovery module
3. Add data models for rendered content
4. Unit tests for build artifact discovery

### Phase 2: MCP Integration (Week 2)
1. Add new tools to `tools.py`
2. Add new resources to `resources.py`
3. Integration tests
4. Documentation updates

### Phase 3: Enhanced Features (Week 3)
1. Add search capability for rendered content
2. Add diff tool (compare source vs rendered)
3. Add build trigger tool
4. End-to-end testing

## Usage Examples

### Example 1: View Rendered Rule

```
User: "Show me the rendered version of sshd_set_idle_timeout for RHEL 9"
Claude: [calls get_rendered_rule(product="rhel9", rule_id="sshd_set_idle_timeout")]
Claude: "Here's the fully rendered rule with all Jinja templates expanded:
  title: Set SSH Idle Timeout Interval
  description: SSH allows administrators to set..."
```

### Example 2: Compare Source vs Rendered

```
User: "Compare the source and rendered versions of rule abc"
Claude: [calls get_rule_details("abc") and get_rendered_rule("rhel9", "abc")]
Claude: "Here are the differences:
  Source: description: "{{{ xccdf_value('var_sshd_idle_timeout') }}}"
  Rendered: description: "300 seconds""
```

### Example 3: Search Rendered Content

```
User: "Search for '300 seconds' in RHEL 9 build artifacts"
Claude: [calls search_rendered_content(query="300 seconds", product="rhel9")]
Claude: "Found in 5 rendered rules: sshd_set_idle_timeout, tmux_set_timeout..."
```

## Configuration

Add to `config/defaults.yaml`:

```yaml
build:
  artifacts_enabled: true
  auto_build_missing: false  # Whether to automatically build if artifacts missing
  cache_rendered: true  # Cache rendered content in memory
```

## Benefits

1. **Accurate Content View**: See exactly what goes into datastreams
2. **Template Debugging**: Compare source templates with rendered output
3. **Value Discovery**: Find actual values used in builds
4. **Build Verification**: Verify builds produced expected output
5. **One-time Build**: For read-only MCP usage, build once and query many times

## Limitations

1. Requires products to be built first
2. Build artifacts may be stale if source changes
3. Build directory can be large (consider cleanup strategy)
4. Different products may use different build paths

## Future Enhancements

1. Automatic build triggering when artifacts missing
2. Build artifact age detection and warnings
3. Incremental build support
4. Build artifact cleanup tools
5. Diff visualization tools
