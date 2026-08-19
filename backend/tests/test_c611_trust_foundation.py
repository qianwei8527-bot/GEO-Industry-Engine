"""C6.11 Trust Foundation: verification pipeline, law mutation, boundary counts."""

import sys, uuid
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select

from app.database import _get_session_factory
from app.models.company import Company
from app.models.evidence import Evidence
from app.services.trust_foundation import TrustFoundationService
from app.universe.law_engine import UniverseLawEngine, get_law_engine
from app.universe.reputation_engine import ReputationEngine
from app.universe.memory_engine import MemoryEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine
from app.universe.event_backbone import get_event_backbone


class TestTrustFoundation:
    def setup_method(self):
        UniverseLawEngine.reset()
        ReputationEngine.reset()
        MemoryEngine.reset()
        RelationshipIntelligenceEngine.reset()
        get_event_backbone().reset()

    async def _company(self, db):
        return (await db.execute(select(Company).limit(1))).scalars().first()

    async def test_verify_evidence_writes_audit_fields(self):
        factory = _get_session_factory()
        async with factory() as db:
            company = await self._company(db)
            if not company:
                return
            ev = Evidence(
                entity_id=company.id, entity_type="company",
                claim=f"trust test {uuid.uuid4().hex[:6]}",
                source_url="https://universe.test/evidence",
                source_type="system_record", truth_status="observed",
            )
            db.add(ev)
            await db.commit()
            await db.refresh(ev)
            verifier = uuid.uuid4()
            verified = await TrustFoundationService().verify_evidence(
                db, str(ev.id), str(verifier), method="system_record_crosscheck", result="approved"
            )
            assert verified.verified is True
            assert verified.truth_status == "verified"
            assert verified.verified_by == verifier
            assert verified.verified_at is not None
            assert verified.verification_method == "system_record_crosscheck"
            assert verified.verification_result == "approved"

    async def test_verify_rejects_missing_fields(self):
        factory = _get_session_factory()
        async with factory() as db:
            company = await self._company(db)
            if not company:
                return
            ev = Evidence(
                entity_id=company.id, entity_type="company",
                claim=f"bad verify {uuid.uuid4().hex[:6]}",
                source_url="https://universe.test/bad", source_type="other",
            )
            db.add(ev)
            await db.commit()
            await db.refresh(ev)
            with pytest.raises(ValueError):
                await TrustFoundationService().verify_evidence(db, str(ev.id), str(uuid.uuid4()), method="", result="")

    async def test_law_mutation_applies_and_persists_reputation(self):
        factory = _get_session_factory()
        async with factory() as db:
            nid = str(uuid.uuid4())
            result = await TrustFoundationService().trigger_law_mutation(db, nid, str(uuid.uuid4()))
            assert "certification_trust_growth" in result["applied_laws"]
            re = ReputationEngine()
            # fresh engine reading DB to prove persistence
            ReputationEngine.reset()
            from app.universe.reputation_engine import get_reputation_engine
            fresh = get_reputation_engine()
            snap = await fresh.restore_from_db(db, nid, "company")
            assert snap.total_events >= 1

    async def test_boundary_counts(self):
        factory = _get_session_factory()
        async with factory() as db:
            company = await self._company(db)
            if not company:
                return
            boundary = await TrustFoundationService().boundary(db, str(company.id))
            assert "evidence" in boundary
            assert "verified_facts" in boundary["evidence"]
            assert "observed_facts" in boundary["evidence"]
            assert "synthetic_data" in boundary["evidence"]
            assert "unknown" in boundary["evidence"]
