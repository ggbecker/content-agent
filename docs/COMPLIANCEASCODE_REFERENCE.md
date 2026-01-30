# ComplianceAsCode/content Project Reference

This document provides key information about the ComplianceAsCode/content project structure, conventions, and implementation details that are important for working with the codebase.

## Table of Contents

1. [Jinja2 Macros and Custom Delimiters](#jinja2-macros-and-custom-delimiters)
2. [Directory Structure](#directory-structure)
3. [Rule Files](#rule-files)
4. [Product Information](#product-information)
5. [Build System](#build-system)

## Jinja2 Macros and Custom Delimiters

ComplianceAsCode uses **custom Jinja2 delimiters** with an extra `{` and `}` to avoid conflicts with other template systems:

| Purpose | Standard Jinja2 | ComplianceAsCode |
|---------|----------------|------------------|
| Variable expansion | `{{ variable }}` | `{{{ variable }}}` |
| Control structures | `{% if condition %}` | `{{% if condition %}}` |
| Comments | `{# comment #}` | `{{# comment #}}` |

### Examples

**Variable expansion:**
```yaml
description: '{{{ ocil_package("audit") }}}'
fixtext: '{{{ package_install("audit") }}}'
srg_requirement: '{{{ srg_requirement_package_installed("audit") }}}'
```

**Control structures:**
```yaml
{{% if product in ["rhel8", "rhel9"] %}}
platforms:
    - multi_platform_rhel
{{% endif %}}
```

**Macro definitions:**
```jinja
{{% macro openshift_cluster_setting(endpoint, suppress) -%}}
This rule's check operates on the cluster configuration dump.
{{%- endmacro %}}
```

### Common Macros

Macros are defined in `shared/macros/` directory:

- `01-general.jinja` - General-purpose macros
- `10-ansible.jinja` - Ansible-specific macros
- `10-bash.jinja` - Bash remediation macros
- `10-ocil.jinja` - OCIL (manual check) macros
- `10-oval.jinja` - OVAL check macros

### Macro Usage Guidelines (ADR-0002)

**Use Jinja2 macros in:**
- Rules (descriptions, checks, remediations)
- Build scripts (internal use)

**Do NOT use Jinja2 macros in:**
- Control files (except `srg_ctr` and `srg_gpos`)
- Variable files
- Profile files

## Directory Structure

### Top-Level Directories

| Directory | Description |
|-----------|-------------|
| `linux_os` | Security content for Linux operating systems |
| `applications` | Security content for applications (OpenShift, OpenStack) |
| `shared` | Templates, Jinja macros, remediation functions |
| `products` | Per-product directories with product-specific info and profiles |
| `ssg` | Python module used by build scripts |
| `build-scripts` | Scripts used by the build system |
| `docs` | User and Developer documentation |
| `tests` | Test suite for content validation |
| `components` | Component files mapping OS components to rules |

### Benchmark Structure

Benchmarks are directories containing a `benchmark.yml` file:

- **Linux OS Benchmark**: `/linux_os/guide`
- **Applications Benchmark**: `/applications`
- **Firefox Benchmark**: `/products/firefox/guide`

Products specify which benchmark they use via `benchmark_root` in their `product.yml` file.

## Rule Files

### Rule Directory Structure

Each rule is a directory with the rule ID as its name, containing:

- `rule.yml` - Main rule definition
- `oval/` - OVAL checks (optional)
- `bash/` - Bash remediation (optional)
- `ansible/` - Ansible remediation (optional)
- `tests/` - Test scenarios (optional)

### Rule YAML Structure

```yaml
documentation_complete: true

title: 'Rule Title'

description: |-
    Multi-line description of what the rule checks.
    Can contain Jinja2 macros: {{{ complete_ocil_entry_file_permissions(file="/etc/hosts", perms="-rw-r--r--") }}}

rationale: |-
    Explanation of why this rule is important.

severity: medium  # low, medium, high, or unknown

identifiers:
    cce@rhel8: CCE-12345-6
    cce@rhel9: CCE-67890-1

references:
    nist: CM-6(a)
    disa: CCI-000366
    stigid@rhel8: RHEL-08-010010

platform: machine  # or 'container', 'multi_platform_all', etc.

ocil_clause: 'the configuration does not match'

ocil: |-
    To check, run the following command...

fixtext: |-
    To fix this, run {{{ package_install("package-name") }}}
```

### Important Fields

- `documentation_complete`: Must be `true` for the rule to be included
- `severity`: Must be `low`, `medium`, `high`, or `unknown`
- `platform`: Defines where the rule applies (machine, container, etc.)
- `identifiers`: Product-specific identifiers using `@` notation
- `references`: Compliance framework references

## Product Information

### How Products Work

Products are **NOT** directly specified in rule files. Instead, product applicability is determined by:

1. **Identifiers and References**: Using `@` notation
   ```yaml
   identifiers:
       cce@rhel8: CCE-12345-6
       cce@rhel9: CCE-67890-1
       stigid@ol8: OL08-010010

   references:
       stigid@rhel9: RHEL-09-255030
   ```

2. **Profiles**: Products include rules in their profiles
3. **Platform Applicability**: Using platform/CPE checks

### Extracting Product Information

To determine which products a rule applies to, check:

1. Parse `identifiers` for keys with `@` (e.g., `cce@rhel8` → rhel8)
2. Parse `references` for keys with `@` (e.g., `stigid@ol8` → ol8)
3. Check which product profiles include the rule

### Product Directory Structure

```
products/rhel9/
├── product.yml          # Product definition
├── profiles/           # Product-specific profiles
│   ├── cis.profile
│   ├── ospp.profile
│   └── ...
└── transforms/         # Product-specific XSLT transforms
```

### Product YAML Example

```yaml
product: rhel9
full_name: Red Hat Enterprise Linux 9
type: platform

benchmark_id: RHEL-9
benchmark_root: "../../linux_os/guide"

profiles_root: "./profiles"

pkg_manager: "dnf"
init_system: "systemd"
```

## Build System

### Build Process Overview

1. **Compile**: Resolve rules, profiles, groups to product-specific form
2. **Template**: Generate checks and remediations from templates
3. **Combine**: Merge OVAL checks into single document
4. **Link**: Link OVAL checks to XCCDF rules
5. **Compose**: Create SCAP data stream

### Key Build Scripts

- `compile_all.py` - Resolves content to product-specific form
- `build_templated_content.py` - Generates templated content
- `combine_ovals.py` - Combines OVAL checks
- `build_xccdf.py` - Generates XCCDF, OVAL, OCIL documents
- `compose_ds.py` - Creates SCAP data stream

### Jinja2 Processing

Jinja2 macros are expanded **at build time** by the SSG build system. The custom delimiters `{{{ }}}` and `{{% %}}` are processed by Python scripts in `build-scripts/` using the `ssg` module.

## References

- **Developer Documentation**: `/docs/manual/developer/`
- **Architecture Decisions**: `/docs/adr/`
- **Template Reference**: `/docs/templates/template_reference.md`
- **Style Guide**: `/docs/manual/developer/04_style_guide.md`

## Key Takeaways for MCP Server Implementation

1. **YAML Parsing**: Use `yaml.load(..., Loader=yaml.FullLoader)` to handle Jinja2 templates in YAML files
2. **Product Extraction**: Parse identifiers/references with `@` notation to determine applicable products
3. **Template Awareness**: Recognize that `{{{ }}}` and `{{% %}}` are Jinja2 macros, not invalid YAML
4. **Build-Time vs Run-Time**: Macros are expanded at build time, not at scan time
5. **No Direct Products Field**: Rules don't have a `products:` field - infer from identifiers and profile inclusion

## Version Information

This reference is based on the ComplianceAsCode/content project structure as of January 2025.
For the most up-to-date information, always refer to the official documentation in the content repository.
