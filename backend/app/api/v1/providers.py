from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.provider import Provider
from app.models.provider_capability import ProviderCapability
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderResponse, ProviderCapabilityCreate, ProviderCapabilityResponse
import uuid

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])

@router.post("", status_code=201)
async def create_provider(data: ProviderCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Provider).where(Provider.entity_id == data.entity_id))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Provider already exists for this entity")
    p = Provider(**data.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return ProviderResponse.model_validate(p)

@router.get("")
async def list_providers(
    provider_type: str = Query(None),
    is_verified: bool = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Provider).order_by(desc(Provider.geo_score)).offset(skip).limit(limit)
    if provider_type:
        stmt = stmt.where(Provider.provider_type == provider_type)
    if is_verified is not None:
        stmt = stmt.where(Provider.is_verified == is_verified)
    r = await db.execute(stmt)
    return [ProviderResponse.model_validate(p) for p in r.scalars().all()]

@router.get("/{provider_id}")
async def get_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Provider).where(Provider.id == provider_id))
    p = r.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Provider not found")
    return ProviderResponse.model_validate(p)

@router.get("/entity/{entity_id}")
async def get_provider_by_entity(entity_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Provider).where(Provider.entity_id == entity_id))
    p = r.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "No provider for this entity")
    return ProviderResponse.model_validate(p)

@router.put("/{provider_id}")
async def update_provider(provider_id: str, data: ProviderUpdate, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Provider).where(Provider.id == provider_id))
    p = r.scalar_one_or_none()
    if not p:
        raise HTTPException(404, "Provider not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return ProviderResponse.model_validate(p)

@router.post("/capabilities", status_code=201)
async def add_provider_capability(data: ProviderCapabilityCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(ProviderCapability).where(
            ProviderCapability.provider_id == data.provider_id,
            ProviderCapability.capability_id == data.capability_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Capability already linked to provider")
    pc = ProviderCapability(**data.model_dump())
    db.add(pc)
    await db.commit()
    await db.refresh(pc)
    return ProviderCapabilityResponse.model_validate(pc)

@router.get("/capabilities/{provider_id}")
async def list_provider_capabilities(provider_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(ProviderCapability).where(ProviderCapability.provider_id == provider_id)
    )
    return [ProviderCapabilityResponse.model_validate(pc) for pc in r.scalars().all()]

@router.delete("/capabilities/{cap_link_id}", status_code=204)
async def remove_provider_capability(cap_link_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ProviderCapability).where(ProviderCapability.id == cap_link_id))
    pc = r.scalar_one_or_none()
    if not pc:
        raise HTTPException(404, "Capability link not found")
    await db.delete(pc)
    await db.commit()
