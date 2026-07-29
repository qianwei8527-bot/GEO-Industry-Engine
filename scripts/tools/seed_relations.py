"""Sprint 2.1: 补全种子数据关联 + 修复User schema + 验证全链路"""
import asyncio, sys, uuid
sys.path.insert(0, r"D:\GEO-Industry-Engine\backend")
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.config import settings

async def seed_relations():
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as db:
        # Get existing companies
        result = await db.execute(text("SELECT id, name, geo_id FROM companies"))
        companies = [(r[0], r[1], r[2]) for r in result.fetchall()]
        print(f"Found {len(companies)} companies")

        # Get industries
        result = await db.execute(text("SELECT id, code, name FROM industries"))
        industries = [(r[0], r[1], r[2]) for r in result.fetchall()]
        print(f"Found {len(industries)} industries")

        c1_id = str(companies[0][0])
        c2_id = str(companies[1][0])
        c3_id = str(companies[2][0])

        # 1. Add Capabilities
        caps = [
            (c1_id, "AI内容生成", "基于大模型的智能内容创作能力", "content", 4),
            (c1_id, "GEO战略咨询", "AI搜索引擎优化策略咨询", "strategy", 3),
            (c2_id, "AI算力基础设施", "大规模AI训练推理算力服务", "infrastructure", 5),
            (c2_id, "模型服务平台", "企业级AI模型部署与运维", "platform", 4),
            (c3_id, "AI个性化学习", "基于AI的自适应学习系统", "education", 3),
            (c3_id, "教育数据分析", "学习行为分析与预测", "data", 3),
        ]
        for cid, name, desc, cat, lvl in caps:
            cap_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO capabilities (id, company_id, name, description, category, level, evidence_ids, tenant_id, created_at, updated_at)
                VALUES (:id, :cid, :name, :desc, :cat, :lvl, '[]', NULL, NOW(), NOW())
            """), {"id": cap_id, "cid": cid, "name": name, "desc": desc, "cat": cat, "lvl": lvl})
        print(f"Added {len(caps)} capabilities")

        # 2. Add Evidence
        evs = [
            (c1_id, "公司官网AI服务展示", "https://example.com/ai-services", "official", 0.9, True),
            (c1_id, "第三方客户评价", "https://review.example.com/stars", "third_party", 0.7, True),
            (c2_id, "ISO27001安全认证", "https://cert.example.com/iso", "certification", 1.0, True),
            (c2_id, "客户案例: 某银行AI项目", "https://cases.example.com/bank", "case_study", 0.8, True),
            (c3_id, "教育部AI教育试点批文", "https://gov.example.com/edu-ai", "government", 1.0, True),
            (c3_id, "用户学习效果数据报告", "https://data.example.com/learning", "research", 0.75, False),
        ]
        for eid_type, claim, url, stype, conf, verified in evs:
            ev_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO evidence (id, entity_type, entity_id, claim, source_url, source_type, confidence_level, verified, tenant_id, created_at)
                VALUES (:id, 'company', :eid, :claim, :url, :stype, :conf, :ver, NULL, NOW())
            """), {"id": ev_id, "eid": eid_type, "claim": claim, "url": url, "stype": stype, "conf": conf, "ver": verified})
        print(f"Added {len(evs)} evidence records")

        # 3. Add Events
        evts = [
            (c1_id, "product_launch", "发布AI内容生成引擎v3.0", "2026-06-15", "high", "官方公告"),
            (c1_id, "partnership_formed", "与头部AI搜索平台达成战略合作", "2026-05-20", "high", "新闻稿"),
            (c2_id, "funding_raised", "完成C轮5亿元融资", "2026-04-10", "high", "投资公告"),
            (c2_id, "certification_achieved", "获得GEO基础设施L3认证", "2026-03-01", "high", "认证中心"),
            (c3_id, "product_launch", "AI学习平台2.0上线", "2026-07-01", "medium", "产品发布"),
            (c3_id, "market_entry", "进入东南亚教育市场", "2026-06-01", "medium", "市场报告"),
        ]
        for eid_type, etype, title, edate, impact, source in evts:
            evt_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO events (id, entity_type, entity_id, event_type, title, description, event_date, impact, source, metadata, tenant_id, created_at)
                VALUES (:id, 'company', :eid, :etype, :title, :desc, :edate, :impact, :src, '{}', NULL, NOW())
            """), {"id": evt_id, "eid": eid_type, "etype": etype, "title": title, "desc": title, "edate": edate, "impact": impact, "src": source})
        print(f"Added {len(evts)} events")

        # 4. Add Relationships
        rels = [
            ("company", c1_id, "company", c2_id, "partners_with", 0.8),
            ("company", c2_id, "company", c1_id, "partners_with", 0.8),
            ("company", c1_id, "company", c3_id, "competitor_of", 0.3),
            ("company", c3_id, "company", c1_id, "competitor_of", 0.3),
        ]
        for stype, sid, ttype, tid, rtype, strength in rels:
            rel_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO relationships (id, source_type, source_id, target_type, target_id, relation_type, strength, evidence_ids, metadata, tenant_id, created_at)
                VALUES (:id, :st, :sid, :tt, :tid, :rt, :str, '[]', '{}', NULL, NOW())
            """), {"id": rel_id, "st": stype, "sid": sid, "tt": ttype, "tid": tid, "rt": rtype, "str": strength})
        print(f"Added {len(rels)} relationships")

        # 5. Add Trust scores
        trusts = [
            (c1_id, "company", 72.5, 2, "L2"),
            (c2_id, "company", 88.0, 3, "L3"),
            (c3_id, "company", 65.0, 2, "L1"),
        ]
        for eid, etype, score, evcount, certlev in trusts:
            t_id = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO trust (id, entity_id, entity_type, trust_score, evidence_count, certification_level, last_evaluated_at, tenant_id, created_at, updated_at)
                VALUES (:id, :eid, :etype, :score, :evcount, :certlev, NOW(), NULL, NOW(), NOW())
            """), {"id": t_id, "eid": eid, "etype": etype, "score": score, "evcount": evcount, "certlev": certlev})
        print(f"Added {len(trusts)} trust records")

        await db.commit()
        print("\n=== Seed relations complete ===")

if __name__ == "__main__":
    asyncio.run(seed_relations())
