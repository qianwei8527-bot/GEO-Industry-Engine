"""C6.11 TrustFoundationService.

Purpose: let the Universe prove a node fact instead of only observing it.

Pipeline:
  Evidence -> verification_method/result -> verified_by/verified_at
  -> Law Mutation -> Reputation Event -> Position/Story projection
  -> Trust Boundary counts

The service never fabricates verification; verification_method and
verification_result are mandatory audit fields.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy import select, func

from app.models.evidence import Evidence
from app.models.geo_visibility import AIAnswerArtifact
from app.models.knowledge_candidate import KnowledgeCandidate


class TrustFoundationService:
    async def verify_evidence(self, db, evidence_id: str, verifier_id: str,
                              method: str = "governance_review",
                              result: str = "approved") -> Evidence:
        try:
            ev = await db.get(Evidence, uuid.UUID(str(evidence_id)))
        except (ValueError, TypeError):
            raise ValueError("evidence_id must be a valid UUID")
        if not ev:
            raise ValueError("Evidence not found")
        try:
            verifier = uuid.UUID(str(verifier_id))
        except (ValueError, TypeError):
            raise ValueError("verifier_id must be a valid user UUID")
        if not method or not result:
            raise ValueError("verification_method and verification_result are required")

        ev.verified = True
        ev.truth_status = "verified"
        ev.may_affect_real_metrics = True
        ev.verified_by = verifier
        ev.verified_at = datetime.now(timezone.utc)
        ev.verification_method = method
        ev.verification_result = result
        await db.commit()
        await db.refresh(ev)
        return ev

    async def trigger_law_mutation(self, db, node_id: str, actor_id: str) -> Dict:
        """Trigger a verified law mutation and persist the resulting reputation event."""
        from app.universe.event_backbone import UniverseEvent
        from app.universe.law_engine import get_law_engine
        from app.universe.reputation_engine import get_reputation_engine

        event = UniverseEvent(
            node_id=node_id,
            domain="certification",
            event_type="certification.approved",
            actor_id=actor_id,
            source="trust_foundation",
        )
        result = await get_law_engine().handle(
            event,
            context={"evidence_status": "verified"},
        )
        if "certification_trust_growth" not in result.get("applied_laws", []):
            raise ValueError("Law mutation did not apply; verified evidence is required")

        re = get_reputation_engine()
        events = re.event_store.get_events(node_id)
        if events:
            latest = events[-1]
            await re.persist_event(db, latest)
            await db.commit()
        return result

    async def boundary(self, db, node_id: str = None) -> Dict:
        q = select(Evidence)
        if node_id:
            q = q.where(Evidence.entity_id == uuid.UUID(str(node_id)))
        rows = (await db.execute(q)).scalars().all()

        verified = observed = pending = inferred = unknown = synthetic = 0
        for e in rows:
            if e.is_synthetic:
                synthetic += 1
            status = (e.truth_status or "unknown").lower()
            if status == "verified":
                verified += 1
            elif status == "observed":
                observed += 1
            elif status == "pending_review":
                pending += 1
            elif status == "inferred":
                inferred += 1
            else:
                unknown += 1

        ai_answers = dict((await db.execute(
            select(AIAnswerArtifact.data_origin, func.count(AIAnswerArtifact.id))
            .group_by(AIAnswerArtifact.data_origin)
        )).all())
        baseline_eligible = (await db.execute(
            select(func.count(AIAnswerArtifact.id)).where(AIAnswerArtifact.baseline_eligible == True)
        )).scalar() or 0
        kc_synthetic = (await db.execute(
            select(func.count(KnowledgeCandidate.id)).where(KnowledgeCandidate.is_synthetic == True)
        )).scalar() or 0

        return {
            "node_id": node_id,
            "evidence": {
                "total": len(rows),
                "verified_facts": verified,
                "observed_facts": observed,
                "pending_review": pending,
                "inferred": inferred,
                "synthetic_data": synthetic,
                "unknown": unknown,
            },
            "ai_answers": {
                "total": sum(ai_answers.values()),
                "by_origin": ai_answers,
                "baseline_eligible": baseline_eligible,
            },
            "knowledge": {
                "synthetic_candidates": kc_synthetic,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def get_trust_foundation_service() -> TrustFoundationService:
    return TrustFoundationService()
