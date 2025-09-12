#!/usr/bin/env python3
"""
Example usage of AtomSpace-Boundary implementation

This example demonstrates how to use the Boundary domain model
with the AtomSpace variant.
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from atomspace_boundary import BoundaryAtomSpace


def main():
    """Demonstrate the AtomSpace-Boundary implementation"""
    print("=== AtomSpace-Boundary Example ===\n")
    
    # Create a new boundary atomspace
    atomspace = BoundaryAtomSpace()
    
    # Create organizations (org atoms in global space)
    print("Creating organizations...")
    acme_org = atomspace.create_organization("acme-corp")
    tech_org = atomspace.create_organization("tech-innovators")
    
    # Create projects within organizations
    print("Creating projects...")
    web_project = atomspace.create_project("acme-corp", "web-platform")
    mobile_project = atomspace.create_project("acme-corp", "mobile-app")
    ai_project = atomspace.create_project("tech-innovators", "ai-research")
    
    # Create resources within projects
    print("Creating resources...")
    atomspace.create_resource("acme-corp", "web-platform", "web-server-01", "host")
    atomspace.create_resource("acme-corp", "web-platform", "database-cluster", "database")
    atomspace.create_resource("acme-corp", "web-platform", "load-balancer", "service")
    
    atomspace.create_resource("acme-corp", "mobile-app", "api-gateway", "service")
    atomspace.create_resource("acme-corp", "mobile-app", "auth-service", "service")
    
    atomspace.create_resource("tech-innovators", "ai-research", "gpu-cluster", "compute")
    atomspace.create_resource("tech-innovators", "ai-research", "ml-pipeline", "service")
    
    # Demonstrate hierarchy traversal
    print("\n=== Hierarchy Information ===")
    hierarchy = atomspace.get_hierarchy_info()
    print(json.dumps(hierarchy, indent=2))
    
    # Demonstrate path-based lookup
    print("\n=== Path-based Lookups ===")
    web_server = atomspace.get_atom_by_path("global/acme-corp/web-platform/web-server-01")
    if web_server:
        print(f"Found: {web_server}")
        print(f"Path: {web_server.get_path()}")
        print(f"Type: {web_server.atom_type}")
        if hasattr(web_server, 'resource_type'):
            print(f"Resource Type: {web_server.resource_type}")
    
    # Demonstrate pattern matching (simulating Boundary domain model queries)
    print("\n=== Pattern Matching Examples ===")
    
    # glo/ [ org?/** ] - Global contains organization spaces
    print("Global organizations:")
    for org in atomspace.list_organizations():
        print(f"  - {org.name} (path: {org.get_path()})")
    
    # org/ [ pro?/** ] - Organization contains project spaces
    print("\nAcme Corp projects:")
    for project in atomspace.list_projects("acme-corp"):
        print(f"  - {project.name} (path: {project.get_path()})")
    
    # pro/ [ res?/** ] - Project contains resource spaces
    print("\nWeb Platform resources:")
    for resource in atomspace.list_resources("acme-corp", "web-platform"):
        print(f"  - {resource.name} ({resource.resource_type}) (path: {resource.get_path()})")
    
    # Demonstrate attribute setting
    print("\n=== Attribute Management ===")
    web_server.set_attribute("ip_address", "192.168.1.100")
    web_server.set_attribute("port", 8080)
    web_server.set_attribute("status", "running")
    
    print(f"Web server attributes:")
    for key, value in web_server.attributes.items():
        print(f"  {key}: {value}")
    
    print("\n=== Federation Patterns ===")
    print("The following patterns are implemented:")
    print("- glo/ [ org?/** ]  => Global atom contains organization spaces")
    print("- org/ [ pro?/** ]  => Organization atom contains project spaces") 
    print("- pro/ [ res?/** ]  => Project atom contains resource spaces")
    print("\nThis follows the HashiCorp Boundary domain model hierarchy.")


if __name__ == "__main__":
    main()