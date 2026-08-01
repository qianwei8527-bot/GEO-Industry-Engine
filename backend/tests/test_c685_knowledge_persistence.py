"""C6.8.5 Knowledge Persistence Hardening: DB repository + restore."""

import sys
import uuid
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from sqlalchemy import select, func

from app.database import _get_session_factory
from app.universe.world_model import LivingWorldModel
from app.universe.event_backbone import get_event_backbone
from app.universe.law_engine import UniverseLawEngine
from app.universe.memory_engine import MemoryEngine
from app.universe.reputation_engine import ReputationEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine
from app.models.knowledge_candidate import KnowledgeCandidate
from app.models.world_model import WorldModelProposalRecord, IndustryContextRecord


class TestKnowledgePersistence:
    def setup_method(self):
        LivingWorldModel.reset()
        UniverseLawEngine.reset()
        get_event_backbone().reset()
        MemoryEngine.reset()
        ReputationEngine.reset()
        RelationshipIntelligenceEngine.reset()

    async def _seed(self, db, concept="AI Agent Worker"):
        wm = LivingWorldModel()
        key = f"role:{concept.lower()}"
        for i, source in enumerate(["openalex", "ror", "gov_cn", "crossref"], start=1):
            await wm.observe(
                concept, "role", source, domain="edu_tech",
                signal_data={"claim": f"observed-{i}"},
                evidence_id=f"ev-{i}", observation_id=f"obs-{i}", db=db,
            )
        await wm.recognize(key, evidence_status="verified", reviewer="reviewer-1", db=db)
        proposal = await wm.propose(key, proposed_by="reviewer-1", db=db)
        await wm.review_proposal(proposal.proposal_id, "reviewer-2", "approved", db=db)
        await wm.adopt(proposal.proposal_id, "system_admin", db=db)
        await wm.assess_industry("edu_tech", name="Education Technology", db=db)
        return wm, key, proposal

    async def test_rows_persisted_after_full_loop(self):
        concept = f"AI Persist {uuid.uuid4().hex[:6]}"
        factory = _get_session_factory()
        async with factory() as db:
            _, key, proposal = await self._seed(db, concept)
            cand_count = (await db.execute(
                select(func.count(KnowledgeCandidate.id)).where(KnowledgeCandidate.candidate_key == key)
            )).scalar()
            prop_rows = (await db.execute(
                select(WorldModelProposalRecord).where(WorldModelProposalRecord.proposal_id == proposal.proposal_id)
            )).scalars().all()
            ctx_count = (await db.execute(
                select(func.count(IndustryContextRecord.id)).where(IndustryContextRecord.industry_id == "edu_tech")
            )).scalar()
            assert cand_count == 1
            assert len(prop_rows) == 1
            assert prop_rows[0].status == "adopted"
            assert prop_rows[0].registry_update_pending is True
            assert "ontology_adoption_governance" in (prop_rows[0].law_ids or [])
            assert ctx_count == 1

    async def test_restore_recovers_candidates_proposals_and_contexts(self):
        concept = f"AI Restore {uuid.uuid4().hex[:6]}"
        factory = _get_session_factory()
        async with factory() as db:
            _, key, proposal = await self._seed(db, concept)
            fresh = LivingWorldModel()
            counts = await fresh.restore_from_db(db)
            assert counts["candidates"] >= 1
            assert counts["proposals"] >= 1
            assert counts["industry_contexts"] >= 1
            cand = fresh.get_candidate(key)
            assert cand is not None
            assert cand.status == "adopted"
            restored = fresh.get_proposal(proposal.proposal_id)
            assert restored is not None
            assert restored.status == "adopted"
            assert "ontology_adoption_governance" in restored.law_ids
            ctx = fresh.get_industry_context("edu_tech")
            assert ctx is not None
            assert "ev-1" in ctx.evidence_ids

    async def test_save_is_idempotent(self):
        concept = f"AI Idempotent {uuid.uuid4().hex[:6]}"
        factory = _get_session_factory()
        async with factory() as db:
            wm, key, proposal = await self._seed(db, concept)
            await wm.observe(
                concept, "role", "openalex", domain="edu_tech",
                signal_data={"claim": "again"}, evidence_id="ev-again", db=db,
            )
            count = (await db.execute(
                select(func.count(KnowledgeCandidate.id)).where(KnowledgeCandidate.candidate_key == key)
            )).scalar()
            assert count == 1
