"""
AtomSpace-Boundary: OpenCog AtomSpace variant federated by HashiCorp Boundary domain model

This package implements an AtomSpace variant that follows the HashiCorp Boundary
domain model hierarchy: Global > Organization > Project > Resource
"""

from .core import (
    BoundaryAtom,
    GlobalAtom,
    OrganizationAtom,
    ProjectAtom,
    ResourceAtom,
    BoundaryAtomSpace,
)

__version__ = "0.1.0"
__all__ = [
    "BoundaryAtom",
    "GlobalAtom", 
    "OrganizationAtom",
    "ProjectAtom",
    "ResourceAtom",
    "BoundaryAtomSpace",
]