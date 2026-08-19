"""V10.6-R4 issue closed-loop API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.issue_service import IssueStateError, get_issue_service

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


def _handle(e: Exception) -> HTTPException:
    if isinstance(e, PermissionError):
        return HTTPException(404, "resource not found")
    if isinstance(e, IssueStateError):
        return HTTPException(409, str(e))
    if isinstance(e, ValueError):
        if str(e) in (
            "issue not found",
            "artifact not found",
            "issue_id must be a valid UUID",
            "artifact_id must be a valid UUID",
        ):
            return HTTPException(404, "resource not found")
        return HTTPException(400, str(e))
    return HTTPException(500, str(e))


@router.post("")
async def create_issue(data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().create_issue(
            db, current_user, data.get("realm_id", ""), data,
        )
    except Exception as e:
        raise _handle(e)


@router.get("")
async def list_issues(realm_id: str, project_id: str = Query(None), status: str = Query(None),
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        return {"issues": await get_issue_service().list_issues(
            db, current_user, realm_id, project_id=project_id, status=status,
        )}
    except Exception as e:
        raise _handle(e)


@router.get("/skills")
async def list_skills(realm_id: str, project_id: str = Query(None), db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        return {"skills": await get_issue_service().list_skill_drafts(db, current_user, realm_id, project_id)}
    except Exception as e:
        raise _handle(e)


@router.get("/skills/{artifact_id}")
async def get_skill_draft(artifact_id: str, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    try:
        service = get_issue_service()
        artifact = await service._require_artifact(db, artifact_id)
        realm_id = (artifact.metadata_json or {}).get("realm_id") or ""
        if not await service._control(db, current_user, realm_id):
            raise PermissionError("realm member permission required")
        return service._artifact_dict(artifact)
    except Exception as e:
        raise _handle(e)


@router.patch("/skills/{artifact_id}")
async def update_skill_draft(artifact_id: str, data: dict, db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().update_skill_draft(
            db, current_user, artifact_id, data.get("edits") or {},
            data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/skills/{artifact_id}/confirm")
async def confirm_skill(artifact_id: str, data: dict, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().confirm_skill(
            db, current_user, artifact_id, bool(data.get("confirmed", False)),
        )
    except Exception as e:
        raise _handle(e)


@router.get("/members/{realm_id}")
async def list_realm_members(realm_id: str, db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    try:
        return {"members": await get_issue_service().list_realm_members(db, current_user, realm_id)}
    except Exception as e:
        raise _handle(e)


@router.get("/{issue_id}")
async def get_issue(issue_id: str, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().get_issue(db, current_user, issue_id)
    except Exception as e:
        raise _handle(e)


@router.patch("/{issue_id}")
async def update_issue(issue_id: str, data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().update_issue(
            db, current_user, issue_id, data, data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{issue_id}/classify")
async def classify_issue(issue_id: str, data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().classify_issue(
            db, current_user, issue_id, data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{issue_id}/classification/confirm")
async def confirm_classification(issue_id: str, data: dict, db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().confirm_classification(
            db, current_user, issue_id, data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{issue_id}/attempts")
async def add_attempt(issue_id: str, data: dict, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().add_attempt(
            db, current_user, issue_id, data, data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{issue_id}/resolve")
async def resolve_issue(issue_id: str, data: dict, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().resolve_issue(
            db, current_user, issue_id, data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{issue_id}/verify")
async def verify_issue(issue_id: str, data: dict, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    try:
        return await get_issue_service().verify_issue(
            db, current_user, issue_id, data.get("expected_version"),
        )
    except Exception as e:
        raise _handle(e)


@router.post("/{issue_id}/skills/generate")
async def generate_skill(issue_id: str, data: dict, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    try:
        issue_ids = data.get("issue_ids") or [issue_id]
        if not isinstance(issue_ids, list) or not issue_ids:
            raise ValueError("issue_ids 不能为空")
        return await get_issue_service().generate_skill(db, current_user, issue_ids)
    except Exception as e:
        raise _handle(e)
