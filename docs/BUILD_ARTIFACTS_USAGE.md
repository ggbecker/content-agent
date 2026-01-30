# Build Artifacts Feature - Usage Guide

## Overview

The build artifacts feature provides access to rendered content from `build/<product>` directories. These files contain the final content after Jinja template processing and variable expansion, showing exactly what goes into the datastreams.

## Why Build Artifacts?

### The Problem
- Source files contain Jinja templates with custom delimiters: `{{{`, `{%`, `{{#`
- Variables like `{{{ xccdf_value('var_sshd_idle_timeout') }}}` are expanded at build time
- Templates show what *could* be, but builds show what *actually is*

### The Solution
- After building a product, the `build/<product>` directory contains fully rendered files
- Build once, query many times
- See the actual values that users will receive

## Prerequisites

### Building Products

Before using build artifact features, you need to build at least one product:

```bash
cd /path/to/ComplianceAsCode/content
./build_product rhel9
```

This creates `build/rhel9/` with all rendered files.

**Note:** For the MCP server reading latest master, one build per product is typically sufficient unless you're actively developing.

## Available Tools

### 1. list_built_products

List all products that have been built and have artifacts available.

**Example:**
```
User: "Which products have been built?"
Claude: [calls list_built_products]
Response: {
  "products": ["fedora", "rhel9", "rhel8", "ol8"],
  "count": 4
}
```

### 2. get_rendered_rule

Get the fully rendered version of a rule for a specific product.

**Parameters:**
- `product`: Product identifier (e.g., "rhel9")
- `rule_id`: Rule identifier (e.g., "sshd_set_idle_timeout")

**Example:**
```
User: "Show me the rendered version of sshd_set_idle_timeout for RHEL 9"
Claude: [calls get_rendered_rule(product="rhel9", rule_id="sshd_set_idle_timeout")]
Response: {
  "rule_id": "sshd_set_idle_timeout",
  "product": "rhel9",
  "rendered_yaml": "title: Set SSH Idle Timeout Interval\ndescription: SSH allows...",
  "rendered_oval": "<def-group>...</def-group>",
  "rendered_remediations": {
    "bash": "#!/bin/bash\necho 'ClientAliveInterval 300' >> /etc/ssh/sshd_config"
  },
  "build_path": "build/rhel9/rules/sshd_set_idle_timeout"
}
```

**What You Get:**
- `rendered_yaml`: The rule.yml with all Jinja variables expanded
- `rendered_oval`: The OVAL check with actual values
- `rendered_remediations`: Bash, Ansible, etc. scripts with variables substituted
- `build_path`: Where to find these files in the build directory

### 3. get_datastream_info

Get information about a built datastream.

**Parameters:**
- `product`: Product identifier

**Example:**
```
User: "Tell me about the RHEL 9 datastream"
Claude: [calls get_datastream_info(product="rhel9")]
Response: {
  "product": "rhel9",
  "datastream_path": "build/ssg-rhel9-ds.xml",
  "file_size": 10485760,
  "build_time": "2026-01-28T10:32:15Z",
  "profiles_count": 15,
  "rules_count": 450,
  "exists": true
}
```

**Use Cases:**
- Check if a product has been built
- See when it was last built (to detect staleness)
- Get quick statistics (profile count, rule count)

### 4. search_rendered_content

Search for text in rendered build artifacts.

**Parameters:**
- `query`: Search query
- `product` (optional): Limit to a specific product
- `limit` (optional): Maximum results (default: 50)

**Example:**
```
User: "Search for 'ClientAliveInterval 300' in RHEL 9 builds"
Claude: [calls search_rendered_content(query="ClientAliveInterval 300", product="rhel9")]
Response: [
  {
    "rule_id": "sshd_set_idle_timeout",
    "product": "rhel9",
    "match_type": "remediation_bash",
    "match_snippet": "...echo 'ClientAliveInterval 300' >> /etc/ssh/sshd_config...",
    "file_path": "build/rhel9/rules/sshd_set_idle_timeout/bash.sh"
  }
]
```

**Use Cases:**
- Find which rules use a specific value
- Search for actual configuration strings (not template variables)
- Locate where specific commands appear in remediations

## Available Resources

Resources provide read-only access through URIs:

### cac://build
List all built products
```
GET cac://build
→ {"products": ["rhel9", "fedora"], "count": 2}
```

### cac://build/{product}
Get datastream info for a product
```
GET cac://build/rhel9
→ {datastream info}
```

### cac://build/{product}/rules/{rule_id}
Get rendered rule content
```
GET cac://build/rhel9/rules/sshd_set_idle_timeout
→ {rendered rule with YAML, OVAL, remediations}
```

## Common Use Cases

### Use Case 1: Compare Source vs Rendered

See what Jinja templates expand to:

```
User: "Compare the source and rendered versions of sshd_set_idle_timeout"

Claude:
1. [calls get_rule_details("sshd_set_idle_timeout")]
   Source: description: "{{{ xccdf_value('var_sshd_idle_timeout') }}}"

2. [calls get_rendered_rule(product="rhel9", rule_id="sshd_set_idle_timeout")]
   Rendered: description: "300 seconds"

Result: "The template variable {{{ xccdf_value('var_sshd_idle_timeout') }}}
expands to '300 seconds' in RHEL 9."
```

### Use Case 2: Find Actual Values

Find what value a rule actually uses:

```
User: "What idle timeout value does RHEL 9 actually use for SSH?"

Claude: [calls get_rendered_rule(product="rhel9", rule_id="sshd_set_idle_timeout")]

Result: "Based on the rendered content, RHEL 9 uses ClientAliveInterval 300
(5 minutes) for SSH idle timeout."
```

### Use Case 3: Debug Build Output

Check if a rule built correctly:

```
User: "Did my new rule build_correctly for RHEL 9?"

Claude: [calls get_rendered_rule(product="rhel9", rule_id="my_new_rule")]

Result: Shows the fully rendered content or error if not found.
```

### Use Case 4: Search for Security Settings

Find which rules set a specific value:

```
User: "Which RHEL 9 rules set password minimum length to 14?"

Claude: [calls search_rendered_content(query="minlen=14", product="rhel9")]

Result: Lists all rules with remediations or OVAL checks containing "minlen=14"
```

## Build Directory Structure

Understanding the build directory structure helps interpret results:

```
build/
├── rhel9/
│   ├── ssg-rhel9-ds.xml          # Main datastream
│   ├── rules/
│   │   ├── sshd_set_idle_timeout/
│   │   │   ├── rule.yml           # Rendered YAML
│   │   │   ├── bash.sh            # Rendered bash remediation
│   │   │   ├── ansible.yml        # Rendered ansible remediation
│   │   │   └── oval/
│   │   │       └── sshd_set_idle_timeout.xml  # Rendered OVAL
│   ├── guides/
│   │   └── ssg-rhel9-guide-*.html
│   └── ansible/
│       └── rhel9-playbook-*.yml
└── fedora/
    └── ...
```

## Best Practices

### 1. Build Once, Query Many Times

For read-only MCP usage (consulting latest master):
- Build each product once after cloning/updating the repository
- Use build artifacts for queries without rebuilding
- Only rebuild when source content changes

```bash
# Initial setup
./build_product rhel9
./build_product rhel8
./build_product fedora
# Now use MCP tools to query build artifacts
```

### 2. Check Build Staleness

If source files have changed, rebuild:

```
User: "When was RHEL 9 last built?"
Claude: [calls get_datastream_info(product="rhel9")]
→ "Last built: 2026-01-15"

User: "That's old, please rebuild it"
# (Future: add build trigger tool)
```

### 3. Combine with Source Queries

Use both source and rendered content for complete understanding:

1. Use `get_rule_details()` to see the template structure
2. Use `get_rendered_rule()` to see the actual values
3. Compare to understand variable expansion

### 4. Product-Specific Differences

Remember that the same rule may render differently for different products:

```
get_rendered_rule(product="rhel9", rule_id="rule_x")  # May use value A
get_rendered_rule(product="rhel8", rule_id="rule_x")  # May use value B
```

## Limitations

### 1. Requires Build First
- Build artifacts only exist after running `./build_product`
- Tools will return "not found" if product hasn't been built

### 2. May Be Stale
- Build artifacts don't auto-update when source changes
- Check `build_time` to detect staleness
- Rebuild manually when needed

### 3. Large Build Directories
- Full product builds can be several GB
- Consider building only needed products
- Clean up old builds periodically

### 4. Build-Specific Paths
- Paths in `build/` may vary by product or build configuration
- The discovery module searches common locations
- Some files may not be found if in unexpected locations

## Troubleshooting

### "Rendered rule not found"

**Problem:** The rule hasn't been built for that product.

**Solutions:**
1. Build the product: `./build_product <product>`
2. Check if the rule actually applies to that product
3. Try `list_built_products()` to see what's available

### "No build directory"

**Problem:** No builds have been performed.

**Solution:** Run `./build_product <product>` at least once.

### "Build artifacts are old"

**Problem:** Source has changed since last build.

**Solution:** Rebuild the product: `./build_product <product>`

### Search returns no results

**Problem:** Search query may be in source templates, not rendered output.

**Try:**
1. Use `search_rules()` to search source content
2. Use `search_rendered_content()` for built artifacts
3. Check both to find where content appears

## Future Enhancements

Planned improvements:

1. **Auto-build trigger**: Add tool to trigger builds from MCP
2. **Build age warnings**: Warn when artifacts are stale
3. **Incremental builds**: Support faster rebuilds of changed rules
4. **Diff tool**: Built-in comparison of source vs rendered
5. **Build cleanup**: Tool to manage old build artifacts

## Summary

Build artifacts provide crucial visibility into the final rendered content:

- **See actual values** after template expansion
- **Search real content** that goes into datastreams
- **Debug build output** to verify correctness
- **One build** supports many queries
- **Complement source content** for complete understanding

Use build artifacts whenever you need to know "what actually is" versus "what could be".
