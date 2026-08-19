"""V10.6-R3 project plan API."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.project_plan_service import PlanStateError, get_project_plan_service

router = APIRouter(prefix="/api/v1/project-plans", tags=["project-plans"])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, PermissionError):
        return HTTPException(404, "resource not found")
    if isinstance(e, PlanStateError):
        return HTTPException(409, str(e))
    if isinstance(e, ValueError):
        if str(e) in (
            "project not found",
            "task not found",
            "project_id must be a valid UUID",
            "task_id or project_id must be a valid UUID",
        ):
            return HTTPException(404, "resource not found")
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


@router.get("/sources")
async def list_sources(db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_project_plan_service().list_workflow_sources(db, current_user)
    except Exception as e:
        raise _handle(e)


@router.get("/{project_id}")
async def list_plan(project_id: str, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    try:
        return await get_project_plan_service().list_plan(db, current_user, project_id)
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/generate")
async def generate_plan(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        return await get_project_plan_service().generate_plan(
            db, current_user, project_id,
            data.get("source_type") or "platform_seed",
            data.get("source_id"),
            data.get("template"),
        )
    except Exception as e:
        raise _handle(e)


@router.put("/{project_id}/draft")
async def update_draft(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_project_plan_service().update_draft(
            db, current_user, project_id, data.get("expected_version"), data.get("plan") or {},
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{project_id}/confirm")
async def confirm_plan(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_project_plan_service().confirm_plan(
            db, current_user, project_id,
            bool(data.get("confirmed", False)),
            data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.patch("/{project_id}/tasks/{task_id}")
async def update_task(project_id: str, task_id: str, data: dict,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        return await get_project_plan_service().update_task(
            db, current_user, project_id, task_id, data,
            data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.get("/{project_id}/export.csv")
async def export_plan(project_id: str, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        csv_text = await get_project_plan_service().export_plan_csv(db, current_user, project_id)
    except Exception as e:
        raise _handle(e)
    return PlainTextResponse(csv_text, media_type="text/csv; charset=utf-8")
