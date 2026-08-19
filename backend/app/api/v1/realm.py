"""V10-P0 Realm owner API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.realm_service import get_realm_service

router = APIRouter(prefix="/api/v1/realm", tags=["realm"])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, PermissionError):
        return HTTPException(403, str(e))
    if isinstance(e, ValueError):
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


@router.post("/enterprises")
async def create_enterprise(data: dict, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().create_enterprise(db, current_user, data)
    except Exception as e:
        raise _handle(e)


@router.post("/brands")
async def create_brand(data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().create_brand(db, current_user, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{entity_id}/claim")
async def claim(entity_id: str, data: dict = None, db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().claim(db, current_user, entity_id, data or {})
    except Exception as e:
        raise _handle(e)


@router.post("/claims/{claim_id}/decision")
async def decide_claim(claim_id: str, data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().decide_claim(
            db, current_user, claim_id,
            data.get("decision", ""),
            reason=data.get("reason"),
            force=bool(data.get("force", False)),
        )
    except Exception as e:
        raise _handle(e)


@router.get("/claims")
async def list_claims(status: str = Query("pending"), db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        return {"claims": await get_realm_service().list_claims(db, current_user, status)}
    except Exception as e:
        raise _handle(e)


@router.get("/mine")
async def list_mine(db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    return {"realms": await get_realm_service().list_mine(db, current_user)}


@router.get("/boundary")
async def boundary(db: AsyncSession = Depends(get_db)):
    return await get_realm_service().boundary(db)


@router.get("/{entity_id}")
async def workspace(entity_id: str, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().get_workspace(db, current_user, entity_id)
    except Exception as e:
        raise _handle(e)


@router.post("/{entity_id}/relationships")
async def add_relationship(entity_id: str, data: dict, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().add_relationship(db, current_user, entity_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{entity_id}/authorizations")
async def create_authorization(entity_id: str, data: dict, db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().create_authorization(db, current_user, entity_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{entity_id}/authorizations/{authorization_id}/revoke")
async def revoke_authorization(entity_id: str, authorization_id: str, data: dict = None,
                               db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().revoke_authorization(
            db, current_user, entity_id, authorization_id,
            reason=(data or {}).get("reason"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{entity_id}/assets")
async def create_asset(entity_id: str, data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().create_asset(db, current_user, entity_id, data)
    except Exception as e:
        raise _handle(e)


@router.get("/{entity_id}/tool-configs")
async def get_tool_configs(entity_id: str, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    try:
        return {"configs": await get_realm_service().get_tool_configs(db, current_user, entity_id)}
    except Exception as e:
        raise _handle(e)


@router.put("/{entity_id}/tool-configs/{key}")
async def save_tool_config(entity_id: str, key: str, data: dict,
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().save_tool_config(
            db, current_user, entity_id, key, data.get("config") or {}
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{entity_id}/evidence")
async def create_evidence(entity_id: str, data: dict, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    try:
        return await get_realm_service().create_evidence(db, current_user, entity_id, data)
    except Exception as e:
        raise _handle(e)
