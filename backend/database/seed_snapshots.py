"""Seed demo snapshots for the first living node.
Creates 4 snapshots for the demo company showing a growth trajectory:
Snapshot 1: Entry (born) → geo_score 40
Snapshot 2: Active (certification added) → geo_score 51
Snapshot 3: Active (evidence growing) → geo_score 59
Snapshot 4: Established (milestone) → geo_score 68
"""

import asyncio, uuid, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from datetime import date, timedelta
from sqlalchemy import select
from app.database import _get_session_factory
from app.models.company import Company
from app.models.node_snapshot import NodeSnapshot

SNAPSHOTS = [
    {"days_ago": 90, "geo": 40, "trust": 42, "vis": 35, "cap": 45, "stage": "Entry",
     "evidence": 2, "certs": 0, "rels": 1, "comps": 3,
     "type": "manual", "trigger": "企业首次进入 GEO Universe", "summary": "初始状态——刚刚注册，基础信息已录入"},
    {"days_ago": 60, "geo": 51, "trust": 55, "vis": 48, "cap": 52, "stage": "Active",
     "evidence": 4, "certs": 1, "rels": 2, "comps": 3,
     "type": "event", "trigger": "获得行业认证——GEO服务能力认证", "summary": "获得行业认证，Trust 和 GEO 评分开始上升", "significant": True},
    {"days_ago": 30, "geo": 59, "trust": 62, "vis": 55, "cap": 58, "stage": "Active",
     "evidence": 7, "certs": 1, "rels": 3, "comps": 4,
     "type": "event", "trigger": "新增3条Evidence + 1个合作伙伴", "summary": "证据库持续增长，合作关系扩展，评分稳步提升"},
    {"days_ago": 2, "geo": 68, "trust": 70, "vis": 65, "cap": 72, "stage": "Established",
     "evidence": 10, "certs": 2, "rels": 5, "comps": 4,
     "type": "event", "trigger": "进入 Established 阶段 + 获得第2个认证", "summary": "跨越关键门槛——正式进入 Established 阶段，生态位置确立",
     "significant": True},
]

async def seed():
    factory = _get_session_factory()
    async with factory() as db:
        companies = (await db.execute(select(Company).limit(1))).scalars().all()
        if not companies:
            print("No companies found — seed companies first")
            return

        company = companies[0]
        print(f"Seeding snapshots for: {company.name} ({company.id})")

        # Delete existing snapshots
        from sqlalchemy import delete
        await db.execute(delete(NodeSnapshot).where(NodeSnapshot.entity_id == company.id))

        today = date.today()
        snapshots = []
        for s in SNAPSHOTS:
            snap = NodeSnapshot(
                entity_id=company.id,
                snapshot_date=today - timedelta(days=s["days_ago"]),
                snapshot_type=s["type"],
                trigger_event=s["trigger"],
                growth_stage=s["stage"],
                geo_score=s["geo"],
                trust_score=s["trust"],
                visibility_score=s["vis"],
                capability_score=s["cap"],
                evidence_count=s["evidence"],
                certification_count=s["certs"],
                relationship_count=s["rels"],
                competitor_count=s["comps"],
                change_summary=s["summary"],
                is_significant=s.get("significant", False),
            )
            snapshots.append(snap)
            db.add(snap)

        await db.commit()
        print(f"Seeded {len(snapshots)} snapshots for {company.name}")
        
        # Also create an IdentityProfile
        from app.models.identity_profile import IdentityProfile
        existing = (await db.execute(
            select(IdentityProfile).where(
                IdentityProfile.entity_id == company.id,
                IdentityProfile.is_primary == True
            )
        )).scalars().first()
        
        if not existing:
            profile = IdentityProfile(
                entity_id=company.id,
                identity_type="企业",
                display_name=company.name,
                industry_context="GEO服务 / AI营销",
                growth_stage="Established",
                reputation_level="A",
                geo_score=68,
                visibility_score=65,
                trust_score=70,
                capability_score=72,
                evidence_count=10,
                certification_count=2,
                relationship_count=5,
            )
            db.add(profile)
            await db.commit()
            print(f"Created IdentityProfile for {company.name}")

        print("Seed complete!")

if __name__ == "__main__":
    asyncio.run(seed())
