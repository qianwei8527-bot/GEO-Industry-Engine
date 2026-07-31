import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import _get_session_factory
from app.models.provider import Provider
from app.models.provider_capability import ProviderCapability
from app.models.market_demand import MarketDemand, DemandCategory, DemandStatus
from app.models.entity import Entity
from app.models.capability import Capability
from app.models.industry import Industry
from sqlalchemy import select
import uuid

async def seed():
    async with _get_session_factory()() as db:
        entities = (await db.execute(select(Entity).where(Entity.entity_type == 'company').limit(5))).scalars().all()
        industries = (await db.execute(select(Industry).limit(5))).scalars().all()
        caps = (await db.execute(select(Capability).limit(10))).scalars().all()

        if len(entities) < 2:
            print("Need at least 2 entities, found", len(entities))
            return

        providers_data = [
            {"entity_id": entities[0].id, "provider_type": "company", "trust_score": 82.5, "geo_score": 78.0,
             "verification_status": "verified", "is_verified": True, "completed_orders": 15, "avg_rating": 4.5,
             "pricing_model": {"model": "project", "range_min": 5000, "range_max": 50000}},
        ]
        if len(entities) > 1:
            providers_data.append({"entity_id": entities[1].id, "provider_type": "company", "trust_score": 65.0, "geo_score": 55.5,
             "verification_status": "pending", "is_verified": False, "completed_orders": 3, "avg_rating": 3.8,
             "pricing_model": {"model": "hourly", "rate": 300}})
        if len(entities) > 2:
            providers_data.append({"entity_id": entities[2].id, "provider_type": "company", "trust_score": 91.0, "geo_score": 85.3,
             "verification_status": "verified", "is_verified": True, "completed_orders": 42, "avg_rating": 4.9,
             "pricing_model": {"model": "fixed", "range_min": 10000, "range_max": 100000}})

        providers = []
        for pd in providers_data:
            existing = (await db.execute(select(Provider).where(Provider.entity_id == pd["entity_id"]))).scalar_one_or_none()
            if existing:
                providers.append(existing)
                continue
            p = Provider(id=uuid.uuid4(), **pd)
            db.add(p)
            providers.append(p)

        # Link capabilities
        if caps and providers:
            for i, prov in enumerate(providers[:3]):
                for j, cap in enumerate(caps[:min(3, len(caps))]):
                    existing = (await db.execute(
                        select(ProviderCapability).where(
                            ProviderCapability.provider_id == prov.id,
                            ProviderCapability.capability_id == cap.id
                        )
                    )).scalar_one_or_none()
                    if not existing:
                        pc = ProviderCapability(id=uuid.uuid4(), provider_id=prov.id, capability_id=cap.id,
                                               level=3 + (j % 3), verified=True, experience_years=1.5 + (i * 2))
                        db.add(pc)

        # Create demands
        if entities and industries:
            demands_data = [
                {"publisher_id": entities[0].id, "title": "提升AI搜索可见度", "description": "需要专业的GEO优化服务",
                 "category": DemandCategory.SERVICE, "industry_id": industries[0].id if industries else None,
                 "urgency_level": "high", "budget_min": 5000, "budget_max": 20000, "timeline_days": 60,
                 "requirements": {"keywords": ["GEO优化", "AI搜索"]}, "status": DemandStatus.OPEN},
            ]
            if len(entities) > 1:
                demands_data.append({"publisher_id": entities[1].id, "title": "企业AI数据训练服务", "description": "需要数据标注和AI模型微调",
                 "category": DemandCategory.DATA, "industry_id": industries[1].id if len(industries) > 1 else None,
                 "urgency_level": "normal", "budget_min": 20000, "budget_max": 80000, "timeline_days": 90,
                 "requirements": {"data_type": ["文本"]}, "status": DemandStatus.OPEN})
            for dd in demands_data:
                d = MarketDemand(id=uuid.uuid4(), demand_type="demand", **dd)
                db.add(d)

        await db.commit()
        print(f"Seeded: {len(providers)} providers, {len(caps)} caps, {len(entities)} entities used")

asyncio.run(seed())