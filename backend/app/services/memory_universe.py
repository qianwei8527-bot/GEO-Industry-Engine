"""C6.6 Memory Universe — unified world memory for a node.

Answers "what happened, why, who influenced it, how it changed" by fusing
persistent event sources into one timeline, deriving cause chains, and
generating a node life narrative. AI never invents facts: narrative is
built from recorded events only (deterministic template).
"""
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event as EventORM
from app.models.geo_event import GeoEvent
from app.models.reputation_event_record import ReputationEventRecord
from app.models.transaction_record import UniverseTransactionRecord, TransactionEventRecord
from app.models.candidate_change import CandidateChange
from app.models.change_audit import CandidateChangeAudit

print("Phase C6.6: Memory Universe service loaded")

CAUSE_RULES = [
    # (effect_pattern, cause_description)
    ("certification_passed", "获得认证 → 信誉提升"),
    ("customer_success", "客户成功 → 交付信誉提升"),
    ("negative_feedback", "负面反馈 → 信誉下降"),
    ("change_applied", "审核通过的变化被应用 → 节点状态更新"),
    ("collaboration_completed", "合作完成 → 关系信誉提升"),
    ("settled", "交易结算 → 双向信誉与关系反馈"),
    ("node_onboarding", "节点入驻 → 首次认知建立"),
]


class MemoryUniverseService:
    def __init__(self):
        self.cause_rules = CAUSE_RULES

    async def unified_timeline(self, db: AsyncSession, node_id: str, limit: int = 100) -> Dict:
        items = []
        # 1. Event ORM
        for e in (await db.execute(select(EventORM).where(EventORM.entity_id == node_id).limit(limit))).scalars().all():
            items.append({"ts": e.event_date.isoformat() if e.event_date else "", "type": e.event_type,
                          "title": e.title, "description": e.description or "", "source": "event"})
        # 2. GeoEvent
        for g in (await db.execute(select(GeoEvent).where(GeoEvent.source_node_id == node_id).limit(limit))).scalars().all():
            items.append({"ts": g.event_date.isoformat() if g.event_date else "", "type": g.event_type,
                          "title": g.title, "description": g.description or "", "source": "geo_event"})
        # 3. Reputation events (durable)
        for r in (await db.execute(select(ReputationEventRecord).where(ReputationEventRecord.node_id == node_id)
                                   .limit(limit))).scalars().all():
            items.append({"ts": r.timestamp.isoformat() if r.timestamp else "", "type": r.event_type,
                          "title": r.description or r.event_type,
                          "description": f"dimension={r.dimension} impact={r.impact} weight={r.effective_weight}",
                          "source": "reputation_event"})
        # 4. Candidate changes + audit
        for cc in (await db.execute(select(CandidateChange).where(CandidateChange.node_id == node_id).limit(limit))).scalars().all():
            items.append({"ts": cc.created_at.isoformat() if cc.created_at else "", "type": "candidate_change",
                          "title": cc.signal_label or cc.change_type,
                          "description": f"review={cc.review_status}", "source": "candidate_change"})
        # 5. Transactions (node is either party)
        txs = (await db.execute(select(UniverseTransactionRecord).where(
            or_(UniverseTransactionRecord.node_a_id == node_id, UniverseTransactionRecord.node_b_id == node_id)
        ).limit(20))).scalars().all()
        for t in txs:
            for te in (await db.execute(select(TransactionEventRecord).where(
                    TransactionEventRecord.transaction_id == t.transaction_id).limit(20))).scalars().all():
                items.append({"ts": te.timestamp.isoformat() if te.timestamp else "", "type": te.event_type,
                              "title": f"交易 {t.transaction_id[:8]}: {te.event_type}",
                              "description": te.description or "", "source": "transaction_event"})
        # 6. Memory engine (in-memory facts)
        try:
            from app.universe.memory_engine import get_memory_engine
            for f in get_memory_engine().get_facts(node_id)[:20]:
                items.append({"ts": f.timestamp[:10] if f.timestamp else "", "type": "memory_fact",
                              "title": f.statement, "description": f.category, "source": "memory_fact"})
        except Exception:
            pass
        items.sort(key=lambda x: x.get("ts", ""), reverse=True)
        return {"node_id": node_id, "count": len(items), "timeline": items[:limit]}

    async def cause_analysis(self, db: AsyncSession, node_id: str) -> Dict:
        tl = await self.unified_timeline(db, node_id, limit=200)
        chain = []
        for item in tl["timeline"]:
            etype = item.get("type", "")
            for pattern, cause in self.cause_rules:
                if pattern in etype or pattern in item.get("title", ""):
                    chain.append({"event": item.get("title"), "type": etype,
                                  "cause": cause, "source": item.get("source"),
                                  "occurred_at": item.get("ts")})
                    break
        return {"node_id": node_id, "cause_chain": chain[:50], "explained_events": len(chain)}

    async def generate_narrative(self, db: AsyncSession, node_id: str, node_name: str = "") -> Dict:
        tl = await self.unified_timeline(db, node_id, limit=100)
        events = tl["timeline"]
        if not events:
            return {"node_id": node_id, "story": "该节点尚无记录事件，Universe 尚未形成对其生命故事的认知。", "period": None}
        first = events[-1]["ts"][:10] if events else ""
        last = events[0]["ts"][:10] if events else ""
        milestones = [e for e in events if e["type"] in ("certification_passed", "settled", "change_applied",
                                                         "node_onboarding", "collaboration_completed", "trust_established")]
        lines = [f"节点 {node_name or node_id[:8]} 的生命记录从 {first} 至 {last}，共 {len(events)} 条事件。"]
        if milestones:
            lines.append("关键节点：")
            for m in milestones[:5]:
                lines.append(f"- {m['ts'][:10]}：{m['title']}（{m['source']}）")
        lines.append("以上内容完全来自已记录事件，不包含 AI 推断事实。")
        return {"node_id": node_id, "story": "\n".join(lines), "period": {"from": first, "to": last},
                "event_count": len(events)}
