import asyncio, sys, uuid
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

        # Capabilities
        caps = [
            (c1, "AI内容生成", "基于大模型的智能内容创作能力", "content", 4),
            (c1, "GEO战略咨询", "AI搜索引擎优化策略咨询", "strategy", 3),
            (c2, "AI算力基础设施", "大规模AI训练推理算力服务", "infrastructure", 5),
            (c2, "模型服务平台", "企业级AI模型部署与运维", "platform", 4),
            (c3, "AI个性化学习", "基于AI的自适应学习系统", "education", 3),
            (c3, "教育数据分析", "学习行为分析与预测", "data", 3),
        ]
        for cid, name, desc, cat, lvl in caps:
            cap_id = str(uuid.uuid4())
            sql = text(
                "INSERT INTO capabilities (id, company_id, name, description, category, level, evidence_ids, tenant_id, created_at, updated_at) "
                "VALUES (:id, :cid, :name, :desc, :cat, :lvl, '[]', NULL, NOW(), NOW())"
            )
            await db.execute(sql, {"id": cap_id, "cid": cid, "name": name, "desc": desc, "cat": cat, "lvl": lvl})
        print("Added " + str(len(caps)) + " capabilities")

        # Evidence
        evs = [
            (c1, "公司官网AI服务展示", "https://example.com/ai-services", "official", 0.9, True),
            (c1, "第三方客户评价", "https://review.example.com/stars", "third_party", 0.7, True),
            (c2, "ISO27001安全认证", "https://cert.example.com/iso", "certification", 1.0, True),
            (c2, "客户案例: 某银行AI项目", "https://cases.example.com/bank", "case_study", 0.8, True),
            (c3, "教育部AI教育试点批文", "https://gov.example.com/edu-ai", "government", 1.0, True),
            (c3, "用户学习效果数据报告", "https://data.example.com/learning", "research", 0.75, False),
        ]
        for eid, claim, url, stype, conf, verified in evs:
            ev_id = str(uuid.uuid4())
            sql = text(
                "INSERT INTO evidence (id, entity_type, entity_id, claim, source_url, source_type, confidence_level, verified, tenant_id, created_at) "
                "VALUES (:id, 'company', :eid, :claim, :url, :stype, :conf, :ver, NULL, NOW())"
            )
            await db.execute(sql, {"id": ev_id, "eid": eid, "claim": claim, "url": url, "stype": stype, "conf": conf, "ver": verified})
        print("Added " + str(len(evs)) + " evidence records")

        await db.commit()
        print("Seed complete!")

asyncio.run(seed())
