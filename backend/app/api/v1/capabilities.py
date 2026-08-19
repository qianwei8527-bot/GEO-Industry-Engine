"""V10.1 Sixth Business Module API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.capability_service import get_capability_service

router = APIRouter(prefix="/api/v1/capabilities", tags=["capabilities"])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, PermissionError):
        return HTTPException(403, str(e))
    if isinstance(e, ValueError):
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


@router.get("")
async def list_capabilities(source_mode: str = Query(None), capability_type: str = Query(None),
                            realm_entity_id: str = Query(None), db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    try:
        return {"capabilities": await get_capability_service().list(
            db, current_user, source_mode, capability_type, realm_entity_id
        )}
    except Exception as e:
        raise _handle(e)


@router.get("/public")
async def list_public_capabilities():
    return {"capabilities": get_capability_service().list_public()}


@router.post("")
async def create_capability(data: dict, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    try:
        return await get_capability_service().create(db, current_user, data)
    except Exception as e:
        raise _handle(e)


@router.get("/runs")
async def list_runs(project_id: str = Query(None), realm_entity_id: str = Query(None),
                    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return {"runs": await get_capability_service().list_runs(db, current_user, project_id, realm_entity_id)}
    except Exception as e:
        raise _handle(e)


@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: AsyncSession = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    try:
        return await get_capability_service().get_run(db, current_user, run_id)
    except Exception as e:
        raise _handle(e)


@router.get("/{capability_id}")
async def get_capability(capability_id: str, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_capability_service().get(db, current_user, capability_id)
    except Exception as e:
        raise _handle(e)


@router.post("/{capability_id}/run")
async def run_capability(capability_id: str, data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_capability_service().run(db, current_user, capability_id, data)
    except Exception as e:
        raise _handle(e)
