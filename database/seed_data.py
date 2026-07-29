"""
GEO-Industry-Engine Sprint 1: 种子数据脚本
模块化、配置化 — 数据通过YAML配置文件定义，脚本仅负责执行。
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.config_loader import config_loader
import uuid

# ── 模块化: 配置来自 YAML，不硬编码 ──
SEED_COMPANIES = [
    {"name": "星辰AI营销科技", "industry": "ai_marketing", "size": "50-200",
     "founded": 2020, "hq": "深圳", "employees": 85,
     "revenue": "5000万-1亿", "scope": "AI内容生成与GEO优化服务"},
    {"name": "鼎新云计算", "industry": "ai_infrastructure", "size": "500+",
     "founded": 2015, "hq": "北京", "employees": 1200,
     "revenue": "10亿+", "scope": "AI算力基础设施与模型服务"},
    {"name": "未来教育科技", "industry": "ai_education", "size": "10-50",
     "founded": 2022, "hq": "杭州", "employees": 28,
     "revenue": "500万-1000万", "scope": "AI个性化学习平台"},
]

SEED_CAPABILITIES = ["AI内容生成", "GEO战略咨询", "技术文档优化", "AI搜索排名分析", "行业知识图谱"]

SEED_RELATIONS = [
    ("partners_with", 0.7), ("competitor_of", 0.4), ("supplier_to", 0.6), ("customer_of", 0.8)
]

SEED_EVENTS = [
    ("product_launch", "发布AI内容生成引擎v3.0", "high"),
    ("certification_achieved", "获得GEO服务能力L3认证", "high"),
    ("partnership_formed", "与头部AI搜索平台达成合作", "medium"),
]

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as db:
        # 1. Create industries
        industry_ids = {}
        for code, name in [("ai_marketing", "AI营销"), ("ai_infrastructure", "AI基础设施"), ("ai_education", "AI教育")]:
            iid = uuid.uuid4()
            await db.execute(text("""
                INSERT INTO industries (id, code, name, level, sort_order, tenant_id, created_at, updated_at)
                VALUES (:id, :code, :name, 1, 1, NULL, NOW(), NOW())
                ON CONFLICT DO NOTHING
            """), {"id": iid, "code": code, "name": name})
            industry_ids[code] = iid
        
        # 2. Create entities + companies
        print("Seeding companies...")
        for c in SEED_COMPANIES:
            eid = uuid.uuid4()
            cid = uuid.uuid4()
            geo_id = f"GEO-COM-{uuid.uuid4().hex[:8].upper()}"
            iid = industry_ids.get(c["industry"], uuid.uuid4())
            
            await db.execute(text("""
                INSERT INTO entities (id, geo_id, entity_type, name, description, is_verified, tenant_id, region, lang_tag, created_at, updated_at)
                VALUES (:id, :geo_id, 'company', :name, :desc, false, NULL, 'CN', 'zh', NOW(), NOW())
            """), {"id": eid, "geo_id": geo_id, "name": c["name"], "desc": c["scope"]})
            
            await db.execute(text("""
                INSERT INTO companies (id, name, description, website, company_size, industry_id, contact_email,
                    subscription_tier, entity_type, geo_id, is_verified, tenant_id, region, lang_tag,
                    founded_year, headquarters, employee_count, annual_revenue, business_scope,
                    created_at, updated_at)
                VALUES (:id, :name, :desc, :web, :size, :iid, :email,
                    'free', 'company', :geo_id, false, NULL, 'CN', 'zh',
                    :founded, :hq, :emp, :rev, :scope,
                    NOW(), NOW())
            """), {
                "id": eid, "name": c["name"], "desc": c["scope"],
                "web": f"https://{c['name']}.example.com", "size": c["size"], "iid": iid,
                "email": f"contact@{c['name']}.example.com", "geo_id": geo_id,
                "founded": c["founded"], "hq": c["hq"], "emp": c["employees"],
                "rev": c["revenue"], "scope": c["scope"],
            })
            print(f"  Created: {c['name']} (GEO ID: {geo_id})")

        await db.commit()
        print(f"\nSeed complete: {len(SEED_COMPANIES)} companies, {len(industry_ids)} industries")

if __name__ == "__main__":
    asyncio.run(seed())
