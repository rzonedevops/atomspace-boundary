"""
Core implementation of AtomSpace-Boundary domain model
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Union, Any
from uuid import uuid4
import weakref


class BoundaryAtom(ABC):
    """
    Base class for all atoms in the Boundary domain model.
    
    Represents the core concept of an atom that can be federated
    across the Boundary hierarchy: Global > Organization > Project > Resource
    """
    
    def __init__(self, name: str, atom_type: str, parent: Optional['BoundaryAtom'] = None):
        self.id = str(uuid4())
        self.name = name
        self.atom_type = atom_type
        self.parent = weakref.ref(parent) if parent else None
        self.children: Set['BoundaryAtom'] = set()
        self.attributes: Dict[str, Any] = {}
        
        if parent:
            parent.add_child(self)
    
    def add_child(self, child: 'BoundaryAtom') -> None:
        """Add a child atom to this atom"""
        self.children.add(child)
    
    def remove_child(self, child: 'BoundaryAtom') -> None:
        """Remove a child atom from this atom"""
        self.children.discard(child)
    
    def get_parent(self) -> Optional['BoundaryAtom']:
        """Get the parent atom, if any"""
        return self.parent() if self.parent else None
    
    def get_path(self) -> str:
        """Get the full path from root to this atom"""
        path_parts = []
        current = self
        while current:
            path_parts.append(current.name)
            current = current.get_parent()
        return '/'.join(reversed(path_parts))
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on this atom"""
        self.attributes[key] = value
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get an attribute from this atom"""
        return self.attributes.get(key, default)
    
    @abstractmethod
    def can_contain(self, child_type: str) -> bool:
        """Check if this atom can contain a child of the given type"""
        pass
    
    def __str__(self) -> str:
        return f"{self.atom_type}({self.name})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, path={self.get_path()})"


class GlobalAtom(BoundaryAtom):
    """
    Global (glo) atom that contains organization spaces and global resources.
    Pattern: glo/ [ org?/** | res?/** ]
    """
    
    def __init__(self, name: str = "global"):
        super().__init__(name, "global")
    
    def can_contain(self, child_type: str) -> bool:
        """Global atoms can contain organization atoms and resources"""
        return child_type in ["organization", "resource"]
    
    def create_organization(self, name: str) -> 'OrganizationAtom':
        """Create a new organization within this global space"""
        return OrganizationAtom(name, parent=self)
    
    def create_resource(self, name: str, resource_type: str = "generic") -> 'ResourceAtom':
        """Create a new resource within this global space"""
        return ResourceAtom(name, resource_type, parent=self)
    
    def get_organizations(self) -> List['OrganizationAtom']:
        """Get all organization atoms in this global space"""
        return [child for child in self.children if isinstance(child, OrganizationAtom)]
    
    def get_resources(self) -> List['ResourceAtom']:
        """Get all resource atoms in this global space"""
        return [child for child in self.children if isinstance(child, ResourceAtom)]


class OrganizationAtom(BoundaryAtom):
    """
    Organization (org) atom that contains project spaces and organization resources.
    Pattern: org/ [ pro?/** | res?/** ]
    """
    
    def __init__(self, name: str, parent: Optional[GlobalAtom] = None):
        super().__init__(name, "organization", parent)
    
    def can_contain(self, child_type: str) -> bool:
        """Organization atoms can contain project atoms and resources"""
        return child_type in ["project", "resource"]
    
    def create_project(self, name: str) -> 'ProjectAtom':
        """Create a new project within this organization space"""
        return ProjectAtom(name, parent=self)
    
    def create_resource(self, name: str, resource_type: str = "generic") -> 'ResourceAtom':
        """Create a new resource within this organization space"""
        return ResourceAtom(name, resource_type, parent=self)
    
    def get_projects(self) -> List['ProjectAtom']:
        """Get all project atoms in this organization space"""
        return [child for child in self.children if isinstance(child, ProjectAtom)]
    
    def get_resources(self) -> List['ResourceAtom']:
        """Get all resource atoms in this organization space"""
        return [child for child in self.children if isinstance(child, ResourceAtom)]


class ProjectAtom(BoundaryAtom):
    """
    Project (pro) atom that contains resource spaces.
    Pattern: pro/ [ res?/** ]
    """
    
    def __init__(self, name: str, parent: Optional[OrganizationAtom] = None):
        super().__init__(name, "project", parent)
    
    def can_contain(self, child_type: str) -> bool:
        """Project atoms can only contain resource atoms"""
        return child_type == "resource"
    
    def create_resource(self, name: str, resource_type: str = "generic") -> 'ResourceAtom':
        """Create a new resource within this project space"""
        return ResourceAtom(name, resource_type, parent=self)
    
    def get_resources(self) -> List['ResourceAtom']:
        """Get all resource atoms in this project space"""
        return [child for child in self.children if isinstance(child, ResourceAtom)]


class ResourceAtom(BoundaryAtom):
    """
    Resource (res) atom - can be at global, organization, or project level.
    These represent actual resources like hosts, services, etc.
    """
    
    def __init__(self, name: str, resource_type: str = "generic", parent: Optional[Union[GlobalAtom, OrganizationAtom, ProjectAtom]] = None):
        super().__init__(name, "resource", parent)
        self.resource_type = resource_type
    
    def can_contain(self, child_type: str) -> bool:
        """Resource atoms are leaf nodes and cannot contain other atoms"""
        return False
    
    def get_resource_type(self) -> str:
        """Get the type of this resource"""
        return self.resource_type


class BoundaryAtomSpace:
    """
    AtomSpace implementation that manages the Boundary domain model federation.
    
    This class provides the main interface for creating and managing atoms
    in the hierarchical Boundary structure.
    """
    
    def __init__(self):
        self.global_atom = GlobalAtom()
        self.atoms_by_id: Dict[str, BoundaryAtom] = {self.global_atom.id: self.global_atom}
        self.atoms_by_path: Dict[str, BoundaryAtom] = {self.global_atom.get_path(): self.global_atom}
    
    def register_atom(self, atom: BoundaryAtom) -> None:
        """Register an atom in the atomspace"""
        self.atoms_by_id[atom.id] = atom
        self.atoms_by_path[atom.get_path()] = atom
    
    def get_atom_by_id(self, atom_id: str) -> Optional[BoundaryAtom]:
        """Get an atom by its ID"""
        return self.atoms_by_id.get(atom_id)
    
    def get_atom_by_path(self, path: str) -> Optional[BoundaryAtom]:
        """Get an atom by its path"""
        return self.atoms_by_path.get(path)
    
    def create_organization(self, name: str) -> OrganizationAtom:
        """Create a new organization in the global space"""
        org = self.global_atom.create_organization(name)
        self.register_atom(org)
        return org
    
    def create_project(self, org_name: str, project_name: str) -> Optional[ProjectAtom]:
        """Create a new project in the specified organization"""
        org = self.get_atom_by_path(f"{self.global_atom.name}/{org_name}")
        if org and isinstance(org, OrganizationAtom):
            project = org.create_project(project_name)
            self.register_atom(project)
            return project
        return None
    
    def create_resource(self, org_name: str, project_name: str, resource_name: str, 
                       resource_type: str = "generic") -> Optional[ResourceAtom]:
        """Create a new resource in the specified project"""
        project = self.get_atom_by_path(f"{self.global_atom.name}/{org_name}/{project_name}")
        if project and isinstance(project, ProjectAtom):
            resource = project.create_resource(resource_name, resource_type)
            self.register_atom(resource)
            return resource
        return None
    
    def create_global_resource(self, resource_name: str, resource_type: str = "generic") -> ResourceAtom:
        """Create a new resource at the global level"""
        resource = self.global_atom.create_resource(resource_name, resource_type)
        self.register_atom(resource)
        return resource
    
    def create_org_resource(self, org_name: str, resource_name: str, resource_type: str = "generic") -> Optional[ResourceAtom]:
        """Create a new resource at the organization level"""
        org = self.get_atom_by_path(f"{self.global_atom.name}/{org_name}")
        if org and isinstance(org, OrganizationAtom):
            resource = org.create_resource(resource_name, resource_type)
            self.register_atom(resource)
            return resource
        return None
    
    def get_global(self) -> GlobalAtom:
        """Get the global atom (root of the hierarchy)"""
        return self.global_atom
    
    def list_organizations(self) -> List[OrganizationAtom]:
        """List all organizations in the atomspace"""
        return self.global_atom.get_organizations()
    
    def list_projects(self, org_name: str) -> List[ProjectAtom]:
        """List all projects in the specified organization"""
        org = self.get_atom_by_path(f"{self.global_atom.name}/{org_name}")
        if org and isinstance(org, OrganizationAtom):
            return org.get_projects()
        return []
    
    def list_resources(self, org_name: str, project_name: str) -> List[ResourceAtom]:
        """List all resources in the specified project"""
        project = self.get_atom_by_path(f"{self.global_atom.name}/{org_name}/{project_name}")
        if project and isinstance(project, ProjectAtom):
            return project.get_resources()
        return []
    
    def list_global_resources(self) -> List[ResourceAtom]:
        """List all resources at the global level"""
        return self.global_atom.get_resources()
    
    def list_org_resources(self, org_name: str) -> List[ResourceAtom]:
        """List all resources at the organization level"""
        org = self.get_atom_by_path(f"{self.global_atom.name}/{org_name}")
        if org and isinstance(org, OrganizationAtom):
            return org.get_resources()
        return []
    
    def get_hierarchy_info(self) -> Dict[str, Any]:
        """Get information about the current hierarchy structure"""
        info = {
            "global": {
                "name": self.global_atom.name,
                "resources": [],
                "organizations": []
            }
        }
        
        # Add global level resources
        for resource in self.global_atom.get_resources():
            resource_info = {
                "name": resource.name,
                "type": resource.get_resource_type()
            }
            info["global"]["resources"].append(resource_info)
        
        for org in self.global_atom.get_organizations():
            org_info = {
                "name": org.name,
                "resources": [],
                "projects": []
            }
            
            # Add organization level resources
            for resource in org.get_resources():
                resource_info = {
                    "name": resource.name,
                    "type": resource.get_resource_type()
                }
                org_info["resources"].append(resource_info)
            
            for project in org.get_projects():
                project_info = {
                    "name": project.name,
                    "resources": []
                }
                
                for resource in project.get_resources():
                    resource_info = {
                        "name": resource.name,
                        "type": resource.get_resource_type()
                    }
                    project_info["resources"].append(resource_info)
                
                org_info["projects"].append(project_info)
            
            info["global"]["organizations"].append(org_info)
        
        return info