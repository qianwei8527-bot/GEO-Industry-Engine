"""C6.8 Living World Model: concept emergence -> proposal -> governance -> adoption."""

import sys
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
from app.universe.world_model import get_world_model, LivingWorldModel
from app.universe.event_backbone import get_event_backbone
from app.universe.law_engine import UniverseLawEngine, get_law_engine
from app.universe.registry import get_registry
from app.universe.memory_engine import MemoryEngine
from app.universe.reputation_engine import ReputationEngine
from app.universe.relationship_intelligence import RelationshipIntelligenceEngine


class TestLivingWorldModel:
    def setup_method(self):
        LivingWorldModel.reset()
        UniverseLawEngine.reset()
        get_event_backbone().reset()
        MemoryEngine.reset()
        ReputationEngine.reset()
        RelationshipIntelligenceEngine.reset()

    def _observe(self, name="AI Agent Worker", category="role", domain="edu_tech", count=4):
        wm = get_world_model()
        sources = ["openalex", "ror", "gov_cn", "crossref"][:max(count, 1)]
        for i, source in enumerate(sources, start=1):
            wm.observe(
                name, category, source, domain=domain,
                signal_data={"claim": f"observed-{i}"},
                evidence_id=f"ev-{i}",
                observation_id=f"obs-{i}",
            )
        key = f"{category}:{name.lower()}"
        return wm, key

    async def test_emergence_lifecycle_and_provenance(self):
        wm, key = self._observe()
        cand = wm.get_candidate(key)
        assert cand.status in ("observed", "emerging")
        assert len(cand.evidence_ids) >= 3
        assert len(cand.provenance) >= 3
        wm.recognize(key, evidence_status="verified", reviewer="reviewer-1")
        assert wm.get_candidate(key).status == "recognized"
        assert wm.get_candidate(key).recognized_by == "reviewer-1"

    async def test_unverified_or_synthetic_cannot_be_recognized(self):
        wm, key = self._observe()
        with pytest.raises(ValueError):
            wm.recognize(key, evidence_status="observed")
        wm2 = get_world_model()
        wm2.observe("Fake Agent", "role", "demo", synthetic=True,
                    signal_data={"is_synthetic": True}, evidence_id="ev-s1")
        with pytest.raises(ValueError):
            wm2.recognize("role:fake agent", evidence_status="verified")

    async def test_proposal_requires_recognized_and_governance_actor(self):
        wm, key = self._observe()
        with pytest.raises(ValueError):
            wm.propose(key, proposed_by="system")
        wm.recognize(key, evidence_status="verified", reviewer="reviewer-1")
        proposal = wm.propose(key, proposed_by="reviewer-1", reason="new role observed")
        assert proposal.status == "pending"
        assert wm.get_candidate(key).status == "proposed"
        with pytest.raises(ValueError):
            wm.propose(key, proposed_by="reviewer-1")

    async def test_approval_requires_law_governance_and_human_actor(self):
        wm, key = self._observe()
        wm.recognize(key, evidence_status="verified", reviewer="reviewer-1")
        proposal = wm.propose(key, proposed_by="reviewer-1")
        with pytest.raises(ValueError):
            await wm.review_proposal(proposal.proposal_id, "system", "approved")
        approved = await wm.review_proposal(proposal.proposal_id, "reviewer-1", "approved")
        assert approved.status == "approved"
        assert "ontology_adoption_governance" in approved.law_ids
        assert approved.law_explanation
        tl = get_event_backbone().timeline()
        types = {e["event_type"] for e in tl}
        assert "ontology.proposal_created" in types
        assert "ontology.proposal_approved" in types

    async def test_rejection_requires_reason_and_keeps_candidate_recognized(self):
        wm, key = self._observe()
        wm.recognize(key, evidence_status="verified", reviewer="reviewer-1")
        proposal = wm.propose(key, proposed_by="reviewer-1")
        with pytest.raises(ValueError):
            await wm.review_proposal(proposal.proposal_id, "reviewer-2", "rejected")
        rejected = await wm.review_proposal(
            proposal.proposal_id, "reviewer-2", "rejected", reason="insufficient impact"
        )
        assert rejected.status == "rejected"
        assert wm.get_candidate(key).status == "recognized"

    async def test_adoption_does_not_mutate_registry(self):
        wm, key = self._observe(name="AI Employee", domain="edu_tech")
        wm.recognize(key, evidence_status="verified", reviewer="reviewer-1")
        proposal = wm.propose(key, proposed_by="reviewer-1")
        await wm.review_proposal(proposal.proposal_id, "reviewer-2", "approved")
        adopted = wm.adopt(proposal.proposal_id, "system_admin")
        assert adopted.status == "adopted"
        assert adopted.registry_update_pending is True
        assert wm.get_candidate(key).status == "adopted"
        assert get_registry().get_node_type("AI Employee") is None
        tl = get_event_backbone().timeline()
        assert any(e["event_type"] == "ontology.concept_adopted" for e in tl)

    async def test_industry_context_model(self):
        wm, key = self._observe(domain="edu_tech")
        ctx = wm.assess_industry("edu_tech", name="Education Technology")
        assert ctx.industry_id == "edu_tech"
        assert any(c["name"] == "AI Agent Worker" for c in ctx.emerging_concepts)
        assert "ev-1" in ctx.evidence_ids
        assert len(ctx.evidence_ids) >= 3
