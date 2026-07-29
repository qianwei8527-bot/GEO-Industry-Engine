import asyncio, sys, uuid
from datetime import date
sys.path.insert(0, r"D:\GEO-Industry-Engine\backend")
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.config import settings

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as db:
        result = await db.execute(text("SELECT id FROM companies"))
        cids = [str(r[0]) for r in result.fetchall()]
        c1, c2, c3 = cids[0], cids[1], cids[2]

        # Events
        evts = [
            (c1, "product_launch", "发布AI内容生成引擎v3.0", date(2026,6,15), "high", "官方公告"),
            (c1, "partnership_formed", "与头部AI搜索平台达成战略合作", date(2026,5,20), "high", "新闻稿"),
            (c2, "funding_raised", "完成C轮5亿元融资", date(2026,4,10), "high", "投资公告"),
            (c2, "certification_achieved", "获得GEO基础设施L3认证", date(2026,3,1), "high", "认证中心"),
            (c3, "product_launch", "AI学习平台2.0上线", date(2026,7,1), "medium", "产品发布"),
            (c3, "market_entry", "进入东南亚教育市场", date(2026,6,1), "medium", "市场报告"),
        ]
        for eid, etype, title, edate, impact, src in evts:
            evt_id = str(uuid.uuid4())
            sql = text(
                "INSERT INTO events (id, entity_type, entity_id, event_type, title, description, event_date, impact, source, metadata, tenant_id, created_at) "
                "VALUES (:id, 'company', :eid, :etype, :title, :desc, :edate, :impact, :src, '{}', NULL, NOW())"
            )
            await db.execute(sql, {"id": evt_id, "eid": eid, "etype": etype, "title": title, "desc": title, "edate": edate, "impact": impact, "src": src})
        print("Added " + str(len(evts)) + " events")

        # Relationships
        rels = [
            ("company", c1, "company", c2, "partners_with", 0.8),
            ("company", c2, "company", c1, "partners_with", 0.7),
            ("company", c1, "company", c3, "competitor_of", 0.3),
        ]
        for st, sid, tt, tid, rt, strength in rels:
            sql = text(
                "INSERT INTO relationships (id, source_type, source_id, target_type, target_id, relation_type, strength, evidence_ids, metadata, tenant_id, created_at) "
                "VALUES (:id, :st, :sid, :tt, :tid, :rt, :str, '[]', '{}', NULL, NOW())"
            )
            await db.execute(sql, {"id": str(uuid.uuid4()), "st": st, "sid": sid, "tt": tt, "tid": tid, "rt": rt, "str": strength})
        print("Added " + str(len(rels)) + " relationships")

        # Trust
        trusts = [(c1, 72.5, 2, "L2"), (c2, 88.0, 3, "L3"), (c3, 65.0, 2, "L1")]
        for eid, score, evcount, certlev in trusts:
            sql = text(
                "INSERT INTO trust (id, entity_id, entity_type, trust_score, evidence_count, certification_level, last_evaluated_at, tenant_id, created_at, updated_at) "
                "VALUES (:id, :eid, 'company', :score, :evcount, :certlev, NOW(), NULL, NOW(), NOW())"
            )
            await db.execute(sql, {"id": str(uuid.uuid4()), "eid": eid, "score": score, "evcount": evcount, "certlev": certlev})
        print("Added " + str(len(trusts)) + " trust records")

        await db.commit()
        print("Relations seed complete!")

asyncio.run(seed())
