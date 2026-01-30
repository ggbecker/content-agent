# API Reference

## MCP Resources

Resources provide read-only access to content via URI.

### Products

**List all products**
```
URI: cac://products
Returns: JSON array of ProductSummary objects
```

**Get product details**
```
URI: cac://products/{product_id}
Example: cac://products/rhel9
Returns: ProductDetails object
```

### Rules

**List rules**
```
URI: cac://rules
Returns: JSON array of RuleSearchResult objects (limited to 100)
```

**Get rule details**
```
URI: cac://rules/{rule_id}
Example: cac://rules/sshd_set_idle_timeout
Returns: RuleDetails object
```

### Templates

**List templates**
```
URI: cac://templates
Returns: JSON array of TemplateSummary objects
```

**Get template schema**
```
URI: cac://templates/{template_name}
Example: cac://templates/sshd_lineinfile
Returns: TemplateSchema object
```

### Profiles

**List all profiles**
```
URI: cac://profiles
Returns: JSON array of ProfileSummary objects
```

**Get profile details**
```
URI: cac://profiles/{product}/{profile_id}
Example: cac://profiles/rhel9/ospp
Returns: ProfileDetails object
```

### Controls

**List control frameworks**
```
URI: cac://controls
Returns: JSON array of control framework names
```

## MCP Tools

Tools are invokable actions that perform operations.

### Discovery Tools

#### list_products

List all available products.

**Parameters:** None

**Returns:**
```json
[
  {
    "product_id": "rhel9",
    "name": "Red Hat Enterprise Linux 9",
    "product_type": "rhel",
    "version": "9",
    "description": "Security compliance content for RHEL 9"
  }
]
```

#### get_product_details

Get detailed information about a product.

**Parameters:**
- `product_id` (string, required): Product identifier

**Returns:** ProductDetails object

**Example:**
```json
{
  "product_id": "rhel9",
  "name": "Red Hat Enterprise Linux 9",
  "profiles": ["ospp", "stig", "cis"],
  "benchmark_root": "linux_os/guide",
  "product_dir": "products/rhel9"
}
```

#### search_rules

Search for rules by keyword, product, or severity.

**Parameters:**
- `query` (string, optional): Search query (matches ID, title, description)
- `product` (string, optional): Filter by product ID
- `severity` (string, optional): Filter by severity (low, medium, high, unknown)
- `limit` (integer, optional): Maximum results (default: 50)

**Returns:** Array of RuleSearchResult objects

**Example:**
```json
[
  {
    "rule_id": "sshd_set_idle_timeout",
    "title": "Set SSH Idle Timeout Interval",
    "severity": "medium",
    "description": "Configure SSH to automatically terminate...",
    "products": ["rhel7", "rhel8", "rhel9"],
    "file_path": "linux_os/guide/services/ssh/..."
  }
]
```

#### get_rule_details

Get complete information about a rule.

**Parameters:**
- `rule_id` (string, required): Rule identifier

**Returns:** RuleDetails object with full metadata, remediations, tests

#### list_templates

List all available rule templates.

**Parameters:** None

**Returns:** Array of TemplateSummary objects

#### get_template_schema

Get parameter schema for a template.

**Parameters:**
- `template_name` (string, required): Template name

**Returns:** TemplateSchema object with parameter definitions

#### list_profiles

List profiles for a product or all products.

**Parameters:**
- `product` (string, optional): Filter by product ID

**Returns:** Array of ProfileSummary objects

#### get_profile_details

Get detailed information about a profile.

**Parameters:**
- `profile_id` (string, required): Profile identifier
- `product` (string, required): Product identifier

**Returns:** ProfileDetails object

### Scaffolding Tools

#### generate_rule_boilerplate

Generate basic rule structure with boilerplate files.

**Parameters:**
- `rule_id` (string, required): Rule identifier (directory name)
- `title` (string, required): Rule title
- `description` (string, required): Rule description
- `severity` (string, required): Rule severity (low, medium, high, unknown)
- `product` (string, required): Primary product
- `location` (string, optional): Custom location path
- `rationale` (string, optional): Rule rationale

**Returns:** ScaffoldingResult object

**Example:**
```json
{
  "success": true,
  "rule_id": "sshd_max_auth_tries",
  "rule_dir": "linux_os/guide/services/ssh/ssh_server/sshd_max_auth_tries",
  "files_created": [
    "linux_os/.../rule.yml",
    "linux_os/.../bash/",
    "linux_os/.../ansible/",
    "linux_os/.../oval/",
    "linux_os/.../tests/"
  ],
  "message": "Rule boilerplate created successfully"
}
```

#### validate_rule_yaml

Validate rule.yml YAML content.

**Parameters:**
- `rule_yaml` (string, required): YAML content to validate
- `check_references` (boolean, optional): Check reference format (default: true)
- `auto_fix` (boolean, optional): Attempt auto-fixing (default: false)

**Returns:** ValidationResult object

**Example:**
```json
{
  "valid": false,
  "errors": [
    {
      "field": "severity",
      "error": "Invalid severity value 'critical'",
      "line": 5,
      "suggestion": "Use one of: low, medium, high, unknown"
    }
  ],
  "warnings": [],
  "fixes_applied": []
}
```

#### generate_rule_from_template

Generate rule using a template (Phase 3 feature - not yet implemented).

**Parameters:**
- `template_name` (string, required): Template name
- `parameters` (object, required): Template parameters
- `rule_id` (string, required): Rule identifier
- `product` (string, required): Product identifier

**Returns:** ScaffoldingResult object

## Data Models

### ProductSummary

```typescript
{
  product_id: string;
  name: string;
  product_type: string;
  version?: string;
  description?: string;
}
```

### ProductDetails

```typescript
{
  product_id: string;
  name: string;
  product_type: string;
  version?: string;
  description?: string;
  profiles: string[];
  benchmark_root: string;
  product_dir: string;
  cpe?: string;
  stats?: ProductStats;
  last_modified?: string;
}
```

### RuleSearchResult

```typescript
{
  rule_id: string;
  title: string;
  severity: string;
  description?: string;
  products: string[];
  file_path: string;
}
```

### RuleDetails

```typescript
{
  rule_id: string;
  title: string;
  description: string;
  rationale?: string;
  severity: string;
  identifiers: RuleIdentifiers;
  references: RuleReferences;
  products: string[];
  platforms: string[];
  remediations: Record<string, boolean>;
  checks: Record<string, boolean>;
  test_scenarios: string[];
  file_path: string;
  rule_dir: string;
  last_modified?: string;
  template?: Record<string, string>;
}
```

### ValidationResult

```typescript
{
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  fixes_applied: string[];
}
```

### ScaffoldingResult

```typescript
{
  success: boolean;
  rule_id: string;
  rule_dir: string;
  message: string;
  files_created: string[];
  validation?: ValidationResult;
}
```

## Error Handling

All tools return structured error messages in the response:

```json
{
  "error": "Error message describing what went wrong",
  "details": "Additional details if available"
}
```

Common errors:
- Resource not found (e.g., invalid product_id, rule_id)
- Invalid parameters (e.g., wrong severity value)
- Validation failures
- File system errors

## Usage Examples

### Example 1: Find SSH Rules

```javascript
// Search for SSH-related rules
search_rules({
  query: "ssh timeout",
  severity: "medium",
  limit: 10
})

// Get details for a specific rule
get_rule_details({
  rule_id: "sshd_set_idle_timeout"
})
```

### Example 2: Create New Rule

```javascript
// Generate rule boilerplate
generate_rule_boilerplate({
  rule_id: "sshd_max_auth_tries",
  title: "Set SSH MaxAuthTries",
  description: "Configure maximum authentication attempts",
  severity: "medium",
  product: "rhel9",
  rationale: "Limit brute force attack attempts"
})

// Validate the generated rule
validate_rule_yaml({
  rule_yaml: "...",
  check_references: true
})
```

### Example 3: Explore Products

```javascript
// List all products
list_products()

// Get details for RHEL 9
get_product_details({
  product_id: "rhel9"
})

// List profiles for RHEL 9
list_profiles({
  product: "rhel9"
})
```
