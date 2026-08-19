"""C7.4 Demand Driven Connection.

Projects a DemandEvent gap into ConnectionCandidates:
  Capability -> Evidence -> Reputation -> Trust -> Connection Value

Trust hardening (C7.4-R):
  - only verified Evidence can raise evidence/trust/connection scores
  - every score is clamped to [0, 1]
  - truth_status is derived from DemandEvent + target evidence, not single-inherited
  - formal accepted/completed requires verified Candidate in production scope
  - synthetic/observed transitions are simulation/internal only
  - DB unique(demand_event_id, target_node_id, connection_type) guarantees idempotency
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List

import yaml
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models.demand_event import DemandEvent
from app.models.connection_candidate import ConnectionCandidate
from app.models.capability import Capability
from app.models.company import Company
from app.models.evidence import Evidence
from app.models.reputation import Reputation

_DEFAULTS = {
    'version': '1.0.0',
    'weights': {'capability': 0.35, 'evidence': 0.25, 'reputation': 0.20, 'trust': 0.20},
    'evidence': {'verified_weight': 1.0, 'observed_weight': 0.0,
                 'min_verified_for_full': 3, 'max_evidence_for_full': 10},
    'reputation': {'max_score': 100.0},
    'trust': {'evidence_weight': 0.6, 'reputation_weight': 0.4},
}


def _clamp(value: float) -> float:
    return round(min(1.0, max(0.0, float(value))), 4)


def _load_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        'config', 'universe', 'demand_connection.yaml',
    )
    if os.path.exists(p):
        raw = open(p, encoding='utf-8').read()
        data = yaml.safe_load(raw) or {}
        data['config_hash'] = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]
        return data
    data = dict(_DEFAULTS)
    data['config_hash'] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    return data


class DemandConnectionService:
    def __init__(self):
        self.config = _load_config()

    async def generate(self, db, demand_event_id: str) -> Dict:
        try:
            demand = await db.get(DemandEvent, uuid.UUID(str(demand_event_id)))
        except (ValueError, TypeError):
            raise ValueError("demand_event_id must be a valid UUID")
        if not demand:
            raise ValueError("DemandEvent not found")

        pattern = f"%{demand.missing_capability}%"
        caps = (await db.execute(
            select(Capability).where(Capability.name.ilike(pattern))
        )).scalars().all()

        grouped: Dict[str, List[Capability]] = {}
        for c in caps:
            grouped.setdefault(str(c.company_id), []).append(c)

        candidates = []
        for company_id, cap_list in grouped.items():
            candidate = await self._build_candidate(db, demand, company_id, cap_list)
            candidates.append(candidate)

        return {
            "demand_event_id": str(demand.id),
            "generated": len(candidates),
            "candidates": [self._to_dict(c) for c in candidates],
        }

    async def _build_candidate(self, db, demand: DemandEvent, company_id: str,
                               cap_list: List[Capability]) -> ConnectionCandidate:
        company = await db.get(Company, uuid.UUID(company_id))
        if not company:
            raise ValueError(f"Company not found: {company_id}")

        evidence_rows = (await db.execute(
            select(Evidence).where(Evidence.entity_id == company.id).limit(200)
        )).scalars().all()
        verified_rows = [e for e in evidence_rows if e.truth_status == "verified"]
        observed_count = sum(1 for e in evidence_rows if e.truth_status in ("observed", "pending_review", "inferred"))
        synthetic_count = sum(1 for e in evidence_rows if e.is_synthetic or e.truth_status == "synthetic")
        verified_count = len(verified_rows)

        rep = (await db.execute(
            select(Reputation).where(
                Reputation.node_id == company.id,
                Reputation.node_type == "company",
            ).order_by(Reputation.created_at.desc()).limit(1)
        )).scalars().first()

        ev_cfg = self.config.get('evidence', {})
        verified_weight = ev_cfg.get('verified_weight', 1.0)
        min_verified = ev_cfg.get('min_verified_for_full', 3)

        capability_score = _clamp(0.6 + max(c.level for c in cap_list) / 10.0)
        evidence_score = _clamp(min(1.0, verified_count / min_verified) * verified_weight)
        reputation_score = _clamp((rep.total_score if rep else 0) / self.config.get('reputation', {}).get('max_score', 100.0))
        trust_cfg = self.config.get('trust', {})
        trust_score = _clamp(
            trust_cfg.get('evidence_weight', 0.6) * evidence_score
            + trust_cfg.get('reputation_weight', 0.4) * reputation_score
        )
        weights = self.config.get('weights', {})
        connection_score = _clamp(
            weights.get('capability', 0.35) * capability_score
            + weights.get('evidence', 0.25) * evidence_score
            + weights.get('reputation', 0.20) * reputation_score
            + weights.get('trust', 0.20) * trust_score
        )

        # truth is jointly derived from DemandEvent + target evidence
        if demand.is_synthetic or demand.truth_status == "synthetic" or synthetic_count > 0:
            truth_status = "synthetic"
        elif demand.truth_status == "verified" and verified_count > 0:
            truth_status = "verified"
        else:
            truth_status = "observed"
        may_affect = truth_status == "verified"

        connection_type = company.entity_type or "company"
        dedup = hashlib.sha256(
            f"{demand.id}|{company.id}|{connection_type}".encode()
        ).hexdigest()[:32]

        existing = (await db.execute(
            select(ConnectionCandidate).where(ConnectionCandidate.deduplication_hash == dedup)
        )).scalars().first()

        explanation = (
            f"capability={capability_score}, evidence={evidence_score}, "
            f"reputation={reputation_score}, trust={trust_score}, "
            f"connection={connection_score}, truth={truth_status}, "
            f"rule={self.config.get('version')}, config={self.config.get('config_hash')}"
        )
        fields = {
            "target_node_id": str(company.id),
            "connection_type": connection_type,
            "matched_capabilities": [c.name for c in cap_list],
            "evidence_ids": [str(e.id) for e in verified_rows],
            "verified_evidence_count": verified_count,
            "observed_evidence_count": observed_count,
            "synthetic_evidence_count": synthetic_count,
            "capability_score": capability_score,
            "evidence_score": evidence_score,
            "reputation_score": reputation_score,
            "trust_score": trust_score,
            "connection_score": connection_score,
            "explanation": explanation,
            "truth_status": truth_status,
            "may_affect_real_metrics": may_affect,
            "rule_version": self.config.get('version', '1.0.0'),
            "config_version": self.config.get('version', '1.0.0'),
            "config_hash": self.config.get('config_hash'),
        }
        if existing:
            for key, value in fields.items():
                setattr(existing, key, value)
            existing.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(existing)
            return existing

        candidate = ConnectionCandidate(
            candidate_id=str(uuid.uuid4()),
            demand_event_id=demand.id,
            source_node_id=str(demand.actor_id) if demand.actor_id else None,
            deduplication_hash=dedup,
            **fields,
        )
        db.add(candidate)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            candidate = (await db.execute(
                select(ConnectionCandidate).where(ConnectionCandidate.deduplication_hash == dedup)
            )).scalars().first()
            if candidate:
                for key, value in fields.items():
                    setattr(candidate, key, value)
                candidate.updated_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(candidate)
        await db.refresh(candidate)
        return candidate

    async def list(self, db, demand_event_id: str = None, limit: int = 100) -> List[Dict]:
        q = select(ConnectionCandidate).order_by(ConnectionCandidate.connection_score.desc())
        if demand_event_id:
            q = q.where(ConnectionCandidate.demand_event_id == uuid.UUID(str(demand_event_id)))
        rows = (await db.execute(q.limit(limit))).scalars().all()
        return [self._to_dict(r) for r in rows]

    async def get(self, db, candidate_id: str) -> Dict:
        try:
            row = await db.get(ConnectionCandidate, uuid.UUID(str(candidate_id)))
        except (ValueError, TypeError):
            raise ValueError("candidate_id must be a valid UUID")
        if not row:
            raise ValueError("ConnectionCandidate not found")
        return self._to_dict(row)

    async def decide(self, db, candidate_id: str, decision: str,
                     source: str = "rule", actor: str = None,
                     reason: str = None, scope: str = "production") -> Dict:
        try:
            candidate = await db.get(ConnectionCandidate, uuid.UUID(str(candidate_id)))
        except (ValueError, TypeError):
            raise ValueError("candidate_id must be a valid UUID")
        if not candidate:
            raise ValueError("ConnectionCandidate not found")
        if scope not in ("production", "internal", "simulation"):
            raise ValueError("decision_scope must be production/internal/simulation")

        allowed = {
            "proposed": ["qualified", "rejected"],
            "qualified": ["accepted", "rejected"],
            "accepted": ["completed"],
            "rejected": [],
        }
        if decision not in allowed.get(candidate.status, []):
            raise ValueError(f"invalid transition from {candidate.status} to {decision}")
        if decision == "rejected" and not (reason or "").strip():
            raise ValueError("rejection requires a reason")
        if source not in ("rule", "agent", "human"):
            raise ValueError("decision_source must be rule/agent/human")

        if decision in ("qualified", "accepted", "completed"):
            if candidate.truth_status == "verified":
                if scope != "production":
                    raise ValueError("verified candidate decisions require production scope")
            elif candidate.truth_status == "observed":
                if decision == "qualified":
                    if scope not in ("internal", "simulation"):
                        raise ValueError("observed candidate can only be qualified in internal/simulation scope")
                elif scope != "simulation":
                    raise ValueError("observed candidate cannot be accepted/completed in production")
            else:  # synthetic
                if scope != "simulation":
                    raise ValueError("synthetic candidate can only be exercised in simulation scope")

        candidate.status = decision
        candidate.decision_source = source
        candidate.decision_scope = scope
        candidate.decided_by = actor
        candidate.decision_reason = reason
        candidate.decided_at = datetime.now(timezone.utc)
        candidate.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(candidate)
        return self._to_dict(candidate)

    async def record_outcome(self, db, candidate_id: str, outcome: str, actor: str = None) -> Dict:
        if outcome not in ("won", "lost", "unknown"):
            raise ValueError("outcome must be won/lost/unknown")
        try:
            candidate = await db.get(ConnectionCandidate, uuid.UUID(str(candidate_id)))
        except (ValueError, TypeError):
            raise ValueError("candidate_id must be a valid UUID")
        if not candidate:
            raise ValueError("ConnectionCandidate not found")
        candidate.outcome = outcome
        candidate.decided_by = actor
        candidate.decided_at = datetime.now(timezone.utc)
        candidate.updated_at = datetime.now(timezone.utc)
        demand = await db.get(DemandEvent, candidate.demand_event_id)
        if demand and outcome in ("won", "lost"):
            demand.outcome = outcome
            demand.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(candidate)
        return self._to_dict(candidate)

    async def boundary(self, db) -> Dict:
        rows = (await db.execute(select(ConnectionCandidate))).scalars().all()
        by_truth: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        real = synthetic = 0
        for r in rows:
            by_truth[r.truth_status] = by_truth.get(r.truth_status, 0) + 1
            by_status[r.status] = by_status.get(r.status, 0) + 1
            if r.may_affect_real_metrics:
                real += 1
            else:
                synthetic += 1
        return {
            "total": len(rows),
            "by_truth_status": by_truth,
            "by_status": by_status,
            "may_affect_real_metrics": real,
            "synthetic_isolated": synthetic,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _to_dict(self, c: ConnectionCandidate) -> Dict:
        return {
            "id": str(c.id),
            "candidate_id": c.candidate_id,
            "demand_event_id": str(c.demand_event_id),
            "source_node_id": c.source_node_id,
            "target_node_id": c.target_node_id,
            "connection_type": c.connection_type,
            "matched_capabilities": c.matched_capabilities or [],
            "evidence_ids": c.evidence_ids or [],
            "verified_evidence_count": c.verified_evidence_count,
            "observed_evidence_count": c.observed_evidence_count,
            "synthetic_evidence_count": c.synthetic_evidence_count,
            "capability_score": c.capability_score,
            "evidence_score": c.evidence_score,
            "reputation_score": c.reputation_score,
            "trust_score": c.trust_score,
            "connection_score": c.connection_score,
            "explanation": c.explanation,
            "truth_status": c.truth_status,
            "status": c.status,
            "decision_source": c.decision_source,
            "decision_scope": c.decision_scope,
            "may_affect_real_metrics": c.may_affect_real_metrics,
            "outcome": c.outcome,
            "decided_by": c.decided_by,
            "decision_reason": c.decision_reason,
            "decided_at": c.decided_at.isoformat() if c.decided_at else None,
            "rule_version": c.rule_version,
            "config_version": c.config_version,
            "config_hash": c.config_hash,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }


def get_demand_connection_service() -> DemandConnectionService:
    return DemandConnectionService()
