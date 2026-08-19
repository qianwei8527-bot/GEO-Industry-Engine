"""V10-P0 GEO Project API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.geo_project_service import get_geo_project_service

router = APIRouter(prefix="/api/v1/geo-projects", tags=["geo-projects"])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, PermissionError):
        return HTTPException(403, str(e))
    if isinstance(e, ValueError):
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


@router.post("")
async def create_project(data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().create_project(db, current_user, data)
    except Exception as e:
        raise _handle(e)


@router.get("")
async def list_projects(realm_id: str = Query(None), db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        return {"projects": await get_geo_project_service().list_projects(db, current_user, realm_id)}
    except Exception as e:
        raise _handle(e)


@router.get("/review/artifacts")
async def review_artifacts(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    try:
        return {"artifacts": await get_geo_project_service().list_draft_artifacts(db, current_user)}
    except Exception as e:
        raise _handle(e)


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().get_project(db, current_user, project_id)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/work-items")
async def create_work_item(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().create_work_item(db, current_user, project_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/artifacts")
async def create_artifact(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().create_artifact(db, current_user, project_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/artifacts/{artifact_id}/publish")
async def publish_artifact(project_id: str, artifact_id: str, data: dict,
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().publish_artifact(db, current_user, artifact_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/tool-executions")
async def create_tool_execution(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().create_tool_execution(db, current_user, project_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/tool-executions/run")
async def run_local_tool(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().run_local_tool(db, current_user, project_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/outcomes")
async def create_outcome(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().create_outcome(db, current_user, project_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/monitoring-results")
async def record_monitoring_result(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                   current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().record_monitoring_result(db, current_user, project_id, data)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/outcomes/{outcome_id}/refresh")
async def refresh_outcome(project_id: str, outcome_id: str, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().refresh_outcome(db, current_user, outcome_id)
    except Exception as e:
        raise _handle(e)


@router.get("/{project_id}/summary")
async def project_summary(project_id: str, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().project_summary(db, current_user, project_id)
    except Exception as e:
        raise _handle(e)


@router.get("/{project_id}/timeline")
async def timeline(project_id: str, db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    try:
        return {"timeline": await get_geo_project_service().timeline(db, current_user, project_id)}
    except Exception as e:
        raise _handle(e)


@router.get("/{project_id}/assets")
async def project_assets(project_id: str, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_geo_project_service().project_assets(db, current_user, project_id)
    except Exception as e:
        raise _handle(e)
