# NodeActivationService — C6.0 real node onboarding orchestration.
#
# This is an APPLICATION SERVICE, not a new Engine. It orchestrates
# existing models and existing Universe engines to bring a real node
# into Universe:
#
#   Company -> Identity -> Capability -> Evidence -> Observation
#   -> Context -> Position -> Reputation -> Possibility -> Connection
#   -> Memory -> Snapshot -> Home
#
# Every step is tracked (started/completed/failed), failures are recorded,
# retries are safe, and activation is idempotent via idempotency_key.
# One company never creates duplicate nodes or duplicate evidence.

import uuid
import os as _os
from datetime import datetime, date, timezone
from typing import Dict, List, Optional, Any
import yaml
import re

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity
from app.models.company import Company
from app.models.capability import Capability
from app.models.evidence import Evidence
from app.models.identity_profile import IdentityProfile
from app.models.node_snapshot import NodeSnapshot
from app.models.growth_stage import GrowthStage
from app.models.reputation import Reputation
from app.models.geo_event import GeoEvent
from app.models.onboarding_session import OnboardingSession

print("Phase C6.0: NodeActivationService loaded")


def _load_onboarding_config() -> Dict:
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))),
                      'config', 'universe', 'onboarding.yaml')
    if _os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


class NodeActivationService:
    """Orchestrates the full onboarding pipeline for one company node."""

    def __init__(self):
        self.config = _load_onboarding_config()

    # ───────────────────────────── Session ─────────────────────────────

    async def create_session(self, db: AsyncSession, idempotency_key: str,
                             company_name: str = "", user_id=None) -> OnboardingSession:
        """Create a draft session bound to the current user (C6.2)."""
        existing = (await db.execute(
            select(OnboardingSession).where(OnboardingSession.idempotency_key == idempotency_key)
        )).scalars().first()
        if existing:
            return existing
        session = OnboardingSession(
            idempotency_key=idempotency_key,
            session_status="draft",
            current_step=1,
            company_name=company_name or None,
            user_id=user_id,
            data_json={},
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def save_draft(self, db: AsyncSession, session_id: str,
                         data: Dict, current_step: int = 1) -> OnboardingSession:
        """Save partial onboarding data for a draft session."""
        session = await db.get(OnboardingSession, uuid.UUID(session_id))
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        if session.session_status not in ("draft", "validated", "failed"):
            raise ValueError(f"Session in status {session.session_status} cannot be edited")
        merged = dict(session.data_json or {})
        merged.update(data or {})
        session.data_json = merged
        session.current_step = max(current_step, session.current_step or 1)
        if data and data.get("company_name"):
            session.company_name = data["company_name"]
        session.session_status = "draft"
        session.error_message = None
        await db.commit()
        await db.refresh(session)
        return session

    # ───────────────────────── Validation ─────────────────────────────

    async def validate(self, db: AsyncSession, session: OnboardingSession) -> Dict:
        """Validate completeness, duplicate company, evidence format."""
        data = session.data_json or {}
        issues = []
        warnings = []

        # Required identity
        if not data.get("company_name"):
            issues.append({"field": "company_name", "message": "企业名称必填"})
        if not data.get("description"):
            issues.append({"field": "description", "message": "企业简介必填"})
        if not data.get("industry_id"):
            issues.append({"field": "industry_id", "message": "一级行业必选"})

        # Capabilities: at least one product with core capability
        products = data.get("products") or []
        if not products:
            issues.append({"field": "products", "message": "至少录入一个产品/服务"})
        else:
            missing_caps = [p.get("name", "") for p in products if not p.get("core_capability")]
            if missing_caps:
                issues.append({"field": "core_capability", "message": "产品必须填写核心能力"})

        # Evidence format
        evidence_items = data.get("evidence_items") or []
        for i, ev in enumerate(evidence_items):
            url = ev.get("source_url") or ""
            if self.config.get("validation", {}).get("evidence_url_required", True):
                if not url.startswith("http://") and not url.startswith("https://"):
                    issues.append({"field": f"evidence[{i}].source_url",
                                   "message": "证据必须包含有效 URL（http/https）"})
            if not ev.get("evidence_type"):
                issues.append({"field": f"evidence[{i}].evidence_type", "message": "证据类型必填"})
            if not ev.get("title") and not ev.get("claim"):
                issues.append({"field": f"evidence[{i}].title", "message": "证据标题必填"})

        # Duplicate company (C6.1 Gate 0-3: config-driven 4-level match)
        dup_warning = await self._validate_duplicate_with_match(db, data)
        if dup_warning:
            warnings.append(dup_warning)

        # Data quality score (6-dimension)
        dq = self._data_quality(data)
        threshold = self.config.get("validation", {}).get("data_quality_threshold", 0.5)
        overall = dq.get("overall_confidence", 0.0)
        if overall < threshold:
            warnings.append({"type": "low_data_quality", "score": overall,
                             "message": f"综合置信度 {overall:.0%}，低于建议阈值 {threshold:.0%}"})

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "data_quality": dq,
            "missing_evidence": self._missing_evidence(data),
        }

    # ───────────────────────── Activation ─────────────────────────────

    async def activate(self, db: AsyncSession, session: OnboardingSession) -> Dict:
        """Run the full lifecycle pipeline. Idempotent: never duplicates nodes."""
        if session.session_status == "completed" and session.activation_result_json:
            return session.activation_result_json

        # If a previous failed run left a partial node, resume safely.
        session.session_status = "activating"
        session.retry_count = (session.retry_count or 0) + 1
        await db.commit()

        data = session.data_json or {}
        lifecycle: Dict[str, Any] = {}
        node_id = None
        node_type = "company"

        # 1. Observation record (always first, idempotent by session)
        try:
            await self._record_observation(db, session, data)
            lifecycle["observation"] = {"status": "completed"}
        except Exception as e:
            lifecycle["observation"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 2. Create or match Company
        try:
            company = await self._create_company(db, session, data)
            node_id = str(company.id)
            # C6.2: if the activating user exists, bind node_owner membership.
            if session.user_id:
                try:
                    from app.services.governance import get_governance_service
                    await get_governance_service().add_membership(
                        db, session.user_id, node_id, "node_owner",
                        node_type="company", created_by=session.user_id, accepted=True)
                except Exception:
                    pass
            lifecycle["identity"] = {"status": "completed", "node_id": node_id}
        except Exception as e:
            lifecycle["identity"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 3. IdentityProfile
        try:
            await self._create_identity(db, company, data)
            lifecycle["identity_profile"] = {"status": "completed"}
        except Exception as e:
            lifecycle["identity_profile"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 4. Capabilities
        try:
            caps = await self._create_capabilities(db, company, data)
            lifecycle["capability"] = {"status": "completed", "count": len(caps)}
        except Exception as e:
            lifecycle["capability"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 5. Evidence
        try:
            evs = await self._create_evidence(db, company, data)
            lifecycle["evidence"] = {"status": "completed", "count": len(evs)}
        except Exception as e:
            lifecycle["evidence"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 6. Context + Position (reuse existing engines)
        ctx = None
        try:
            from app.universe.context_engine import get_context_engine
            extra = {
                "name": company.name,
                "description": getattr(company, "description", "") or data.get("description", ""),
                "industry_id": str(company.industry_id) if company.industry_id else "",
                "geo_score": getattr(company, "geo_score", 0) or 0,
                "trust_score": 0,
                "evidence_count": len(evs),
                "capability_count": len(caps),
                "relationship_count": 0,
                "certification_count": 0,
            }
            ctx = get_context_engine().understand(node_id, node_type, extra)
            lifecycle["position"] = {"status": "completed",
                                     "position": ctx.current_position.get("position", {})}
        except Exception as e:
            lifecycle["position"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 7. Reputation (memory engine events + DB reputation row)
        try:
            rep = await self._compute_reputation(db, company, data)
            lifecycle["reputation"] = {"status": "completed", "profile": rep}
        except Exception as e:
            lifecycle["reputation"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 8. Possibility graph
        possibility = None
        try:
            from app.universe.possibility_engine import get_possibility_engine
            graph = get_possibility_engine().project(ctx)
            possibility = {
                "states": len(graph.states),
                "horizons": sorted({s.horizon_days for s in graph.states.values() if s.horizon_days > 0}),
                "connection_needs": len(graph.get_all_required_connections()),
            }
            lifecycle["possibility"] = {"status": "completed", **possibility}
        except Exception as e:
            lifecycle["possibility"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 9. Connection candidates
        connections = None
        try:
            from app.universe.connection_engine import get_connection_engine
            report = get_connection_engine().discover_connections(node_id, node_type)
            connections = {
                "candidates": len(report.candidates),
                "top_alignment": round(sorted(report.candidates, key=lambda x: x.future_alignment_score, reverse=True)[0].future_alignment_score, 2) if report.candidates else 0,
            }
            lifecycle["connection"] = {"status": "completed", **connections}
        except Exception as e:
            lifecycle["connection"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 10. Memory (facts from goals)
        try:
            await self._write_memory(company, data)
            lifecycle["memory"] = {"status": "completed"}
        except Exception as e:
            lifecycle["memory"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        # 11. GrowthStage + NodeSnapshot
        try:
            await self._write_stage_and_snapshot(db, company, ctx, rep, caps, evs)
            lifecycle["snapshot"] = {"status": "completed"}
        except Exception as e:
            lifecycle["snapshot"] = {"status": "failed", "reason": str(e)}
            return await self._fail(db, session, lifecycle, str(e))

        result = {
            "session_id": str(session.id),
            "node_id": node_id,
            "node_type": node_type,
            "activation_status": "completed",
            "lifecycle": lifecycle,
            "data_quality": self._data_quality(data),
            "missing_evidence": self._missing_evidence(data),
            "warnings": [w for w in (await self.validate(db, session))["warnings"]],
            "home_url": f"/universe/home?node_type=company&node_id={node_id}",
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
        session.session_status = "completed"
        session.activation_result_json = result
        session.error_message = None
        await db.commit()
        return result

    # ───────────────────────── Pipeline steps ─────────────────────────

    async def _record_observation(self, db, session, data):
        ev = GeoEvent(
            event_type="node_onboarding",
            title=f"节点入驻：{data.get('company_name', session.company_name or '新企业')}",
            description="用户通过 /universe/join 提交企业资料，进入 Universe 激活流程",
            source_node_type="session",
            impact_level="medium",
            impact_score=1.0,
            event_data={"session_id": str(session.id), "idempotency_key": session.idempotency_key},
            source_agent="onboarding_service",
        )
        db.add(ev)
        await db.commit()

    async def _create_company(self, db, session, data) -> Company:
        """Create company or return existing one (idempotent)."""
        name = (data.get("company_name") or "").strip()
        existing = (await db.execute(
            select(Company).where(func.lower(Company.name) == name.lower())
        )).scalars().first()
        if existing:
            return existing
        company = Company(
            name=name,
            description=data.get("description", ""),
            website=data.get("website") or None,
            company_size=data.get("company_size") or None,
            industry_id=uuid.UUID(data["industry_id"]) if data.get("industry_id") else None,
            contact_email=data.get("contact_email") or None,
            founded_year=data.get("founded_year"),
            headquarters=data.get("region") or None,
            business_scope="; ".join(
                [p.get("name", "") for p in (data.get("products") or []) if p.get("name")]
            ) or None,
            entity_type="company",
            geo_id=f"GEO-COMP-{uuid.uuid4().hex[:8].upper()}",
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    async def _create_identity(self, db, company: Company, data):
        existing = (await db.execute(
            select(IdentityProfile).where(
                IdentityProfile.entity_id == company.id,
                IdentityProfile.is_primary == True,
            )
        )).scalars().first()
        if existing:
            return existing
        profile = IdentityProfile(
            entity_id=company.id,
            identity_type="企业",
            display_name=company.name,
            tagline=data.get("self_positioning") or data.get("description", "")[:100] or None,
            industry_context=data.get("track") or data.get("sub_industry"),
            capability_profile={
                "capabilities": [p.get("core_capability", "") for p in (data.get("products") or [])],
            },
            growth_stage="Entry",
            evidence_count=0,
            certification_count=0,
            relationship_count=0,
            is_primary=True,
        )
        db.add(profile)
        await db.commit()

    async def _create_capabilities(self, db, company: Company, data) -> List[Capability]:
        caps = []
        for i, p in enumerate(data.get("products") or []):
            cap_name = p.get("core_capability") or p.get("name")
            if not cap_name:
                continue
            existing = (await db.execute(
                select(Capability).where(
                    Capability.company_id == company.id,
                    Capability.name == cap_name,
                )
            )).scalars().first()
            if existing:
                caps.append(existing)
                continue
            cap = Capability(
                company_id=company.id,
                name=cap_name,
                level=1,
                description=p.get("problem_solved") or p.get("differentiator") or None,
                category=p.get("product_type") or "service",
                evidence_ids=[],
            )
            db.add(cap)
            caps.append(cap)
        await db.commit()
        for c in caps:
            await db.refresh(c)
        return caps

    async def _create_evidence(self, db, company: Company, data) -> List[Evidence]:
        evs = []
        conf_map = self.config.get("evidence_confidence", {})
        for item in data.get("evidence_items") or []:
            ev_type = item.get("evidence_type", "other")
            claim = item.get("title") or item.get("claim") or ""
            existing = (await db.execute(
                select(Evidence).where(
                    Evidence.entity_id == company.id,
                    Evidence.claim == claim,
                    Evidence.source_url == (item.get("source_url") or ""),
                )
            )).scalars().first()
            if existing:
                evs.append(existing)
                continue
            ev = Evidence(
                entity_type="company",
                entity_id=company.id,
                claim=claim,
                source_url=item.get("source_url") or "",
                source_name=item.get("source_name"),
                source_description=item.get("source_description"),
                occurred_at=item.get("occurred_at"),
                confidence_level=item.get("confidence_level") or conf_map.get(ev_type, 0.3),
                source_type=ev_type,
                verified=False,  # self-reported is never auto-verified
            )
            db.add(ev)
            evs.append(ev)
        await db.commit()
        for e in evs:
            await db.refresh(e)
        return evs

    async def _compute_reputation(self, db, company: Company, data) -> Dict:
        """Seed reputation events (memory engine) and write DB reputation row."""
        from app.universe.reputation_engine import get_reputation_engine
        re = get_reputation_engine()
        node_id = str(company.id)

        # C6.5-R fact boundary: ONLY verified evidence may raise reputation.
        # observed/pending/synthetic/self_report never do.
        for item in (data.get("evidence_items") or [])[:8]:
            if item.get("truth_status") != "verified":
                continue
            ev_type = item.get("evidence_type", "other")
            desc = item.get("title") or item.get("claim") or ""
            mapped_type = {
                "official_website": "ai_search_indexed",
                "media_report": "industry_citation",
                "customer_case": "customer_success",
                "award_certification": "certification_passed",
                "partner_org": "relationship_established",
                "expert_endorsement": "peer_endorsement",
                "data_result": "innovation_release",
                "ai_citation": "ai_agent_cited",
            }.get(ev_type, "capability_verified")
            re.record_event(node_id, "company", mapped_type, desc, "association")

        snap = re.recalculate(node_id, "company")

        # Persist to DB Reputation table
        rep = (await db.execute(
            select(Reputation).where(Reputation.node_id == company.id)
        )).scalars().first()
        if not rep:
            rep = Reputation(node_id=company.id, node_type="company")
        rep.total_score = snap.overall_score
        rep.reputation_level = snap.overall_level or "N/A"
        rep.evidence_count = len(data.get("evidence_items") or [])
        rep.case_count = sum(1 for i in (data.get("evidence_items") or []) if i.get("evidence_type") == "customer_case")
        rep.dimension_breakdown = {k: v.to_dict() for k, v in snap.dimensions.items()}
        rep.last_evaluated_at = datetime.now(timezone.utc)
        db.add(rep)
        await db.commit()

        return {
            "status": snap.status,
            "overall_score": snap.overall_score,
            "overall_level": snap.overall_level,
            "trend": snap.trend,
        }

    async def _write_memory(self, company: Company, data):
        from app.universe.memory_engine import get_memory_engine
        mem = get_memory_engine()
        node_id = str(company.id)
        node_type = "company"
        if data.get("key_problem"):
            mem.record_fact(node_id, node_type, f"核心问题：{data['key_problem']}", "goal", "onboarding")
        for key, label in [("goal_30d", "未来30天目标"), ("goal_90d", "未来90天目标"), ("goal_180d", "未来180天目标")]:
            if data.get(key):
                mem.record_fact(node_id, node_type, f"{label}：{data[key]}", "goal", "onboarding")
        if data.get("connection_wants"):
            mem.record_fact(node_id, node_type, f"希望连接：{data['connection_wants']}", "relationship", "onboarding")
        if data.get("risk_to_avoid"):
            mem.record_fact(node_id, node_type, f"希望避免：{data['risk_to_avoid']}", "risk", "onboarding")

    async def _write_stage_and_snapshot(self, db, company, ctx, rep, caps, evs):
        stage = ctx.current_position.get("position", {}).get("growth_stage", "Entry")
        gs = (await db.execute(
            select(GrowthStage).where(GrowthStage.node_id == company.id)
        )).scalars().first()
        if not gs:
            gs = GrowthStage(node_id=company.id, node_type="company")
        gs.current_stage = stage
        gs.stage_level = 1
        gs.stage_progress = ctx.current_position.get("inputs", {}).get("evidence_count", 0) / 10.0
        gs.missing_capabilities = [c.get("cap_id", "") for c in ctx.capability_state.get("available", [])[:5]]
        gs.recommended_actions = ctx.recommended_direction.get("detailed", [])[:3]
        db.add(gs)

        snap = NodeSnapshot(
            entity_id=company.id,
            snapshot_date=date.today(),
            snapshot_type="event",
            trigger_event="node_onboarding",
            growth_stage=stage,
            geo_score=getattr(company, "geo_score", 0) or 0,
            visibility_score=0,
            trust_score=rep.get("overall_score", 0),
            capability_score=len(caps),
            evidence_count=len(evs),
            certification_count=0,
            relationship_count=0,
            competitor_count=0,
            position_json=ctx.current_position,
            capability_json={"count": len(caps)},
            reputation_json=rep,
            change_summary="节点入驻 Universe，完成首次身份、位置、信誉与未来分析",
            is_significant=True,
        )
        db.add(snap)
        await db.commit()

    # ───────────────────────── Helpers ─────────────────────────

    async def _fail(self, db, session, lifecycle, error: str) -> Dict:
        session.session_status = "failed"
        session.error_message = error
        session.activation_result_json = {"activation_status": "failed", "lifecycle": lifecycle, "error": error}
        await db.commit()
        return session.activation_result_json

    async def _find_duplicate_company(self, db, name: str):
        if not name:
            return None
        return (await db.execute(
            select(Company).where(func.lower(Company.name) == name.lower())
        )).scalars().first()

    # ── C6.1 Gate 0-3: config-driven node matching ──

    @staticmethod
    def _normalize_domain(url: str) -> str:
        if not url:
            return ""
        u = url.strip().lower()
        u = u.replace("http://", "").replace("https://", "").replace("www.", "")
        return u.split("/")[0].split("?")[0]

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not name:
            return ""
        for suffix in ("有限公司", "有限责任公司", "股份有限公司", "科技", "集团", "股份", "公司"):
            name = name.replace(suffix, "")
        return re.sub(r"[\s（）()·.-]", "", name).lower()

    async def match_existing_node(self, db, data: Dict) -> Dict:
        """C6.1 Gate 0-3: match a candidate company against existing nodes.

        Returns one of: exact_match | probable_match | possible_duplicate | new_node
        Weights and fields come from config (learning.yaml or onboarding.yaml).
        """
        cfg = self.config.get("deduplication") or {}
        # C6.1 Gate 0-3: dedup rules live in learning.yaml (authoritative).
        try:
            import os as _os2, yaml as _yaml2
            _p2 = _os2.path.join(_os2.path.dirname(_os2.path.dirname(_os2.path.dirname(_os2.path.dirname(_os2.path.abspath(__file__))))),
                                  'config', 'universe', 'learning.yaml')
            if _os2.path.exists(_p2):
                _lcfg = _yaml2.safe_load(open(_p2, encoding='utf-8')) or {}
                cfg = _lcfg.get('deduplication', {}) or cfg
        except Exception:
            pass
        fields = cfg.get("match_fields", [])
        if not fields:
            fields = [
                {"key": "credit_code", "weight": 1.0, "exact": True},
                {"key": "website", "weight": 0.9, "normalize": "domain"},
                {"key": "company_name", "weight": 0.8, "normalize": "name"},
                {"key": "contact_email", "weight": 0.5},
            ]

        companies = (await db.execute(
            select(Company).order_by(Company.created_at)
        )).scalars().all()

        best = None
        best_score = 0.0
        for company in companies:
            score = 0.0
            matched_fields = []
            for fd in fields:
                key = fd.get("key")
                weight = fd.get("weight", 0.5)
                exact = fd.get("exact", False)
                norm = fd.get("normalize", "")
                candidate_val = data.get(key)
                if not candidate_val and key == "website":
                    candidate_val = data.get("website")
                if not candidate_val and key == "company_name":
                    candidate_val = data.get("company_name")
                if not candidate_val and key == "region_name":
                    candidate_val = data.get("region")
                if not candidate_val:
                    continue
                company_val = None
                if key == "company_name":
                    company_val = company.name
                elif key == "website":
                    company_val = getattr(company, "website", None)
                elif key == "contact_email":
                    company_val = getattr(company, "contact_email", None)
                elif key == "region_name":
                    company_val = getattr(company, "headquarters", None) or getattr(company, "region", None)
                elif key == "credit_code":
                    company_val = None  # not stored on Company today; exact external ids may live in ext metadata
                if not company_val:
                    continue
                if norm == "domain":
                    match = self._normalize_domain(candidate_val) == self._normalize_domain(company_val)
                elif norm == "name":
                    match = self._normalize_name(candidate_val) == self._normalize_name(company_val)
                else:
                    match = str(candidate_val).strip().lower() == str(company_val).strip().lower()
                if match:
                    score += weight
                    matched_fields.append(key)
            if score > best_score:
                best_score = score
                best = company

        levels = cfg.get("match_levels", [])
        level_id = "new_node"
        for lv in sorted(levels, key=lambda x: x.get("min_score", 0), reverse=True):
            if best_score >= lv.get("min_score", 0):
                level_id = lv["id"]
                break

        return {
            "match_level": level_id,
            "matched_node_id": str(best.id) if best else None,
            "matched_name": best.name if best else None,
            "match_score": round(best_score, 2),
            "matched_fields": [] if not best else self._last_matched_fields,
        }

    _last_matched_fields = []

    async def _validate_duplicate_with_match(self, db, data: Dict) -> Dict:
        """Validation helper returning duplicate warnings from match result."""
        match = await self.match_existing_node(db, data)
        if match["match_level"] in ("exact_match", "probable_match"):
            return {
                "type": "duplicate_company",
                "match_level": match["match_level"],
                "node_id": match["matched_node_id"],
                "message": f"企业「{data.get('company_name')}」匹配到已有节点（{match['match_level']}）",
            }
        if match["match_level"] == "possible_duplicate":
            return {
                "type": "possible_duplicate",
                "match_level": match["match_level"],
                "node_id": match["matched_node_id"],
                "message": f"企业「{data.get('company_name')}」可能是已有节点的重复（{match['match_level']}），需人工确认",
            }
        return None

    def _data_quality(self, data: Dict) -> Dict:
        """C6.1 Gate 0-1: six-dimension data quality, weighted and configurable.

        profile_completeness measures form completeness; evidence dimensions
        measure what is actually verifiable. A fully filled self-reported form
        cannot reach overall_confidence 1.0.
        """
        weights = self.config.get("data_quality_weights", {})
        w = lambda k: weights.get(k, 0.0)

        # 1. profile_completeness: form fields filled
        profile_fields = ["company_name", "description", "industry_id", "products", "goal_30d", "goal_90d", "goal_180d"]
        filled = sum(1 for f in profile_fields if data.get(f) or (f == "products" and data.get("products")))
        profile_completeness = round(filled / len(profile_fields), 2)

        # 2. evidence_coverage: preferred evidence types present
        ev = data.get("evidence_items") or []
        ev_types = {e.get("evidence_type") for e in ev}
        preferred = ["official_website", "customer_case", "media_report", "award_certification"]
        coverage = round(len(ev_types & set(preferred)) / len(preferred), 2)

        # 3. evidence_verification: verified share (self_report never counts as verified)
        ver_weights = self.config.get("evidence_verification_weights", {})
        if ev:
            total = sum(ver_weights.get(e.get("verification_status", "self_report"), 0.1) for e in ev)
            evidence_verification = round(min(total / len(ev), 1.0), 2)
        else:
            evidence_verification = 0.0

        # 4. source_diversity: distinct source names / types
        sources = {e.get("source_name") or e.get("source_type") for e in ev if e.get("source_name") or e.get("source_type")}
        source_diversity = round(min(len(sources) / 3.0, 1.0), 2)

        # 5. freshness: recent evidence (occurred_at within 365 days, or unknown)
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        recent = 0
        for e in ev:
            oc = e.get("occurred_at")
            if not oc:
                recent += 0.5
            else:
                try:
                    d = datetime.fromisoformat(str(oc).replace("Z", "+00:00"))
                    if (now - d).days <= 365:
                        recent += 1.0
                except Exception:
                    recent += 0.5
        freshness = round(recent / len(ev), 2) if ev else 0.0

        # 6. overall_confidence: weighted composite of the above (never 1.0 when all self_report)
        overall = round(
            profile_completeness * w("profile_completeness") +
            coverage * w("evidence_coverage") +
            evidence_verification * w("evidence_verification") +
            source_diversity * w("source_diversity") +
            freshness * w("freshness"),
            2,
        )
        # The overall_confidence weight is folded into the composite via normalized weights.
        # Normalize so configured weights sum to 1.0; if they don't, use raw ratio.
        total_w = sum(weights.values()) or 1.0
        overall = round(overall / total_w, 2)

        return {
            "profile_completeness": profile_completeness,
            "evidence_coverage": coverage,
            "evidence_verification": evidence_verification,
            "source_diversity": source_diversity,
            "freshness": freshness,
            "overall_confidence": overall,
        }

    def _missing_evidence(self, data: Dict) -> List[str]:
        missing = []
        if not data.get("evidence_items"):
            return ["官网页面", "客户案例", "媒体报道"]
        types = {e.get("evidence_type") for e in data["evidence_items"]}
        preferred = ["official_website", "customer_case", "media_report"]
        for t in preferred:
            if t not in types:
                missing.append(t)
        return missing

    async def get_status(self, db, session) -> Dict:
        if session.activation_result_json:
            return session.activation_result_json
        return {
            "session_id": str(session.id),
            "session_status": session.session_status,
            "current_step": session.current_step,
            "activation_status": "pending",
            "error": session.error_message,
        }
