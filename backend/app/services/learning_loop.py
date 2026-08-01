"""LearningLoopService — C6.1 evidence-driven continuous learning loop.

Application service (NOT an Engine). Orchestrates existing models/engines:

  Observation -> CandidateChange -> dedup -> review -> apply
  -> GeoEvent/Memory -> recompute affected engines -> NodeSnapshot diff

Rules enforced here (config-driven via learning.yaml):
  - self_report never raises reputation
  - unverified evidence defaults to PENDING_REVIEW
  - high-impact changes require human approval
  - verified evidence may trigger recompute
  - rules and weights never auto-change
"""
import uuid, hashlib, re, json
from datetime import datetime, timezone, date
from typing import Dict, List, Optional, Any
import os as _os, yaml

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_change import CandidateChange
from app.models.evidence import Evidence
from app.models.company import Company
from app.models.capability import Capability
from app.models.geo_event import GeoEvent
from app.models.node_snapshot import NodeSnapshot
from app.models.growth_stage import GrowthStage
from app.models.reputation import Reputation

print("Phase C6.1: LearningLoopService loaded")


def _load_learning_config() -> Dict:
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                      'config', 'universe', 'learning.yaml')
    if _os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


class LearningLoopService:
    def __init__(self):
        self.config = _load_learning_config()
        self.impact_config = {i['id']: i for i in self.config.get('review', {}).get('impact_levels', [])}
        self.engine_map = self.config.get('affected_engines', {})

    # ───────────────────────── Observation intake ─────────────────────────

    async def create_observation(self, db: AsyncSession, data: Dict, actor_id: str = "system") -> CandidateChange:
        """Turn an observation into a CandidateChange with dedup + review state.

        actor_id comes from the server-side authenticated user (C6.2), never from the client.
        """
        node_id = str(data.get("node_id") or "").strip()
        change_type = (data.get("change_type") or "").strip()
        if not node_id or not change_type:
            raise ValueError("node_id and change_type are required")
        if not actor_id or actor_id == "client":
            raise ValueError("actor_id must come from the authenticated session")
        if change_type not in ("user_evidence", "evidence_verification_change", "profile_update", "admin_observation"):
            raise ValueError(f"Unsupported change_type: {change_type}")

        source_type = data.get("source_type", "user")
        source_id = str(data.get("source_id") or "") or f"{source_type}-{actor_id[:8]}"
        proposed = data.get("proposed_value") or {}
        before = data.get("before_value") or {}

        # Impact level from config
        impact = self._infer_impact(change_type, proposed)
        # Affected engines from config mapping
        affected = self._affected_engines(change_type, proposed)
        # Applicable rules (never mutable)
        rules = ["R01", "R09"] if "reputation" in affected else ["R01"]
        # Dedup hash
        dedup = self._dedup_hash(node_id, change_type, source_id, proposed)

        # Dedup: existing same hash in non-terminal state -> accumulate, not duplicate
        existing = (await db.execute(
            select(CandidateChange).where(
                CandidateChange.deduplication_hash == dedup,
                CandidateChange.review_status.in_(["OBSERVED", "PENDING_REVIEW", "APPROVED"]),
            )
        )).scalars().first()
        if existing:
            existing.occurrence_count += 1
            existing.signal_strength = min(1.0, existing.occurrence_count / 10.0)
            existing.updated_at = datetime.utcnow()
            await db.commit()
            return existing

        cc = CandidateChange(
            id=uuid.uuid4(),
            change_type=change_type,
            signal_label=data.get("label") or f"{change_type}: {node_id}",
            source=source_type,
            source_detail=data.get("source_detail"),
            source_id=source_id,
            evidence_summary=data.get("evidence_summary"),
            evidence_url=data.get("evidence_url"),
            evidence_data=data.get("evidence_data"),
            certainty_level=data.get("certainty_level", "B"),
            node_id=node_id,
            source_evidence_ids=data.get("source_evidence_ids") or [],
            before_value=before or None,
            proposed_value=proposed or None,
            confidence_level=float(data.get("confidence_level", 0.3)),
            impact_level=impact,
            deduplication_hash=dedup,
            affected_engines=affected,
            applicable_rules=rules,
            review_status="OBSERVED",
            actor_id=actor_id,
            occurrence_count=1,
            signal_strength=0.1,
            status="pending",
            source_type=data.get("source_kind", "production"),
        )
        db.add(cc)
        await db.commit()
        await db.refresh(cc)

        # Unverified/self-reported evidence always goes to PENDING_REVIEW
        await self._set_review_state(db, cc, "PENDING_REVIEW", actor_id)
        return cc

    # ───────────────────────── Review ─────────────────────────

    async def approve(self, db: AsyncSession, change_id: str, actor: str, reason: str = "") -> CandidateChange:
        cc = await self._get(db, change_id)
        if cc.review_status not in ("OBSERVED", "PENDING_REVIEW"):
            raise ValueError(f"Cannot approve change in state {cc.review_status}")
        if not actor or actor in ("system", "auto"):
            raise ValueError("high-impact changes require a human actor; self-approval by system is forbidden")
        from_status = cc.review_status
        cc.review_status = "APPROVED"
        cc.actor_id = actor
        cc.reviewed_at = datetime.utcnow()
        cc.signal_label = (cc.signal_label or "") + (f" [批准: {reason}]" if reason else "")
        await db.commit()
        await db.refresh(cc)
        await self._audit_status(db, cc, from_status, "APPROVED", actor, reason)
        return cc

    async def reject(self, db: AsyncSession, change_id: str, actor: str, reason: str) -> CandidateChange:
        cc = await self._get(db, change_id)
        if cc.review_status in ("APPLIED", "SUPERSEDED"):
            raise ValueError(f"Cannot reject change in state {cc.review_status}")
        from_status = cc.review_status
        cc.review_status = "REJECTED"
        cc.actor_id = actor
        cc.reviewed_at = datetime.utcnow()
        cc.rejection_reason = reason
        cc.status = "rejected"
        await db.commit()
        await db.refresh(cc)
        await self._audit_status(db, cc, from_status, "REJECTED", actor, reason)
        return cc

    # ───────────────────────── Apply ─────────────────────────

    async def apply(self, db: AsyncSession, change_id: str, actor: str = "admin") -> CandidateChange:
        """Apply an approved change. Idempotent: APPLIED/FAILED terminal states never re-run."""
        cc = await self._get(db, change_id)
        if cc.review_status == "APPLIED":
            return cc
        if cc.review_status != "APPROVED":
            raise ValueError(f"Cannot apply change in state {cc.review_status}; approve first")

        from_status = cc.review_status
        cc.review_status = "APPLYING"
        cc.actor_id = actor
        await db.commit()
        await self._audit_status(db, cc, from_status, "APPLYING", actor, None)

        try:
            result = await self._apply_change(db, cc)
            cc.review_status = "APPLIED"
            cc.status = "acknowledged"
            cc.applied_at = datetime.utcnow()
            cc.applied_result = result
            # Save before/after snapshot + GeoEvent + Memory
            await self._post_apply(db, cc, result)
            await db.commit()
            await self._audit_status(db, cc, "APPLYING", "APPLIED", actor, None)
        except Exception as e:
            await db.rollback()
            cc = await db.get(CandidateChange, uuid.UUID(change_id))
            if cc:
                cc.review_status = "FAILED"
                cc.applied_result = {"error": str(e)}
                await db.commit()
                await self._audit_status(db, cc, "APPLYING", "FAILED", actor, str(e)[:500])
            raise
        await db.refresh(cc)
        return cc

    async def _apply_change(self, db: AsyncSession, cc: CandidateChange) -> Dict:
        node_id = cc.node_id
        proposed = cc.proposed_value or {}
        result = {"applied": [], "recomputed": []}

        if cc.change_type == "user_evidence":
            ev = await self._add_evidence(db, node_id, proposed)
            result["applied"].append({"kind": "evidence", "id": str(ev.id)})
            # self_report / pending never raises reputation directly
            result["note"] = "evidence stored as self_report/pending; reputation unchanged until verified"

        elif cc.change_type == "evidence_verification_change":
            ev = await self._set_evidence_verified(db, proposed)
            if ev:
                result["applied"].append({"kind": "evidence_verified", "id": str(ev.id)})
                # Verified evidence may now contribute reputation (mapped, high-weight source).
                self._record_verified_reputation_event(db, node_id, ev)
                result["recomputed"].extend(await self._recompute_engines(db, node_id, ["reputation", "position"]))

        elif cc.change_type == "profile_update":
            result["applied"].extend(await self._apply_profile_update(db, node_id, proposed))
            result["recomputed"].extend(await self._recompute_engines(db, node_id, cc.affected_engines or []))

        elif cc.change_type == "admin_observation":
            await self._record_admin_observation(db, node_id, proposed)
            result["applied"].append({"kind": "geo_event"})
            result["recomputed"].extend(await self._recompute_engines(db, node_id, cc.affected_engines or []))

        return result

    async def _add_evidence(self, db, node_id: str, proposed: Dict) -> Evidence:
        claim = proposed.get("title") or proposed.get("claim") or ""
        url = proposed.get("source_url") or ""
        # C6.2 retry-safe: same claim+url never creates a duplicate evidence row.
        existing = (await db.execute(
            select(Evidence).where(Evidence.claim == claim, Evidence.source_url == url)
        )).scalars().first()
        if existing:
            return existing
        occurred = proposed.get("occurred_at")
        if isinstance(occurred, str) and occurred:
            try:
                from datetime import datetime as _dtp
                occurred = _dtp.fromisoformat(str(occurred).replace("Z", "+00:00"))
            except Exception:
                occurred = None
        ev = Evidence(
            entity_type="company",
            entity_id=uuid.UUID(node_id) if len(node_id) == 36 else node_id,
            claim=claim,
            source_url=url,
            source_name=proposed.get("source_name"),
            source_description=proposed.get("source_description"),
            occurred_at=occurred,
            confidence_level=float(proposed.get("confidence_level", 0.3)),
            source_type=proposed.get("evidence_type", "other"),
            verified=False,  # never auto-verified
        )
        db.add(ev)
        await db.commit()
        await db.refresh(ev)
        return ev

    async def _set_evidence_verified(self, db, proposed: Dict) -> Optional[Evidence]:
        ev_id = proposed.get("evidence_id")
        if not ev_id:
            return None
        ev = await db.get(Evidence, uuid.UUID(ev_id))
        if not ev:
            return None
        # C6.2: verified requires a real server-side verifier identity.
        vb = proposed.get("verified_by") or ""
        if not vb:
            raise ValueError("verified_by is required to mark evidence verified")
        try:
            verifier = uuid.UUID(str(vb))
        except (ValueError, TypeError):
            raise ValueError("verified_by must be a valid user UUID; client labels are not accepted")
        ev.verified = True
        ev.verified_by = verifier
        ev.verified_at = datetime.utcnow()
        # Verified evidence may carry higher confidence
        ev.confidence_level = max(ev.confidence_level or 0, 0.7)
        await db.commit()
        await db.refresh(ev)
        return ev

    def _record_verified_reputation_event(self, db, node_id: str, ev) -> None:
        """After external verification, record a reputation event with a verified source.

        self_report can never do this; only the verification path calls here.
        """
        try:
            from app.universe.reputation_engine import get_reputation_engine
            mapping = {
                "media_report": ("industry_citation", "association"),
                "customer_case": ("customer_success", "enterprise_customer"),
                "award_certification": ("certification_passed", "government"),
                "official_website": ("ai_search_indexed", "association"),
                "partner_org": ("relationship_established", "partner"),
                "expert_endorsement": ("peer_endorsement", "association"),
                "data_result": ("innovation_release", "association"),
                "ai_citation": ("ai_agent_cited", "ai_observation"),
            }
            et, source = mapping.get(ev.source_type or "other", ("capability_verified", "association"))
            re = get_reputation_engine()
            re.record_event(node_id, "company", et, ev.claim or "verified evidence", source)
            re.recalculate(node_id, "company")
        except Exception:
            pass

    async def _apply_profile_update(self, db, node_id: str, proposed: Dict) -> List[Dict]:
        applied = []
        company = await db.get(Company, uuid.UUID(node_id)) if len(node_id) == 36 else None
        if not company:
            # Allow provider nodes by direct id string? Keep company-only for C6.1 scope.
            company = (await db.execute(select(Company).where(Company.id == node_id))).scalars().first()
        if company:
            for field in ("website", "company_size", "headquarters", "description", "business_scope"):
                if field in proposed:
                    setattr(company, field, proposed[field])
                    applied.append({"kind": "profile_field", "field": field})
            # Capabilities
            for cap in proposed.get("capabilities", []) or []:
                name = cap.get("core_capability") or cap.get("name")
                if not name:
                    continue
                existing = (await db.execute(
                    select(Capability).where(Capability.company_id == company.id, Capability.name == name)
                )).scalars().first()
                if not existing:
                    existing = Capability(company_id=company.id, name=name, level=1, category=cap.get("product_type", "service"))
                    db.add(existing)
                    applied.append({"kind": "capability", "name": name})
            await db.commit()
        return applied

    async def _record_admin_observation(self, db, node_id: str, proposed: Dict):
        ev = GeoEvent(
            event_type="admin_observation",
            title=proposed.get("title") or "管理员产业观察",
            description=proposed.get("description") or "",
            source_node_id=uuid.UUID(node_id) if len(node_id) == 36 else None,
            source_node_type="company",
            impact_level=proposed.get("impact_level", "medium"),
            impact_score=float(proposed.get("impact_score", 0.5)),
            affected_dimensions=proposed.get("affected_dimensions"),
            source_agent="admin",
            is_processed=True,
        )
        db.add(ev)
        await db.commit()

    async def _recompute_engines(self, db, node_id: str, engines: List[str]) -> List[str]:
        """Recompute only the affected engines (never full re-run)."""
        recomputed = []
        from app.universe.context_engine import get_context_engine
        ctx = get_context_engine().understand(node_id, "company", {})
        if "position" in engines:
            recomputed.append("position")
        if "reputation" in engines:
            try:
                from app.universe.reputation_engine import get_reputation_engine
                get_reputation_engine().recalculate(node_id, "company")
                recomputed.append("reputation")
            except Exception:
                pass
        if "possibility" in engines:
            try:
                from app.universe.possibility_engine import get_possibility_engine
                get_possibility_engine().project(ctx)
                recomputed.append("possibility")
            except Exception:
                pass
        if "connection" in engines:
            try:
                from app.universe.connection_engine import get_connection_engine
                get_connection_engine().discover_connections(node_id, "company")
                recomputed.append("connection")
            except Exception:
                pass
        return recomputed

    async def _post_apply(self, db, cc: CandidateChange, result: Dict):
        """Write GeoEvent, Memory fact, and a before/after NodeSnapshot diff."""
        node_id = cc.node_id
        # GeoEvent
        db.add(GeoEvent(
            event_type=f"candidate_change_{cc.change_type}",
            title=f"变化已应用：{cc.signal_label or cc.change_type}",
            description=cc.evidence_summary or "CandidateChange applied",
            source_node_id=uuid.UUID(node_id) if len(node_id) == 36 else None,
            source_node_type="company",
            impact_level=cc.impact_level,
            impact_score=cc.confidence_level,
            affected_dimensions={"change_id": str(cc.id), "engines": cc.affected_engines},
            source_agent="learning_loop_service",
            is_processed=True,
        ))
        # Memory fact
        try:
            from app.universe.memory_engine import get_memory_engine
            mem = get_memory_engine()
            mem.record_fact(node_id=node_id, node_type="company",
                            statement=f"变化应用：{cc.change_type}（{cc.signal_label}）",
                            category="learning", source="learning_loop")
        except Exception:
            pass
        # NodeSnapshot before/after
        before = cc.before_value or {}
        db.add(NodeSnapshot(
            entity_id=uuid.UUID(node_id) if len(node_id) == 36 else node_id,
            snapshot_date=date.today(),
            snapshot_type="event",
            trigger_event=f"change_{cc.id}",
            change_summary=f"{cc.change_type}: {before} -> {cc.proposed_value}",
            is_significant=cc.impact_level == "high",
        ))
        await db.commit()

    # ───────────────────────── Helpers ─────────────────────────

    def _infer_impact(self, change_type: str, proposed: Dict) -> str:
        if change_type == "profile_update" and proposed.get("capabilities"):
            return "medium"
        if change_type == "evidence_verification_change":
            return "medium"
        if change_type == "user_evidence":
            return "low"
        if change_type == "admin_observation":
            return proposed.get("impact_level", "medium") or "medium"
        return "low"

    def _affected_engines(self, change_type: str, proposed: Dict) -> List[str]:
        if change_type == "user_evidence":
            return self.engine_map.get("evidence", [])
        if change_type == "evidence_verification_change":
            return self.engine_map.get("evidence", [])
        if change_type == "profile_update":
            return self.engine_map.get("capability", []) + self.engine_map.get("profile", [])
        if change_type == "admin_observation":
            return self.engine_map.get("industry", [])
        return []

    def _dedup_hash(self, node_id: str, change_type: str, source_id: str, proposed: Dict) -> str:
        canonical = json.dumps(proposed, sort_keys=True, ensure_ascii=False)
        raw = f"{node_id}|{change_type}|{source_id}|{canonical}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    async def _set_review_state(self, db, cc: CandidateChange, state: str, actor_id: str = "system"):
        from_status = cc.review_status
        cc.review_status = state
        await db.commit()
        await db.refresh(cc)
        await self._audit_status(db, cc, from_status, state, actor_id, None)

    async def _audit_status(self, db, cc: CandidateChange, from_status: str, to_status: str,
                            actor_id: str, reason: str = None):
        from app.models.change_audit import CandidateChangeAudit
        db.add(CandidateChangeAudit(
            change_id=str(cc.id), from_status=from_status, to_status=to_status,
            actor_id=uuid.UUID(str(actor_id)) if actor_id and len(str(actor_id)) == 36 else None,
            reason=reason,
        ))
        await db.commit()

    async def _get(self, db, change_id: str) -> CandidateChange:
        cc = await db.get(CandidateChange, uuid.UUID(change_id))
        if not cc:
            raise ValueError(f"Change not found: {change_id}")
        return cc

    # ───────────────────────── Queries ─────────────────────────

    async def list_changes(self, db, status: str = None, node_id: str = None, limit: int = 50):
        q = select(CandidateChange)
        if status:
            q = q.where(CandidateChange.review_status == status)
        if node_id:
            q = q.where(CandidateChange.node_id == node_id)
        q = q.order_by(CandidateChange.created_at.desc()).limit(limit)
        rows = (await db.execute(q)).scalars().all()
        return [self._to_dict(r) for r in rows]

    async def get_change(self, db, change_id: str) -> Optional[Dict]:
        cc = await self._get(db, change_id)
        return self._to_dict(cc)

    async def get_learning_history(self, db, node_id: str, limit: int = 30) -> List[Dict]:
        q = select(CandidateChange).where(CandidateChange.node_id == node_id)
        q = q.order_by(CandidateChange.created_at.desc()).limit(limit)
        rows = (await db.execute(q)).scalars().all()
        return [self._to_dict(r) for r in rows]

    def _to_dict(self, cc: CandidateChange) -> Dict:
        return {
            "id": str(cc.id),
            "node_id": cc.node_id,
            "change_type": cc.change_type,
            "signal_label": cc.signal_label,
            "source": cc.source,
            "source_id": cc.source_id,
            "source_evidence_ids": cc.source_evidence_ids or [],
            "before_value": cc.before_value,
            "proposed_value": cc.proposed_value,
            "confidence_level": cc.confidence_level,
            "impact_level": cc.impact_level,
            "deduplication_hash": cc.deduplication_hash,
            "affected_engines": cc.affected_engines or [],
            "applicable_rules": cc.applicable_rules or [],
            "review_status": cc.review_status,
            "reviewed_at": cc.reviewed_at.isoformat() if cc.reviewed_at else None,
            "applied_at": cc.applied_at.isoformat() if cc.applied_at else None,
            "actor_id": cc.actor_id,
            "rejection_reason": cc.rejection_reason,
            "applied_result": cc.applied_result,
            "evidence_summary": cc.evidence_summary,
            "evidence_url": cc.evidence_url,
            "occurrence_count": cc.occurrence_count,
            "created_at": cc.created_at.isoformat() if cc.created_at else None,
        }
