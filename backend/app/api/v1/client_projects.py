"""Client collaboration token API.

Reuses RealmDataAuthorization as the bearer capability. A valid token with
use_scope=client_project can list projects of the bound Realm.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.geo_project import GeoProject, ProjectOutcome
from app.models.issue import IssueRecord
from app.models.realm import RealmDataAsset, RealmDataAuthorization, RealmRegistry

router = APIRouter(prefix="/api/v1/client", tags=["client"])


class ClientFeedbackInput(BaseModel):
    token: str
    original_text: str
    scenario: str | None = None
    severity: str = "medium"


@router.get("/projects/{secure_token}")
async def list_client_projects(secure_token: str, db: AsyncSession = Depends(get_db)):
    auth = (
        await db.execute(
            select(RealmDataAuthorization).where(
                RealmDataAuthorization.authorization_code == secure_token
            )
        )
    ).scalars().first()
    if not auth:
        raise HTTPException(404, "client token not found")
    if auth.status != "active":
        raise HTTPException(403, "client token is not active")
    if auth.use_scope not in ("client_project", "project_delivery"):
        raise HTTPException(403, "token scope is not client_project")
    registry = (
        await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == auth.entity_id)
        )
    ).scalars().first()
    if not registry:
        raise HTTPException(404, "realm not found")
    projects = (
        await db.execute(
            select(GeoProject)
            .where(GeoProject.realm_entity_id == registry.entity_id)
            .order_by(GeoProject.created_at.desc())
        )
    ).scalars().all()
    project_rows = []
    for p in projects:
        assets = (
            await db.execute(
                select(RealmDataAsset).where(RealmDataAsset.project_id == p.id)
            )
        ).scalars().all()
        outcomes = (
            await db.execute(
                select(ProjectOutcome).where(ProjectOutcome.project_id == p.id)
            )
        ).scalars().all()
        project_rows.append(
            {
                "id": str(p.id),
                "project_code": p.project_code,
                "name": p.name,
                "status": p.status,
                "lifecycle_state": p.lifecycle_state,
                "truth_status": p.truth_status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "assets": [
                    {
                        "title": a.title,
                        "asset_type": a.asset_type,
                        "truth_status": a.truth_status,
                    }
                    for a in assets
                ],
                "outcomes": [
                    {
                        "claim_text": o.claim_text,
                        "outcome_type": o.outcome_type,
                        "truth_status": o.truth_status,
                    }
                    for o in outcomes
                ],
            }
        )
    return {
        "token_status": "valid",
        "realm": {
            "realm_code": registry.realm_code,
            "realm_type": registry.realm_type,
            "display_name": registry.display_name,
        },
        "authorization": {
            "use_scope": auth.use_scope,
            "source_name": auth.source_name,
            "grantee_type": auth.grantee_type,
            "valid_until": auth.valid_until.isoformat() if auth.valid_until else None,
            "status": auth.status,
            "authorization_code_masked": _mask_code(auth.authorization_code),
        },
        "projects": project_rows,
    }


@router.post("/projects/{project_id}/feedback")
async def submit_client_feedback(
    project_id: str, body: ClientFeedbackInput, db: AsyncSession = Depends(get_db)
):
    auth = (
        await db.execute(
            select(RealmDataAuthorization).where(
                RealmDataAuthorization.authorization_code == body.token
            )
        )
    ).scalars().first()
    if not auth or auth.status != "active" or auth.use_scope not in ("client_project", "project_delivery"):
        raise HTTPException(403, "client token is invalid")
    registry = (
        await db.execute(
            select(RealmRegistry).where(RealmRegistry.entity_id == auth.entity_id)
        )
    ).scalars().first()
    if not registry:
        raise HTTPException(404, "realm not found")
    project = await db.get(GeoProject, project_id)
    if not project or str(project.realm_entity_id) != str(registry.entity_id):
        raise HTTPException(404, "project not found for this token")
    if not body.original_text.strip():
        raise HTTPException(400, "original_text is required")
    issue = IssueRecord(
        issue_code=f"ISS-{uuid.uuid4().hex[:12].upper()}",
        realm_id=registry.id,
        project_id=project.id,
        original_text=body.original_text.strip(),
        scenario=body.scenario,
        source="client_token",
        severity=body.severity,
        status="new",
    )
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return {"status": "received", "issue_code": issue.issue_code}


def _mask_code(code: str) -> str:
    if not code:
        return ""
    if len(code) <= 14:
        return f"{code[:6]}••••"
    return f"{code[:14]}••••{code[-4:]}"
