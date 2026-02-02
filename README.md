# content-agent

[![CI](https://github.com/ComplianceAsCode/content-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ComplianceAsCode/content-agent/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ComplianceAsCode/content-agent/branch/main/graph/badge.svg)](https://codecov.io/gh/ComplianceAsCode/content-agent)
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

### Installation

```bash
pip install content-agent
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "content-agent": {
      "command": "python",
      "args": ["-m", "content_agent"],
      "env": {
        "CONTENT_AGENT_CONTENT__REPOSITORY": "/path/to/content"
      }
    }
  }
}
```

Restart Claude Desktop and start asking questions about ComplianceAsCode content!

### Standalone Usage

```bash
# Use existing content repository
content-agent --content-repo /path/to/content

# Use managed checkout (auto-clones and updates)
content-agent --content-repo managed

# HTTP mode for web integrations
content-agent --mode http --port 8080
```

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

### Setup

```bash
git clone https://github.com/ComplianceAsCode/content-agent
cd content-agent
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
pytest --cov=content_agent --cov-report=html
```

### Code Quality

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
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

- Issues: https://github.com/ComplianceAsCode/content-agent/issues
- Documentation: https://github.com/ComplianceAsCode/content-agent/blob/main/README.md
