#!/usr/bin/env python3
"""
Comprehensive example demonstrating the complete federation structure:
- 3 enterprises (global entities)
- Each with 3 organizations (3x3=9 total)
- Each organization with 3 projects (3x3x3=27 total)
- Resources at global, organization, and project levels
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from atomspace_boundary import BoundaryAtomSpace
import json


def create_enterprise_infrastructure(enterprise_name: str, org_prefix: str) -> BoundaryAtomSpace:
    """Create infrastructure for a single enterprise"""
    print(f"\nCreating {enterprise_name} infrastructure...")
    
    # Create enterprise atomspace
    atomspace = BoundaryAtomSpace()
    atomspace.global_atom.name = enterprise_name  # Customize the global name
    
    # Create global (enterprise) level resources
    print(f"  Creating {enterprise_name} global resources...")
    atomspace.create_global_resource("enterprise-dns", "service")
    atomspace.create_global_resource("enterprise-gateway", "network")
    atomspace.create_global_resource("global-monitoring", "service")
    atomspace.create_global_resource("backup-system", "storage")
    
    # Create 3 organizations per enterprise
    organizations = []
    for i in range(1, 4):
        org_name = f"{org_prefix}-org-{i:02d}"
        print(f"  Creating organization: {org_name}")
        org = atomspace.create_organization(org_name)
        organizations.append(org_name)
        
        # Create organization level resources
        atomspace.create_org_resource(org_name, f"{org_name}-network", "network")
        atomspace.create_org_resource(org_name, f"{org_name}-security", "service")
        atomspace.create_org_resource(org_name, f"{org_name}-storage", "storage")
        
        # Create 3 projects per organization
        for j in range(1, 4):
            project_name = f"project-{j:02d}"
            print(f"    Creating project: {org_name}/{project_name}")
            project = atomspace.create_project(org_name, project_name)
            
            # Create project level resources
            for k in range(1, 4):
                resource_types = ["host", "service", "database"]
                resource_type = resource_types[(k-1) % len(resource_types)]
                resource_name = f"{project_name}-{resource_type}-{k:02d}"
                
                resource = atomspace.create_resource(org_name, project_name, resource_name, resource_type)
                
                # Add attributes to resources
                if resource:
                    resource.set_attribute("environment", "production" if k == 1 else "development")
                    resource.set_attribute("region", f"region-{i}")
                    resource.set_attribute("cost_center", org_name)
                    resource.set_attribute("created_by", enterprise_name)
                    
                    if resource_type == "host":
                        resource.set_attribute("cpu_cores", 4 * k)
                        resource.set_attribute("memory_gb", 8 * k)
                        resource.set_attribute("os", "ubuntu-22.04")
                    elif resource_type == "service":
                        resource.set_attribute("port", 8080 + k)
                        resource.set_attribute("replicas", k)
                        resource.set_attribute("protocol", "https")
                    elif resource_type == "database":
                        resource.set_attribute("engine", "postgresql")
                        resource.set_attribute("version", f"14.{k}")
                        resource.set_attribute("storage_gb", 100 * k)
    
    return atomspace


def demonstrate_enterprise_structure(enterprises: dict):
    """Demonstrate the complete enterprise structure"""
    print("\n" + "="*60)
    print("COMPREHENSIVE FEDERATION STRUCTURE")
    print("="*60)
    
    total_orgs = 0
    total_projects = 0
    total_resources = 0
    
    for enterprise_name, atomspace in enterprises.items():
        print(f"\n🏢 ENTERPRISE: {enterprise_name}")
        print("-" * 40)
        
        # Global resources
        global_resources = atomspace.list_global_resources()
        print(f"  Global Resources ({len(global_resources)}):")
        for resource in global_resources:
            print(f"    └── {resource.name} ({resource.resource_type})")
        
        # Organizations
        organizations = atomspace.list_organizations()
        total_orgs += len(organizations)
        print(f"  Organizations ({len(organizations)}):")
        
        for org in organizations:
            print(f"    🏪 {org.name}")
            
            # Organization resources
            org_resources = atomspace.list_org_resources(org.name)
            print(f"      Org Resources ({len(org_resources)}):")
            for resource in org_resources:
                print(f"        └── {resource.name} ({resource.resource_type})")
            
            # Projects
            projects = atomspace.list_projects(org.name)
            total_projects += len(projects)
            print(f"      Projects ({len(projects)}):")
            
            for project in projects:
                print(f"        📁 {project.name}")
                
                # Project resources
                resources = atomspace.list_resources(org.name, project.name)
                total_resources += len(resources)
                print(f"          Resources ({len(resources)}):")
                for resource in resources:
                    env = resource.get_attribute("environment", "unknown")
                    print(f"            └── {resource.name} ({resource.resource_type}) [{env}]")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Enterprises: {len(enterprises)}")
    print(f"  Total Organizations: {total_orgs}")
    print(f"  Total Projects: {total_projects}")
    print(f"  Total Resources: {total_resources}")
    print(f"  Expected: 3 enterprises × 3 orgs × 3 projects = 27 projects ✓")


def demonstrate_cross_enterprise_queries(enterprises: dict):
    """Demonstrate queries across multiple enterprises"""
    print("\n" + "="*60)
    print("CROSS-ENTERPRISE QUERIES")
    print("="*60)
    
    # Find all production resources across all enterprises
    print("\n1. All production resources across enterprises:")
    for enterprise_name, atomspace in enterprises.items():
        print(f"  {enterprise_name}:")
        for org in atomspace.list_organizations():
            for project in atomspace.list_projects(org.name):
                for resource in atomspace.list_resources(org.name, project.name):
                    if resource.get_attribute("environment") == "production":
                        print(f"    └── {resource.get_path()} ({resource.resource_type})")
    
    # Find all database resources across enterprises
    print("\n2. All database resources across enterprises:")
    for enterprise_name, atomspace in enterprises.items():
        print(f"  {enterprise_name}:")
        for org in atomspace.list_organizations():
            for project in atomspace.list_projects(org.name):
                for resource in atomspace.list_resources(org.name, project.name):
                    if resource.resource_type == "database":
                        version = resource.get_attribute("version", "unknown")
                        storage = resource.get_attribute("storage_gb", "unknown")
                        print(f"    └── {resource.get_path()} (v{version}, {storage}GB)")
    
    # Find high-memory hosts across enterprises
    print("\n3. High-memory hosts (>= 16GB) across enterprises:")
    for enterprise_name, atomspace in enterprises.items():
        print(f"  {enterprise_name}:")
        for org in atomspace.list_organizations():
            for project in atomspace.list_projects(org.name):
                for resource in atomspace.list_resources(org.name, project.name):
                    if resource.resource_type == "host":
                        memory = resource.get_attribute("memory_gb")
                        if memory and memory >= 16:
                            cpu = resource.get_attribute("cpu_cores", "unknown")
                            print(f"    └── {resource.get_path()} ({memory}GB RAM, {cpu} cores)")


def demonstrate_resource_levels(enterprises: dict):
    """Demonstrate resources at different levels"""
    print("\n" + "="*60)
    print("RESOURCES AT DIFFERENT LEVELS")
    print("="*60)
    
    for enterprise_name, atomspace in enterprises.items():
        print(f"\n🏢 {enterprise_name} Resource Distribution:")
        
        # Global level
        global_resources = atomspace.list_global_resources()
        print(f"  Global Level ({len(global_resources)} resources):")
        for resource in global_resources:
            print(f"    └── {resource.get_path()} ({resource.resource_type})")
        
        # Organization level
        total_org_resources = 0
        for org in atomspace.list_organizations():
            org_resources = atomspace.list_org_resources(org.name)
            total_org_resources += len(org_resources)
        print(f"  Organization Level ({total_org_resources} resources total)")
        
        # Project level
        total_project_resources = 0
        for org in atomspace.list_organizations():
            for project in atomspace.list_projects(org.name):
                project_resources = atomspace.list_resources(org.name, project.name)
                total_project_resources += len(project_resources)
        print(f"  Project Level ({total_project_resources} resources total)")


def demonstrate_federation_patterns(enterprises: dict):
    """Demonstrate the updated federation patterns"""
    print("\n" + "="*60)
    print("FEDERATION PATTERNS")
    print("="*60)
    
    print("Updated patterns implemented:")
    print("- glo/ [ org?/** | res?/** ]  => Global atom contains organizations AND resources")
    print("- org/ [ pro?/** | res?/** ]  => Organization atom contains projects AND resources")
    print("- pro/ [ res?/** ]            => Project atom contains resources")
    print("\nThis extends the HashiCorp Boundary domain model with multi-level resources.")
    
    # Show a specific example
    enterprise_name = list(enterprises.keys())[0]
    atomspace = enterprises[enterprise_name]
    
    print(f"\nExample paths in {enterprise_name}:")
    print("Global resources:")
    for resource in atomspace.list_global_resources():
        print(f"  └── {resource.get_path()}")
    
    if atomspace.list_organizations():
        org = atomspace.list_organizations()[0]
        print(f"\nOrganization resources ({org.name}):")
        for resource in atomspace.list_org_resources(org.name):
            print(f"  └── {resource.get_path()}")
        
        if atomspace.list_projects(org.name):
            project = atomspace.list_projects(org.name)[0]
            print(f"\nProject resources ({org.name}/{project.name}):")
            for resource in atomspace.list_resources(org.name, project.name):
                print(f"  └── {resource.get_path()}")


def main():
    """Create and demonstrate the comprehensive federation structure"""
    print("🚀 COMPREHENSIVE ATOMSPACE-BOUNDARY FEDERATION EXAMPLE")
    print("=" * 70)
    print("Creating 3 enterprises × 3 organizations × 3 projects structure")
    print("with resources at global, organization, and project levels")
    
    # Create 3 enterprises
    enterprises = {}
    enterprise_configs = [
        ("TechCorp-Global", "techcorp"),
        ("FinanceInc-Global", "finance"),
        ("HealthSys-Global", "health")
    ]
    
    for enterprise_name, org_prefix in enterprise_configs:
        enterprises[enterprise_name] = create_enterprise_infrastructure(enterprise_name, org_prefix)
    
    print(f"\n✅ Successfully created {len(enterprises)} enterprises!")
    
    # Demonstrate the structure
    demonstrate_enterprise_structure(enterprises)
    demonstrate_resource_levels(enterprises)
    demonstrate_cross_enterprise_queries(enterprises)
    demonstrate_federation_patterns(enterprises)
    
    # Show detailed hierarchy for one enterprise
    print("\n" + "="*60)
    print("DETAILED HIERARCHY EXAMPLE")
    print("="*60)
    enterprise_name = list(enterprises.keys())[0]
    atomspace = enterprises[enterprise_name]
    hierarchy = atomspace.get_hierarchy_info()
    print(f"\n{enterprise_name} complete structure:")
    print(json.dumps(hierarchy, indent=2))


if __name__ == "__main__":
    main()