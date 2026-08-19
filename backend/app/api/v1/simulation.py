"""Simulation closed-loop API. All results are explicitly simulation-only."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.simulation_loop_service import get_simulation_loop_service

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, PermissionError):
        return HTTPException(403, str(e))
    if isinstance(e, ValueError):
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


@router.post("/loops/run")
async def run_simulation_loop(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await get_simulation_loop_service().run(
            db, current_user, data.get("realm_id") or ""
        )
    except Exception as e:
        raise _handle(e)


@router.get("/loops/latest")
async def latest_simulation_loop(
    realm_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await get_simulation_loop_service().latest(db, current_user, realm_id)
    except Exception as e:
        raise _handle(e)
