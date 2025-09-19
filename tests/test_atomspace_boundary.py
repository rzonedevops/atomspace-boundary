#!/usr/bin/env python3
"""
Tests for AtomSpace-Boundary implementation

These tests validate the Boundary domain model implementation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from atomspace_boundary import (
    BoundaryAtom,
    GlobalAtom,
    OrganizationAtom, 
    ProjectAtom,
    ResourceAtom,
    BoundaryAtomSpace
)


def test_boundary_atom_hierarchy():
    """Test the basic atom hierarchy"""
    print("Testing basic atom hierarchy...")
    
    # Create atoms
    global_atom = GlobalAtom("test-global")
    org = OrganizationAtom("test-org", parent=global_atom)
    project = ProjectAtom("test-project", parent=org)
    resource = ResourceAtom("test-resource", "host", parent=project)
    
    # Test parent-child relationships
    assert org.get_parent() == global_atom
    assert project.get_parent() == org
    assert resource.get_parent() == project
    
    # Test path generation
    assert global_atom.get_path() == "test-global"
    assert org.get_path() == "test-global/test-org"
    assert project.get_path() == "test-global/test-org/test-project"
    assert resource.get_path() == "test-global/test-org/test-project/test-resource"
    
    # Test containment rules
    assert global_atom.can_contain("organization")
    assert not global_atom.can_contain("project")
    assert global_atom.can_contain("resource")  # Updated: global can now contain resources
    
    assert org.can_contain("project")
    assert not org.can_contain("organization")
    assert org.can_contain("resource")  # Updated: org can now contain resources
    
    assert project.can_contain("resource")
    assert not project.can_contain("organization")
    assert not project.can_contain("project")
    
    assert not resource.can_contain("resource")
    assert not resource.can_contain("organization")
    assert not resource.can_contain("project")
    
    print("✓ Basic atom hierarchy tests passed")


def test_boundary_atomspace():
    """Test the BoundaryAtomSpace functionality"""
    print("Testing BoundaryAtomSpace...")
    
    atomspace = BoundaryAtomSpace()
    
    # Test organization creation
    org1 = atomspace.create_organization("org1")
    org2 = atomspace.create_organization("org2")
    
    assert len(atomspace.list_organizations()) == 2
    assert org1.name == "org1"
    assert org2.name == "org2"
    
    # Test project creation
    project1 = atomspace.create_project("org1", "project1")
    project2 = atomspace.create_project("org1", "project2")
    project3 = atomspace.create_project("org2", "project3")
    
    assert project1 is not None
    assert project2 is not None
    assert project3 is not None
    
    org1_projects = atomspace.list_projects("org1")
    org2_projects = atomspace.list_projects("org2")
    
    assert len(org1_projects) == 2
    assert len(org2_projects) == 1
    
    # Test resource creation
    resource1 = atomspace.create_resource("org1", "project1", "resource1", "host")
    resource2 = atomspace.create_resource("org1", "project1", "resource2", "service")
    resource3 = atomspace.create_resource("org2", "project3", "resource3", "database")
    
    assert resource1 is not None
    assert resource2 is not None
    assert resource3 is not None
    
    project1_resources = atomspace.list_resources("org1", "project1")
    project3_resources = atomspace.list_resources("org2", "project3")
    
    assert len(project1_resources) == 2
    assert len(project3_resources) == 1
    
    # Test path-based lookup
    found_resource = atomspace.get_atom_by_path("global/org1/project1/resource1")
    assert found_resource is not None
    assert found_resource.name == "resource1"
    assert found_resource.resource_type == "host"
    
    print("✓ BoundaryAtomSpace tests passed")


def test_federation_patterns():
    """Test the federation patterns described in the problem statement"""
    print("Testing federation patterns...")
    
    atomspace = BoundaryAtomSpace()
    
    # Pattern: glo/ [ org?/** ] - Global contains organization spaces
    org1 = atomspace.create_organization("acme")
    org2 = atomspace.create_organization("techcorp")
    
    global_atom = atomspace.get_global()
    organizations = global_atom.get_organizations()
    assert len(organizations) == 2
    assert any(org.name == "acme" for org in organizations)
    assert any(org.name == "techcorp" for org in organizations)
    
    # Pattern: org/ [ pro?/** ] - Organization contains project spaces  
    project1 = atomspace.create_project("acme", "web-app")
    project2 = atomspace.create_project("acme", "mobile-app")
    project3 = atomspace.create_project("techcorp", "ai-platform")
    
    acme_projects = atomspace.list_projects("acme")
    techcorp_projects = atomspace.list_projects("techcorp")
    
    assert len(acme_projects) == 2
    assert len(techcorp_projects) == 1
    assert any(proj.name == "web-app" for proj in acme_projects)
    assert any(proj.name == "mobile-app" for proj in acme_projects)
    assert any(proj.name == "ai-platform" for proj in techcorp_projects)
    
    # Pattern: pro/ [ res?/** ] - Project contains resource spaces
    resource1 = atomspace.create_resource("acme", "web-app", "web-server", "host")
    resource2 = atomspace.create_resource("acme", "web-app", "database", "database")
    resource3 = atomspace.create_resource("techcorp", "ai-platform", "gpu-cluster", "compute")
    
    webapp_resources = atomspace.list_resources("acme", "web-app")
    ai_resources = atomspace.list_resources("techcorp", "ai-platform")
    
    assert len(webapp_resources) == 2
    assert len(ai_resources) == 1
    assert any(res.name == "web-server" and res.resource_type == "host" for res in webapp_resources)
    assert any(res.name == "database" and res.resource_type == "database" for res in webapp_resources)
    assert any(res.name == "gpu-cluster" and res.resource_type == "compute" for res in ai_resources)
    
    print("✓ Federation pattern tests passed")


def test_attributes():
    """Test attribute management"""
    print("Testing attribute management...")
    
    atomspace = BoundaryAtomSpace()
    org = atomspace.create_organization("test-org")
    project = atomspace.create_project("test-org", "test-project")
    resource = atomspace.create_resource("test-org", "test-project", "test-server", "host")
    
    # Set attributes
    resource.set_attribute("ip_address", "192.168.1.100")
    resource.set_attribute("port", 8080)
    resource.set_attribute("status", "running")
    
    # Get attributes
    assert resource.get_attribute("ip_address") == "192.168.1.100"
    assert resource.get_attribute("port") == 8080
    assert resource.get_attribute("status") == "running"
    assert resource.get_attribute("nonexistent") is None
    assert resource.get_attribute("nonexistent", "default") == "default"
    
    print("✓ Attribute management tests passed")


def test_multi_level_resources():
    """Test resources at global, organization, and project levels"""
    print("Testing multi-level resources...")
    
    atomspace = BoundaryAtomSpace()
    
    # Create global resources
    global_res1 = atomspace.create_global_resource("global-dns", "service")
    global_res2 = atomspace.create_global_resource("global-backup", "storage")
    
    assert global_res1 is not None
    assert global_res2 is not None
    assert len(atomspace.list_global_resources()) == 2
    
    # Create organization and org resources
    org = atomspace.create_organization("test-org")
    org_res1 = atomspace.create_org_resource("test-org", "org-network", "network")
    org_res2 = atomspace.create_org_resource("test-org", "org-security", "service")
    
    assert org_res1 is not None
    assert org_res2 is not None
    assert len(atomspace.list_org_resources("test-org")) == 2
    
    # Create project and project resources
    project = atomspace.create_project("test-org", "test-project")
    proj_res = atomspace.create_resource("test-org", "test-project", "web-server", "host")
    
    assert proj_res is not None
    assert len(atomspace.list_resources("test-org", "test-project")) == 1
    
    # Test path hierarchies
    assert global_res1.get_path() == "global/global-dns"
    assert org_res1.get_path() == "global/test-org/org-network"
    assert proj_res.get_path() == "global/test-org/test-project/web-server"
    
    # Test containment rules
    assert atomspace.global_atom.can_contain("resource")
    assert org.can_contain("resource")
    assert project.can_contain("resource")
    
    print("✓ Multi-level resource tests passed")


def run_all_tests():
    """Run all tests"""
    print("=== Running AtomSpace-Boundary Tests ===\n")
    
    test_boundary_atom_hierarchy()
    test_boundary_atomspace()
    test_federation_patterns()
    test_attributes()
    test_multi_level_resources()
    
    print("\n=== All Tests Passed! ===")


if __name__ == "__main__":
    run_all_tests()