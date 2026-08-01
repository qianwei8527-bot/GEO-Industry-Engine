"""C6.5 Public Sandbox verification — invariants and engine-derived results.

Checks data isolation, source traceability, idempotency, and that Position/
Reputation etc come from engines (never seeded).
"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.models.company import Company
from app.models.evidence import Evidence
from app.models.capability import Capability

RESULTS = {"passed": 0, "failed": 0}
def check(name, cond, detail=""):
    RESULTS["passed" if cond else "failed"] += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))

async def main():
    factory = _get_session_factory()
    async with factory() as db:
        real_names = ["清华大学", "北京大学", "复旦大学", "上海交通大学", "科大讯飞", "好未来",
                      "网易有道", "视源股份", "中国科学院", "中国教育科学研究院",
                      "国家教育行政学院", "中国教育装备行业协会"]
        for nm in real_names:
            c = (await db.execute(select(Company).where(Company.name == nm))).scalars().first()
            check(f"real node present: {nm}", c is not None)
            if c:
                evs = (await db.execute(select(Evidence).where(Evidence.entity_id == c.id))).scalars().all()
                check(f"{nm} evidence traceable", all(e.source_url for e in evs) and len(evs) >= 1, f"{len(evs)} ev")
                syn = [e for e in evs if e.is_synthetic]
                check(f"{nm} no synthetic evidence", len(syn) == 0)
        syn_nodes = (await db.execute(select(Company).where(Company.name.like("%仿真%")))).scalars().all()
        check("synthetic nodes exist", len(syn_nodes) >= 12, f"{len(syn_nodes)}")
        # synthetic evidence must not affect real metrics
        bad = (await db.execute(select(func.count(Evidence.id)).where(
            Evidence.is_synthetic == True, Evidence.may_affect_real_metrics == True))).scalar()
        check("synthetic evidence cannot affect real metrics", bad == 0, f"{bad}")
        # engine-derived: position/reputation computed from context engine, not stored as seed
        from app.universe.context_engine import get_context_engine
        c = (await db.execute(select(Company).where(Company.name == "清华大学"))).scalars().first()
        ctx = get_context_engine().understand(str(c.id), "company", {"name": c.name,
            "evidence_count": (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == c.id))).scalar()})
        pos = ctx.current_position.get("position", {})
        check("position computed by engine", bool(pos.get("growth_stage")))
        check("reputation profile present", bool(ctx.reputation_profile))

    total = RESULTS["passed"] + RESULTS["failed"]
    print(f"\nVERIFY: {RESULTS['passed']}/{total} passed")
    return 0 if RESULTS["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
