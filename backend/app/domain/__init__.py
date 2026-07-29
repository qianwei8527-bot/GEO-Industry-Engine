"""GEO Domain Layer - Core business entities and value objects.

This layer is independent of infrastructure concerns. All six product systems
share these domain entities through the knowledge graph.
"""
from app.domain.entities.entity import Entity, EntityType
from app.domain.entities.company import Company
from app.domain.capability.capability import Capability
from app.domain.relationship.relationship import Relationship, RelationType
from app.domain.event.event import Event, EventType
from app.domain.evidence.evidence import Evidence
from app.domain.trust.trust import TrustScore

__all__ = [
    "Entity", "EntityType",
    "Company",
    "Capability",
    "Relationship", "RelationType",
    "Event", "EventType",
    "Evidence",
    "TrustScore",
]

