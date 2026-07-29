import asyncio, sys, os, uuid
sys.path.insert(0, r"D:\GEO-Industry-Engine\backend")
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.config import settings

SEED_COMPANIES = [
    {"name": "星辰AI营销科技", "industry": "ai_marketing", "size": "50-200", "founded": 2020, "hq": "深圳", "employees": 85, "revenue": "5000万-1亿", "scope": "AI内容生成与GEO优化服务"},
    {"name": "鼎新云计算", "industry": "ai_infrastructure", "size": "500+", "founded": 2015, "hq": "北京", "employees": 1200, "revenue": "10亿+", "scope": "AI算力基础设施与模型服务"},
    {"name": "未来教育科技", "industry": "ai_education", "size": "10-50", "founded": 2022, "hq": "杭州", "employees": 28, "revenue": "500万-1000万", "scope": "AI个性化学习平台"},
]

SEED_INDUSTRIES = [
    ("ai_marketing", "AI营销"),
    ("ai_infrastructure", "AI基础设施"),
    ("ai_education", "AI教育"),
]

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as db:
        # Industries
        industry_ids = {}
        for code, name in SEED_INDUSTRIES:
            iid = str(uuid.uuid4())
            sql = text("INSERT INTO industries (id, code, name, level, sort_order, tenant_id, created_at, updated_at) VALUES (:id, :code, :name, 1, 1, NULL, NOW(), NOW()) ON CONFLICT DO NOTHING")
            await db.execute(sql, {"id": iid, "code": code, "name": name})
            industry_ids[code] = iid
            print(f"  Industry: {name}")

        # Companies
        print("Seeding companies...")
        for c in SEED_COMPANIES:
            eid = str(uuid.uuid4())
            geo_id = "GEO-COM-" + uuid.uuid4().hex[:8].upper()
            iid = industry_ids.get(c["industry"], str(uuid.uuid4()))
            
            web = "https://" + c["name"] + ".example.com"
            email_addr = "contact@" + c["name"] + ".example.com"

            # Entity
            await db.execute(text(
                "INSERT INTO entities (id, geo_id, entity_type, name, description, is_verified, tenant_id, region, lang_tag, created_at, updated_at) "
                "VALUES (:id, :geo_id, :type, :name, :desc, false, NULL, :region, :lang, NOW(), NOW())"
            ), {"id": eid, "geo_id": geo_id, "type": "company", "name": c["name"], "desc": c["scope"], "region": "CN", "lang": "zh"})

            # Company
            await db.execute(text(
                "INSERT INTO companies (id, name, description, website, company_size, industry_id, contact_email, "
                "subscription_tier, entity_type, geo_id, is_verified, tenant_id, region, lang_tag, "
                "founded_year, headquarters, employee_count, annual_revenue, business_scope, created_at, updated_at) "
                "VALUES (:id, :name, :desc, :web, :size, :iid, :email, :tier, :type, :geo_id, false, NULL, :region, :lang, "
                ":founded, :hq, :emp, :rev, :scope, NOW(), NOW())"
            ), {
                "id": eid, "name": c["name"], "desc": c["scope"], "web": web, "size": c["size"],
                "iid": iid, "email": email_addr, "tier": "free", "type": "company", "geo_id": geo_id,
                "region": "CN", "lang": "zh", "founded": c["founded"], "hq": c["hq"], "emp": c["employees"],
                "rev": c["revenue"], "scope": c["scope"],
            })
            print("  Created: " + c["name"] + " (" + geo_id + ")")

        await db.commit()
        print("\nSeed complete: {} companies, {} industries".format(len(SEED_COMPANIES), len(industry_ids)))

if __name__ == "__main__":
    asyncio.run(seed())
