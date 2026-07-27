import pytest
import uuid
from datetime import datetime
from app.domain.entities.entity import Entity, EntityType
from app.domain.entities.company import Company
from app.domain.capability.capability import Capability, CapabilityLevel
from app.domain.evidence.evidence import Evidence, ConfidenceLevel
from app.domain.trust.trust import TrustService

class TestDomainModels:
    def test_entity_creation(self):
        e = Entity(name="Test Corp", entity_type=EntityType.COMPANY)
        assert e.geo_id.startswith("GEO-COMP-")
        assert e.id is not None
        assert e.created_at is not None

    def test_company_inherits_entity(self):
        c = Company(name="Test Ltd", website="https://test.com")
        assert c.entity_type == EntityType.COMPANY
        assert c.geo_id.startswith("GEO-COMP-")
        assert c.website == "https://test.com"

    def test_capability_value_object(self):
        cap = Capability(name="AI Dev", company_id=str(uuid.uuid4()), level=CapabilityLevel.L2)
        assert cap.level == CapabilityLevel.L2

    def test_trust_empty(self):
        score = TrustService.compute("e-1", [])
        assert score.score == 0.0

    def test_trust_with_evidence(self):
        ev = Evidence(target_id="e-1", claim="Has AI", source_url="https://x.com")
        score = TrustService.compute("e-1", [ev])
        assert score.score == 20.0
        assert score.evidence_count == 1

    def test_relationship(self):
        from app.domain.relationship.relationship import Relationship, RelationType
        rel = Relationship(source_id="a", target_id="b", relation_type=RelationType.PARTNER)
        assert rel.relation_type.value == "partner"

    def test_event(self):
        from app.domain.event.event import Event, EventType
        ev = Event(entity_id="e-1", event_type=EventType.FUNDING, title="Series A")
        assert ev.occurred_at is not None