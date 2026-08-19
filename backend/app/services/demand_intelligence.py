"""C7 Demand Intelligence Service.

DemandEvent is the "why" layer:
  actor -> scenario -> objective -> pain -> existing_solution
  -> missing_capability -> matched_nodes -> outcome

The service also performs Demand Gap Analysis against existing nodes:
  capability match -> evidence coverage -> reputation coverage.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select, func

from app.models.demand_event import DemandEvent
from app.models.capability import Capability
from app.models.company import Company
from app.models.evidence import Evidence
from app.models.reputation import Reputation


class DemandIntelligenceService:
    async def create_event(self, db, data: Dict, actor_id: str = None,
                           actor_label: str = None) -> Dict:
        question = (data.get("question_text") or "").strip()
        actor_type = (data.get("actor_type") or "").strip()
        scenario = (data.get("scenario") or "").strip()
        missing = (data.get("missing_capability") or "").strip()
        if not question or not actor_type or not scenario or not missing:
            raise ValueError("question_text, actor_type, scenario, missing_capability are required")

        synthetic = bool(data.get("is_synthetic", False))
        truth = "synthetic" if synthetic else (data.get("truth_status") or "observed")
        if truth not in ("observed", "pending_review", "verified", "synthetic"):
            raise ValueError(f"invalid truth_status: {truth}")

        ev = DemandEvent(
            event_id=str(uuid.uuid4()),
            actor_id=uuid.UUID(str(actor_id)) if actor_id else None,
            actor_type=actor_type,
            actor_label=actor_label or data.get("actor_label"),
            scenario=scenario,
            question_text=question,
            objective=data.get("objective"),
            pain=data.get("pain"),
            existing_solution=data.get("existing_solution"),
            missing_capability=missing,
            decision_stage=data.get("decision_stage", "research"),
            involved_nodes=data.get("involved_nodes") or [],
            mentioned_nodes=data.get("mentioned_nodes") or [],
            ai_answer_ids=data.get("ai_answer_ids") or [],
            final_behavior=data.get("final_behavior", "none"),
            outcome=data.get("outcome", "pending"),
            impact_level=data.get("impact_level", "medium"),
            priority=float(data.get("priority", 0) or 0),
            source=data.get("source", "user_report"),
            truth_status=truth,
            is_synthetic=synthetic,
            may_affect_real_metrics=(not synthetic) and truth in ("observed", "verified"),
            captured_at=datetime.now(timezone.utc),
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        return self._to_dict(ev)

    async def list_events(self, db, limit: int = 50) -> List[Dict]:
        rows = (await db.execute(
            select(DemandEvent).order_by(DemandEvent.created_at.desc()).limit(limit)
        )).scalars().all()
        return [self._to_dict(r) for r in rows]

    async def analyze(self, db, event_id: str) -> Dict:
        try:
            uid = uuid.UUID(str(event_id))
        except (ValueError, TypeError):
            raise ValueError("event_id must be a valid UUID")
        ev = await db.get(DemandEvent, uid)
        if not ev:
            raise ValueError("DemandEvent not found")

        pattern = f"%{ev.missing_capability}%"
        caps = (await db.execute(
            select(Capability).where(Capability.name.ilike(pattern))
        )).scalars().all()
        company_ids = list(dict.fromkeys(str(c.company_id) for c in caps))

        matched = []
        for cid in company_ids:
            company_uid = uuid.UUID(cid)
            company = await db.get(Company, company_uid)
            if not company:
                continue
            total = (await db.execute(
                select(func.count(Evidence.id)).where(Evidence.entity_id == company_uid)
            )).scalar() or 0
            verified = (await db.execute(
                select(func.count(Evidence.id)).where(
                    Evidence.entity_id == company_uid,
                    Evidence.truth_status == "verified",
                )
            )).scalar() or 0
            rep = (await db.execute(
                select(Reputation).where(
                    Reputation.node_id == company_uid,
                    Reputation.node_type == "company",
                ).order_by(Reputation.created_at.desc()).limit(1)
            )).scalars().first()
            rep_score = rep.total_score if rep else 0
            coverage = round(
                min(1.0, verified / 3.0) * 0.6
                + min(1.0, total / 10.0) * 0.2
                + min(1.0, rep_score / 100.0) * 0.2,
                2,
            )
            matched.append({
                "node_id": str(company_uid),
                "node_type": "company",
                "name": company.name,
                "evidence_count": total,
                "verified_count": verified,
                "reputation_score": rep_score,
                "reputation_level": rep.reputation_level if rep else "N/A",
                "coverage_score": coverage,
                "reason": f"capability {ev.missing_capability} matched",
            })

        matched.sort(key=lambda x: x["coverage_score"], reverse=True)
        top = matched[:10]
        ev.matched_node_ids = [m["node_id"] for m in top]
        await db.commit()

        from app.universe.rules import get_rule_engine
        rule = get_rule_engine().cite("R02", f"Demand creates Connection: {len(top)} candidate nodes")
        gap_score = round(1 - (top[0]["coverage_score"] if top else 0), 2)
        return {
            "event_id": str(ev.id),
            "missing_capability": ev.missing_capability,
            "gap_score": gap_score,
            "matched_nodes": top,
            "matched_count": len(top),
            "universe_rule": rule,
            "summary": (
                f"{len(top)} nodes can serve '{ev.missing_capability}'; "
                f"world gap {gap_score:.2f}."
            ),
        }

    def _to_dict(self, ev: DemandEvent) -> Dict:
        return {
            "id": str(ev.id),
            "event_id": ev.event_id,
            "actor_id": str(ev.actor_id) if ev.actor_id else None,
            "actor_type": ev.actor_type,
            "actor_label": ev.actor_label,
            "scenario": ev.scenario,
            "question_text": ev.question_text,
            "objective": ev.objective,
            "pain": ev.pain,
            "existing_solution": ev.existing_solution,
            "missing_capability": ev.missing_capability,
            "decision_stage": ev.decision_stage,
            "involved_nodes": ev.involved_nodes or [],
            "mentioned_nodes": ev.mentioned_nodes or [],
            "ai_answer_ids": ev.ai_answer_ids or [],
            "matched_node_ids": ev.matched_node_ids or [],
            "final_behavior": ev.final_behavior,
            "outcome": ev.outcome,
            "impact_level": ev.impact_level,
            "priority": ev.priority,
            "source": ev.source,
            "truth_status": ev.truth_status,
            "is_synthetic": ev.is_synthetic,
            "may_affect_real_metrics": ev.may_affect_real_metrics,
            "captured_at": ev.captured_at.isoformat() if ev.captured_at else None,
            "created_at": ev.created_at.isoformat() if ev.created_at else None,
        }


def get_demand_intelligence_service() -> DemandIntelligenceService:
    return DemandIntelligenceService()
