# content-agent

[![CI](https://github.com/ggbecker/content-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ggbecker/content-agent/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ggbecker/content-agent/branch/main/graph/badge.svg)](https://codecov.io/gh/ggbecker/content-agent)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

MCP (Model Context Protocol) server for the ComplianceAsCode/content project, enabling AI assistants like Claude to interact with security compliance automation workflows.

## Features

- **Content Discovery**: Search and explore rules, profiles, products, and templates
- **Build Artifacts**: Access rendered content from build directories (post-Jinja processing)
- **Rule Scaffolding**: Generate rule boilerplate with validation
- **Build Integration**: Trigger and monitor product/rule builds
- **Test Automation**: Execute and track Automatus test runs
- **Dual Transport**: stdio (Claude Desktop) and HTTP modes

## Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **ComplianceAsCode/content repository** - Clone it first:
   ```bash
   git clone https://github.com/ComplianceAsCode/content.git ~/workspace/content
   ```

### Installation (Local Development)

1. Clone this repository:
   ```bash
   git clone https://github.com/ggbecker/content-agent.git
   cd content-agent
   ```

2. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Verify installation:
   ```bash
   content-agent --help
   ```

### Claude Desktop Integration

#### Option 1: Using Your Existing ComplianceAsCode/content Repository

Add this to your Claude Desktop config file (`claude_desktop_config.json`):

**Location of config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "content-agent": {
      "command": "python",
      "args": ["-m", "content_agent"],
      "env": {
        "CONTENT_AGENT_CONTENT__REPOSITORY": "/home/user/workspace/content"
      }
    }
  }
}
```

Replace `/home/user/workspace/content` with the actual path to your ComplianceAsCode/content repository.

#### Option 2: Let content-agent Manage the Repository

content-agent can automatically clone and manage the ComplianceAsCode/content repository:

```json
{
  "mcpServers": {
    "content-agent": {
      "command": "python",
      "args": ["-m", "content_agent"],
      "env": {
        "CONTENT_AGENT_CONTENT__REPOSITORY": "managed",
        "CONTENT_AGENT_CONTENT__MANAGED_PATH": "~/.content-agent/content"
      }
    }
  }
}
```

**After adding the configuration:**
1. Restart Claude Desktop completely (quit and reopen)
2. Look for a hammer icon (🔨) in the bottom right - this indicates MCP servers are loaded
3. Start asking questions like "What products are available?" or "Search for SSH rules"

### Standalone Usage (CLI)

Run the MCP server directly from command line:

```bash
# Use existing content repository
content-agent --content-repo ~/workspace/content

# Use managed checkout (auto-clones to ~/.content-agent/content)
content-agent --content-repo managed

# With custom configuration file
content-agent --config config.yaml

# Debug mode with detailed logging
content-agent --content-repo ~/workspace/content --log-level DEBUG
```

**Note:** The standalone mode runs the MCP server in stdio mode, which expects MCP protocol messages. For interactive use, integrate with Claude Desktop instead.

### Troubleshooting

#### Claude Desktop Not Showing MCP Tools

1. **Check config file location:**
   - Make sure you edited the correct `claude_desktop_config.json` file
   - Verify the JSON is valid (use a JSON validator)

2. **Check Claude Desktop logs:**
   - **macOS**: `~/Library/Logs/Claude/mcp*.log`
   - **Windows**: `%APPDATA%\Claude\logs\mcp*.log`
   - **Linux**: `~/.config/Claude/logs/mcp*.log`

3. **Verify content-agent is installed:**
   ```bash
   which content-agent
   python -m content_agent --help
   ```

4. **Test manually:**
   ```bash
   content-agent --content-repo ~/workspace/content --log-level DEBUG
   ```
   You should see initialization messages. Press Ctrl+C to exit.

#### MCP Server Fails to Start

**Error: "Content repository not found"**
- Verify the path in `CONTENT_AGENT_CONTENT__REPOSITORY` exists
- Use absolute paths, not relative paths
- Ensure you have read permissions

**Error: "SSG modules not found"**
- Make sure the content repository is complete (has `ssg/` directory)
- Try using a fresh clone of ComplianceAsCode/content

**Error: "Permission denied"**
- Check that Python and content-agent are executable
- Verify file permissions on the content repository

#### Enable Debug Logging

Add debug logging to your Claude Desktop config:

```json
{
  "mcpServers": {
    "content-agent": {
      "command": "python",
      "args": ["-m", "content_agent"],
      "env": {
        "CONTENT_AGENT_CONTENT__REPOSITORY": "/home/user/workspace/content",
        "CONTENT_AGENT_LOGGING__LEVEL": "DEBUG",
        "CONTENT_AGENT_LOGGING__FILE": "/tmp/content-agent.log"
      }
    }
  }
}
```

Then check `/tmp/content-agent.log` for detailed error messages.

## Configuration

### Environment Variables

```bash
# Content repository
CONTENT_AGENT_CONTENT__REPOSITORY=/path/to/content
CONTENT_AGENT_CONTENT__BRANCH=main

# Server mode
CONTENT_AGENT_SERVER__MODE=stdio  # or http
CONTENT_AGENT_SERVER__HTTP__PORT=8080

# Build settings
CONTENT_AGENT_BUILD__MAX_CONCURRENT_BUILDS=2
CONTENT_AGENT_BUILD__TIMEOUT=3600

# Testing settings
CONTENT_AGENT_TESTING__BACKEND=podman
CONTENT_AGENT_TESTING__MAX_CONCURRENT_TESTS=4
```

### Configuration File

Create `config.yaml`:

```yaml
content:
  repository: /path/to/content
  branch: main

server:
  mode: stdio

build:
  max_concurrent_builds: 2
  timeout: 3600

testing:
  backend: podman
  max_concurrent_tests: 4
```

Run with: `content-agent --config config.yaml`

## Available Tools

### Discovery

- `list_products` - List all available products
- `get_product_details` - Get product information
- `search_rules` - Search rules by keyword, product, severity
- `get_rule_details` - Get complete rule information (automatically includes rendered content from builds!)
- `list_templates` - List available templates
- `get_template_schema` - Get template parameter schema

### Build Artifacts

- `list_built_products` - List products with build artifacts
- `get_rendered_rule` - Get fully rendered rule (after Jinja processing)
- `get_datastream_info` - Get datastream information and statistics
- `search_rendered_content` - Search in rendered build artifacts

### Scaffolding

- `generate_rule_boilerplate` - Generate basic rule structure
- `generate_rule_from_template` - Generate rule using template
- `validate_rule_yaml` - Validate rule.yml structure
- `generate_profile_boilerplate` - Generate profile structure

### Build

- `build_product` - Build complete product datastream
- `build_rule` - Build thin datastream for single rule
- `get_build_status` - Get build job status and logs

### Testing

- `run_rule_tests` - Execute Automatus tests for a rule
- `run_profile_tests` - Execute tests for all rules in profile
- `get_test_results` - Get test execution results

## Example Workflows

### Find and Understand a Rule

```
User: "Find SSH timeout rules for RHEL 9"
Claude: [calls search_rules(query="ssh timeout", product="rhel9")]
Claude: "Found 3 rules. The main one is sshd_set_idle_timeout..."
User: "Show me details"
Claude: [calls get_rule_details(rule_id="sshd_set_idle_timeout")]
Claude: "This rule checks ClientAliveInterval. I can see the source and rendered content for rhel9 and rhel10. The rendered RHEL 9 version shows ClientAliveInterval 300 (5 minutes)..."
```

### Create a New Rule

```
User: "Create a new rule for SSH MaxAuthTries"
Claude: [calls generate_rule_boilerplate(...)]
Claude: "Created rule structure at linux_os/guide/services/ssh/..."
Claude: [calls validate_rule_yaml(...)]
Claude: "Rule validates successfully!"
```

### Build and Test

```
User: "Build my new rule for RHEL 9"
Claude: [calls build_rule(product="rhel9", rule_id="sshd_max_auth_tries")]
Claude: "Build started (job: build_123)..."
Claude: [polls get_build_status(job_id="build_123")]
Claude: "Build completed! Datastream at /path/to/build/..."

User: "Run tests"
Claude: [calls run_rule_tests(...)]
Claude: "Tests started (job: test_456)..."
Claude: [polls get_test_results(job_id="test_456")]
Claude: "All 5 test scenarios passed!"
```

## Architecture

```
┌─────────────────┐
│ Claude Desktop  │
└────────┬────────┘
         │ stdio
┌────────▼─────────────────────────┐
│  content-agent          │
│  ┌────────────────────────────┐  │
│  │ MCP Protocol Layer         │  │
│  │ - Resources, Tools, Prompts│  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ Core Business Logic        │  │
│  │ - Discovery, Scaffolding   │  │
│  │ - Build, Testing           │  │
│  └────────────────────────────┘  │
└────────┬─────────────────────────┘
         │
┌────────▼─────────────────────────┐
│ ComplianceAsCode/content         │
│ - SSG modules, Build, Tests      │
└──────────────────────────────────┘
```

## Development

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ggbecker/content-agent.git
   cd content-agent
   ```

2. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Clone the ComplianceAsCode/content repository:**
   ```bash
   git clone https://github.com/ComplianceAsCode/content.git ~/workspace/content
   ```

4. **Test your local installation:**
   ```bash
   # Run with local content repo
   content-agent --content-repo ~/workspace/content --log-level DEBUG
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=content_agent --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py -v

# Run integration tests (requires content repo)
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
content-agent/
├── src/content_agent/       # Main source code
│   ├── config/              # Configuration management
│   ├── core/                # Core functionality
│   │   ├── discovery/       # Content discovery (rules, products, etc.)
│   │   ├── integration/     # ComplianceAsCode integration
│   │   └── scaffolding/     # Code generation
│   ├── models/              # Pydantic data models
│   └── server/              # MCP server implementation
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── examples/                # Example configurations
└── docs/                    # Documentation
```

## Requirements

- Python 3.11+
- ComplianceAsCode/content repository (local or managed)
- For testing: podman or docker
- For builds: CMake, standard build dependencies

## Documentation

### User Documentation
- [Architecture](docs/architecture.md)
- [API Reference](docs/api_reference.md)
- [Deployment Guide](docs/deployment.md)
- [Build Artifacts Usage](docs/BUILD_ARTIFACTS_USAGE.md) - Guide to using rendered content from builds

### ComplianceAsCode Integration
- [ComplianceAsCode Reference](docs/COMPLIANCEASCODE_REFERENCE.md) - Understanding ComplianceAsCode/content project structure
- [Compliance Summary](docs/COMPLIANCE_SUMMARY.md) - Implementation compliance status
- [Compliance Audit](docs/COMPLIANCE_AUDIT.md) - Detailed audit report

### Features
- [Build Artifacts Feature](docs/BUILD_ARTIFACTS_FEATURE.md) - Technical design for build artifacts support
- [Unified Rule Discovery](UNIFIED_RULE_DISCOVERY.md) - Automatic source + rendered content in one call

## License

Apache License 2.0 - see LICENSE file

## Contributing

Contributions welcome! Please see the ComplianceAsCode/content project for contribution guidelines.

## Support

- **Issues**: https://github.com/ggbecker/content-agent/issues
- **Documentation**: https://github.com/ggbecker/content-agent/blob/main/README.md
- **ComplianceAsCode/content**: https://github.com/ComplianceAsCode/content
