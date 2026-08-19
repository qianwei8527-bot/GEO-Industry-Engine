'''V10.5 execution plan API.'''

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.execution_plan_service import get_execution_plan_service

router = APIRouter(prefix='/api/v1/execution', tags=['execution'])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, PermissionError):
        return HTTPException(403, str(e))
    if isinstance(e, ValueError):
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


@router.get('/projects/{project_id}/plan')
async def list_plan(project_id: str, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    try:
        return await get_execution_plan_service().list_plan(db, current_user, project_id)
    except Exception as e:
        raise _handle(e)


@router.post('/projects/{project_id}/plan/generate')
async def generate_plan(project_id: str, data: dict, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        return await get_execution_plan_service().generate_plan(
            db, current_user, project_id, bool(data.get('replace_existing', False)),
        )
    except Exception as e:
        raise _handle(e)


@router.patch('/projects/{project_id}/work-items/{work_item_id}')
async def update_work_item(project_id: str, work_item_id: str, data: dict,
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    try:
        return await get_execution_plan_service().update_work_item(
            db, current_user, project_id, work_item_id, data,
        )
    except Exception as e:
        raise _handle(e)


@router.post('/projects/{project_id}/work-items/{work_item_id}/sync')
async def sync_work_item(project_id: str, work_item_id: str, data: dict,
                         db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_execution_plan_service().sync_work_item(
            db, current_user, project_id, work_item_id, data,
        )
    except Exception as e:
        raise _handle(e)


@router.get('/projects/{project_id}/plan/export')
async def export_plan(project_id: str, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        csv_text = await get_execution_plan_service().export_plan_csv(db, current_user, project_id)
    except Exception as e:
        raise _handle(e)
    return PlainTextResponse(csv_text, media_type='text/csv')
