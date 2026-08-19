"""C8.0 / C8.1 Vertical World Model Contract API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.world_model_contract import get_world_model_contract_service
from app.services.world_projection import get_world_projection_service

router = APIRouter(prefix="/api/v1/universe/worlds", tags=["worlds"])


@router.post("")
async def create_world(data: dict, db: AsyncSession = Depends(get_db)):
    svc = get_world_model_contract_service()
    try:
        return await svc.create_world(db, data.get("code", ""), data.get("name", ""), data.get("description"))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{world_code}/versions")
async def create_draft(world_code: str, data: dict, db: AsyncSession = Depends(get_db)):
    svc = get_world_model_contract_service()
    try:
        return await svc.create_draft(db, world_code, data.get("version", ""),
                                      data.get("package", {}), data.get("source_file"))
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{world_code}/versions/{version}/validate")
async def validate_package(world_code: str, version: str, data: dict):
    from app.services.world_model_contract import WorldPackageValidator
    return WorldPackageValidator().validate(data.get("package", {}))


@router.post("/{world_code}/versions/{version}/publish")
async def publish_version(world_code: str, version: str, data: dict,
                          db: AsyncSession = Depends(get_db)):
    svc = get_world_model_contract_service()
    try:
        return await svc.publish(db, world_code, version, data.get("publisher", "system"))
    except ValueError as e:
        raise HTTPException(400, str(e))


# Static route must be declared before dynamic {version} routes.
@router.get("/{world_code}/versions/diff")
async def diff_versions(world_code: str, from_version: str = Query(...), to_version: str = Query(...),
                        db: AsyncSession = Depends(get_db)):
    svc = get_world_model_contract_service()
    try:
        return await svc.diff(db, world_code, from_version, to_version)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{world_code}/versions/{version}")
async def get_version(world_code: str, version: str, db: AsyncSession = Depends(get_db)):
    svc = get_world_model_contract_service()
    try:
        return await svc.get_version(db, world_code, version)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{world_code}/versions/{version}/compiled")
async def get_compiled(world_code: str, version: str, db: AsyncSession = Depends(get_db)):
    svc = get_world_model_contract_service()
    try:
        return await svc.compiled(db, world_code, version)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{world_code}/versions/{version}/bindings")
async def create_binding(world_code: str, version: str, data: dict,
                         db: AsyncSession = Depends(get_db)):
    svc = get_world_model_contract_service()
    try:
        return await svc.create_binding(
            db, world_code, version,
            data.get("entity_type", ""), data.get("entity_id", ""),
            data.get("concept_code", ""), data.get("truth_status", "observed"),
            data.get("evidence_claim_ids"), data.get("rule_version", "1.0.0"),
            data.get("mapping_source", "manual"), data.get("created_by"),
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


# ---- C8.1 Trusted World Projection ----

@router.get("/{world_code}/versions/{version}/projection")
async def projection(world_code: str, version: str, as_of: str = Query(None),
                     production_only: bool = Query(False),
                     db: AsyncSession = Depends(get_db)):
    svc = get_world_projection_service()
    try:
        return await svc.project(db, world_code, version, as_of=as_of, production_only=production_only)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{world_code}/versions/{version}/projection/coverage")
async def projection_coverage(world_code: str, version: str, as_of: str = Query(None),
                              db: AsyncSession = Depends(get_db)):
    svc = get_world_projection_service()
    try:
        data = await svc.project(db, world_code, version, as_of=as_of)
        return {"coverage": data["coverage"], "truth_status_distribution": data["truth_status_distribution"]}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{world_code}/versions/{version}/projection/unknown")
async def projection_unknown(world_code: str, version: str, as_of: str = Query(None),
                             db: AsyncSession = Depends(get_db)):
    svc = get_world_projection_service()
    try:
        data = await svc.project(db, world_code, version, as_of=as_of)
        return data["unknown"]
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{world_code}/versions/{version}/projection/excluded")
async def projection_excluded(world_code: str, version: str, as_of: str = Query(None),
                              production_only: bool = Query(True),
                              db: AsyncSession = Depends(get_db)):
    svc = get_world_projection_service()
    try:
        data = await svc.project(db, world_code, version, as_of=as_of, production_only=production_only)
        return {"excluded": data["excluded"], "count": len(data["excluded"])}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{world_code}/versions/{version}/projection/source-chain")
async def projection_source_chain(world_code: str, version: str,
                                  entity_id: str = Query(...), concept_code: str = Query(...),
                                  db: AsyncSession = Depends(get_db)):
    svc = get_world_projection_service()
    try:
        return await svc.source_chain(db, world_code, version, entity_id, concept_code)
    except ValueError as e:
        raise HTTPException(400, str(e))
