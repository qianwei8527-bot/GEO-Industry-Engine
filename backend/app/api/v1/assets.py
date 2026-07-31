from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.entity import Entity
from app.models.company import Company
from app.models.capability import Capability
from app.models.certification import Certification, CertStatus
from app.models.evidence import Evidence
from app.models.trust import Trust
from app.models.market_demand import MarketDemand, DemandStatus
from app.models.provider import Provider
from app.models.industry import Industry

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

@router.get("/overview")
async def assets_overview(db: AsyncSession = Depends(get_db)):
    companies = (await db.execute(select(func.count(Company.id)))).scalar() or 0
    entities = (await db.execute(select(func.count(Entity.id)).where(Entity.entity_type == "company"))).scalar() or 0
    providers = (await db.execute(select(func.count(Provider.id)))).scalar() or 0
    capabilities = (await db.execute(select(func.count(Capability.id)))).scalar() or 0
    evidence_count = (await db.execute(select(func.count(Evidence.id)))).scalar() or 0
    certified = (await db.execute(select(func.count(Certification.id)).where(Certification.status == CertStatus.APPROVED))).scalar() or 0
    avg_geo = (await db.execute(select(func.avg(Company.geo_score)))).scalar()
    avg_trust = (await db.execute(select(func.avg(Trust.trust_score)))).scalar()
    open_demands = (await db.execute(select(func.count(MarketDemand.id)).where(MarketDemand.status == DemandStatus.OPEN))).scalar() or 0

    industries = (await db.execute(
        select(Industry.name, func.count(Company.id).label("cnt"))
        .join(Company, Company.industry_id == Industry.id, isouter=True)
        .group_by(Industry.id, Industry.name).order_by(func.count(Company.id).desc()).limit(10)
    )).all()

    return {
        "total_companies": companies,
        "total_entities": entities,
        "total_providers": providers,
        "total_capabilities": capabilities,
        "total_evidence": evidence_count,
        "certified_companies": certified,
        "avg_geo_score": round(float(avg_geo), 1) if avg_geo else 0,
        "avg_trust_score": round(float(avg_trust), 2) if avg_trust else 0,
        "open_demands": open_demands,
        "industries": [{"name": i[0], "company_count": i[1]} for i in industries],
    }

@router.get("/capabilities")
async def assets_capabilities(db: AsyncSession = Depends(get_db)):
    caps = (await db.execute(select(Capability))).scalars().all()
    result = []
    for cap in caps[:30]:
        provider_count = (await db.execute(
            select(func.count()).select_from(Company).join(Capability, Capability.company_id == Company.id).where(Capability.id == cap.id)
        )).scalar() or 0
        demand_count = 5  # placeholder - would match demand requirements
        result.append({
            "name": cap.name,
            "category": cap.category,
            "provider_count": provider_count,
            "demand_count": demand_count,
            "gap": demand_count - provider_count,
            "opportunity_level": "high" if demand_count > provider_count * 2 else "medium" if demand_count > provider_count else "low",
        })
    return sorted(result, key=lambda x: x["gap"], reverse=True)

@router.get("/industries")
async def assets_industries(db: AsyncSession = Depends(get_db)):
    industries = (await db.execute(select(Industry))).scalars().all()
    result = []
    for ind in industries:
        company_count = (await db.execute(
            select(func.count(Company.id)).where(Company.industry_id == ind.id)
        )).scalar() or 0
        demand_count = (await db.execute(
            select(func.count(MarketDemand.id)).where(MarketDemand.industry_id == ind.id, MarketDemand.status == DemandStatus.OPEN)
        )).scalar() or 0
        result.append({
            "id": str(ind.id),
            "name": ind.name,
            "code": ind.code,
            "company_count": company_count,
            "open_demands": demand_count,
            "opportunity_index": round(demand_count / max(company_count, 1), 2),
        })
    return sorted(result, key=lambda x: x["company_count"], reverse=True)

@router.get("/opportunities")
async def assets_opportunities(db: AsyncSession = Depends(get_db)):
    demands = (await db.execute(
        select(MarketDemand).where(MarketDemand.status == DemandStatus.OPEN).limit(20)
    )).scalars().all()
    result = []
    for d in demands:
        provider_count = (await db.execute(select(func.count(Provider.id)))).scalar() or 0
        result.append({
            "demand_id": str(d.id),
            "title": d.title,
            "category": d.category.value if hasattr(d.category, "value") else str(d.category),
            "budget_range": f"{d.budget_min or 0}-{d.budget_max or 0}",
            "urgency": d.urgency_level,
            "provider_availability": provider_count,
            "opportunity_score": round(min(provider_count / 10, 1.0) * 100, 1),
        })
    return result
