"""
Advanced example demonstrating Boundary domain model federation

This example shows more complex scenarios including:
- Multi-level queries
- Cross-organizational resource discovery
- Attribute-based filtering
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from atomspace_boundary import BoundaryAtomSpace
import json


def create_sample_infrastructure(atomspace):
    """Create a sample multi-org infrastructure"""
    
    # Create organizations
    acme = atomspace.create_organization("acme-corp")
    tech = atomspace.create_organization("tech-innovations")
    startup = atomspace.create_organization("quick-startup")
    
    # ACME Corp infrastructure
    web_proj = atomspace.create_project("acme-corp", "web-services")
    data_proj = atomspace.create_project("acme-corp", "data-platform")
    
    # Web services resources
    web1 = atomspace.create_resource("acme-corp", "web-services", "web-server-01", "host")
    web2 = atomspace.create_resource("acme-corp", "web-services", "web-server-02", "host")
    lb = atomspace.create_resource("acme-corp", "web-services", "load-balancer", "service")
    cache = atomspace.create_resource("acme-corp", "web-services", "redis-cache", "service")
    
    # Data platform resources
    db_primary = atomspace.create_resource("acme-corp", "data-platform", "postgres-primary", "database")
    db_replica = atomspace.create_resource("acme-corp", "data-platform", "postgres-replica", "database")
    etl = atomspace.create_resource("acme-corp", "data-platform", "etl-pipeline", "service")
    
    # Tech Innovations infrastructure
    ai_proj = atomspace.create_project("tech-innovations", "ai-research")
    ml_proj = atomspace.create_project("tech-innovations", "ml-ops")
    
    # AI research resources
    gpu1 = atomspace.create_resource("tech-innovations", "ai-research", "gpu-node-01", "compute")
    gpu2 = atomspace.create_resource("tech-innovations", "ai-research", "gpu-node-02", "compute")
    storage = atomspace.create_resource("tech-innovations", "ai-research", "data-lake", "storage")
    
    # ML ops resources
    model_api = atomspace.create_resource("tech-innovations", "ml-ops", "model-api", "service")
    monitoring = atomspace.create_resource("tech-innovations", "ml-ops", "ml-monitor", "service")
    
    # Quick Startup (minimal setup)
    app_proj = atomspace.create_project("quick-startup", "mvp-app")
    app_server = atomspace.create_resource("quick-startup", "mvp-app", "app-server", "host")
    app_db = atomspace.create_resource("quick-startup", "mvp-app", "sqlite-db", "database")
    
    # Set attributes on resources
    web1.set_attribute("ip_address", "10.0.1.10")
    web1.set_attribute("cpu_cores", 4)
    web1.set_attribute("memory_gb", 16)
    web1.set_attribute("status", "running")
    web1.set_attribute("environment", "production")
    
    web2.set_attribute("ip_address", "10.0.1.11")
    web2.set_attribute("cpu_cores", 4)
    web2.set_attribute("memory_gb", 16)
    web2.set_attribute("status", "running")
    web2.set_attribute("environment", "production")
    
    gpu1.set_attribute("gpu_type", "NVIDIA A100")
    gpu1.set_attribute("gpu_memory_gb", 80)
    gpu1.set_attribute("cpu_cores", 64)
    gpu1.set_attribute("memory_gb", 512)
    gpu1.set_attribute("status", "training")
    gpu1.set_attribute("environment", "research")
    
    db_primary.set_attribute("version", "postgresql-14")
    db_primary.set_attribute("storage_gb", 1000)
    db_primary.set_attribute("read_replicas", 2)
    db_primary.set_attribute("status", "active")
    db_primary.set_attribute("environment", "production")
    
    app_server.set_attribute("ip_address", "192.168.1.100")
    app_server.set_attribute("cpu_cores", 2)
    app_server.set_attribute("memory_gb", 8)
    app_server.set_attribute("status", "running")
    app_server.set_attribute("environment", "development")


def demonstrate_federation_queries(atomspace):
    """Demonstrate various federation query patterns"""
    
    print("=== Federation Query Examples ===\n")
    
    # 1. Global → Organization pattern
    print("1. Global organizations (glo/ [ org?/** ]):")
    for org in atomspace.list_organizations():
        project_count = len(atomspace.list_projects(org.name))
        print(f"   └── {org.name} ({project_count} projects)")
    
    print()
    
    # 2. Organization → Project pattern  
    print("2. Organization projects (org/ [ pro?/** ]):")
    for org in atomspace.list_organizations():
        projects = atomspace.list_projects(org.name)
        if projects:
            print(f"   {org.name}:")
            for project in projects:
                resource_count = len(atomspace.list_resources(org.name, project.name))
                print(f"      └── {project.name} ({resource_count} resources)")
    
    print()
    
    # 3. Project → Resource pattern
    print("3. Project resources (pro/ [ res?/** ]):")
    for org in atomspace.list_organizations():
        for project in atomspace.list_projects(org.name):
            resources = atomspace.list_resources(org.name, project.name)
            if resources:
                print(f"   {org.name}/{project.name}:")
                for resource in resources:
                    print(f"      └── {resource.name} ({resource.resource_type})")
    
    print()


def demonstrate_cross_org_queries(atomspace):
    """Demonstrate cross-organizational queries"""
    
    print("=== Cross-Organizational Queries ===\n")
    
    # Find all resources of a specific type across organizations
    print("1. All database resources across organizations:")
    for org in atomspace.list_organizations():
        for project in atomspace.list_projects(org.name):
            for resource in atomspace.list_resources(org.name, project.name):
                if resource.resource_type == "database":
                    print(f"   └── {resource.get_path()} ({resource.get_attribute('version', 'unknown')})")
    
    print()
    
    # Find all production resources
    print("2. All production resources:")
    for org in atomspace.list_organizations():
        for project in atomspace.list_projects(org.name):
            for resource in atomspace.list_resources(org.name, project.name):
                if resource.get_attribute("environment") == "production":
                    status = resource.get_attribute("status", "unknown")
                    print(f"   └── {resource.get_path()} [{status}]")
    
    print()
    
    # Find high-memory resources
    print("3. High-memory resources (>= 16GB):")
    for org in atomspace.list_organizations():
        for project in atomspace.list_projects(org.name):
            for resource in atomspace.list_resources(org.name, project.name):
                memory = resource.get_attribute("memory_gb")
                if memory and memory >= 16:
                    cpu = resource.get_attribute("cpu_cores", "unknown")
                    print(f"   └── {resource.get_path()} ({memory}GB RAM, {cpu} cores)")
    
    print()


def demonstrate_hierarchy_traversal(atomspace):
    """Demonstrate hierarchy traversal patterns"""
    
    print("=== Hierarchy Traversal Patterns ===\n")
    
    # Bottom-up traversal
    print("1. Bottom-up traversal (Resource → Global):")
    web_server = atomspace.get_atom_by_path("global/acme-corp/web-services/web-server-01")
    if web_server:
        current = web_server
        path_elements = []
        while current:
            path_elements.append(f"{current.atom_type}({current.name})")
            current = current.get_parent()
        
        print(f"   Path: {' → '.join(reversed(path_elements))}")
    
    print()
    
    # Find parent project of a resource
    print("2. Parent lookup:")
    gpu_node = atomspace.get_atom_by_path("global/tech-innovations/ai-research/gpu-node-01")
    if gpu_node:
        project = gpu_node.get_parent()
        org = project.get_parent() if project else None
        global_atom = org.get_parent() if org else None
        
        print(f"   Resource: {gpu_node.name}")
        print(f"   Project: {project.name if project else 'None'}")
        print(f"   Organization: {org.name if org else 'None'}")
        print(f"   Global: {global_atom.name if global_atom else 'None'}")
    
    print()


def demonstrate_attribute_filtering(atomspace):
    """Demonstrate attribute-based filtering"""
    
    print("=== Attribute-Based Filtering ===\n")
    
    # Find all running resources
    print("1. All running resources:")
    running_resources = []
    for org in atomspace.list_organizations():
        for project in atomspace.list_projects(org.name):
            for resource in atomspace.list_resources(org.name, project.name):
                if resource.get_attribute("status") == "running":
                    running_resources.append(resource)
    
    for resource in running_resources:
        env = resource.get_attribute("environment", "unknown")
        print(f"   └── {resource.get_path()} [{env}]")
    
    print()
    
    # Group resources by environment
    print("2. Resources grouped by environment:")
    env_groups = {}
    for org in atomspace.list_organizations():
        for project in atomspace.list_projects(org.name):
            for resource in atomspace.list_resources(org.name, project.name):
                env = resource.get_attribute("environment", "unknown")
                if env not in env_groups:
                    env_groups[env] = []
                env_groups[env].append(resource)
    
    for env, resources in env_groups.items():
        print(f"   {env.upper()}:")
        for resource in resources:
            print(f"      └── {resource.get_path()}")
    
    print()


def main():
    """Run the advanced federation example"""
    print("=== Advanced AtomSpace-Boundary Federation Example ===\n")
    
    atomspace = BoundaryAtomSpace()
    
    print("Creating sample multi-organization infrastructure...")
    create_sample_infrastructure(atomspace)
    
    print("Infrastructure created successfully!\n")
    
    demonstrate_federation_queries(atomspace)
    demonstrate_cross_org_queries(atomspace)
    demonstrate_hierarchy_traversal(atomspace)
    demonstrate_attribute_filtering(atomspace)
    
    # Show complete hierarchy
    print("=== Complete Hierarchy Structure ===")
    hierarchy = atomspace.get_hierarchy_info()
    print(json.dumps(hierarchy, indent=2))


if __name__ == "__main__":
    main()