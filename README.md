# atomspace-boundary

OpenCog AtomSpace variant where atoms are federated by the HashiCorp Boundary domain model.

## Overview

This project implements an AtomSpace variant that follows the [HashiCorp Boundary domain model](https://github.com/hashicorp/boundary/website/content/docs/domain-model) hierarchy:

- **Global (glo)** atom contains organization spaces → `glo/ [ org?/** ]`
- **Organization (org)** atom contains project spaces → `org/ [ pro?/** ]`  
- **Project (pro)** atom contains resource spaces → `pro/ [ res?/** ]`

## Architecture

The implementation follows a hierarchical federation model:

```
Global
├── Organization 1
│   ├── Project A
│   │   ├── Resource 1 (host)
│   │   ├── Resource 2 (service)
│   │   └── Resource 3 (database)
│   └── Project B
│       ├── Resource 4 (service)
│       └── Resource 5 (compute)
└── Organization 2
    └── Project C
        └── Resource 6 (host)
```

## Key Classes

- **`BoundaryAtom`**: Abstract base class for all atoms in the hierarchy
- **`GlobalAtom`**: Root atom containing organization spaces
- **`OrganizationAtom`**: Contains project spaces within an organization
- **`ProjectAtom`**: Contains resource spaces within a project
- **`ResourceAtom`**: Leaf nodes representing actual resources (hosts, services, etc.)
- **`BoundaryAtomSpace`**: Main interface for managing the federated atomspace

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from atomspace_boundary import BoundaryAtomSpace

# Create a new atomspace
atomspace = BoundaryAtomSpace()

# Create organizations
org = atomspace.create_organization("acme-corp")

# Create projects within organizations
project = atomspace.create_project("acme-corp", "web-platform")

# Create resources within projects
server = atomspace.create_resource("acme-corp", "web-platform", "web-server-01", "host")

# Set attributes on resources
server.set_attribute("ip_address", "192.168.1.100")
server.set_attribute("status", "running")

# Navigate the hierarchy
print(f"Server path: {server.get_path()}")
# Output: global/acme-corp/web-platform/web-server-01

# Query by path
found = atomspace.get_atom_by_path("global/acme-corp/web-platform/web-server-01")
```

## Federation Patterns

The implementation supports the following HashiCorp Boundary domain model patterns:

### 1. Global → Organization (`glo/ [ org?/** ]`)
```python
# Global atom contains organization spaces
organizations = atomspace.list_organizations()
for org in organizations:
    print(f"Organization: {org.name}")
```

### 2. Organization → Project (`org/ [ pro?/** ]`)
```python
# Organization atom contains project spaces
projects = atomspace.list_projects("acme-corp")
for project in projects:
    print(f"Project: {project.name}")
```

### 3. Project → Resource (`pro/ [ res?/** ]`)
```python
# Project atom contains resource spaces
resources = atomspace.list_resources("acme-corp", "web-platform")
for resource in resources:
    print(f"Resource: {resource.name} ({resource.resource_type})")
```

## Examples

See the `examples/` directory for complete usage examples:

- `basic_usage.py`: Demonstrates core functionality and patterns

Run the example:
```bash
python examples/basic_usage.py
```

## Testing

Run the test suite:
```bash
python tests/test_atomspace_boundary.py
```

## Related Projects

This implementation draws inspiration from:

- [HashiCorp Boundary](https://github.com/hashicorp/boundary)
- [HashiCorp Terraform Provider for Boundary](https://github.com/hashicorp/terraform-provider-boundary)
- [HashiCorp Setup Boundary](https://github.com/hashicorp/setup-boundary)
- [OpenCog AtomSpace](https://github.com/opencog/atomspace)

## License

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0).

## Contributing

Contributions are welcome! Please ensure that any changes maintain the HashiCorp Boundary domain model compatibility and include appropriate tests.
