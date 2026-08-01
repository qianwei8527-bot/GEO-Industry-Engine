"""C6.0 Real Node Onboarding API.

普通企业用户通过 /universe/join 前端分步提交资料，
本 API 负责草稿保存、校验、激活与状态查询。

激活编排由 NodeActivationService 完成（复用现有 Engine，无新 Engine）。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.models.onboarding_session import OnboardingSession
from app.services.node_activation import NodeActivationService
from app.services.governance import get_governance_service
from app.api.deps import get_current_user
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/v1/universe/onboarding", tags=["onboarding"])


@router.get("/config")
async def get_onboarding_config():
    """Return step definitions, evidence types, and validation rules to the frontend."""
    svc = NodeActivationService()
    cfg = svc.config
    return {
        "steps": cfg.get("steps", []),
        "evidence_types": cfg.get("steps", [{}])[3].get("evidence_types", []) if cfg.get("steps") else [],
        "evidence_confidence": cfg.get("evidence_confidence", {}),
        "validation": cfg.get("validation", {}),
        "activation_stages": cfg.get("activation_stages", []),
    }


@router.post("")
async def create_onboarding(data: dict, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    """Create an onboarding draft session bound to the authenticated user."""
    key = (data.get("idempotency_key") or "").strip()
    if not key:
        key = f"onb-{uuid.uuid4().hex[:12]}"
    svc = NodeActivationService()
    session = await svc.create_session(db, key, data.get("company_name", ""), user_id=current_user.id)
    if data.get("data"):
        session = await svc.save_draft(db, str(session.id), data["data"], data.get("current_step", 1))
    return {
        "session_id": str(session.id),
        "idempotency_key": session.idempotency_key,
        "session_status": session.session_status,
        "current_step": session.current_step,
        "data": session.data_json or {},
    }




async def _guard_session(db, session_id: str, user: User):
    """C6.2: only the session owner (or system admin) may read/modify a draft."""
    session = await db.get(OnboardingSession, uuid.UUID(session_id))
    if not session:
        raise HTTPException(404, "Session not found")
    gov = get_governance_service()
    is_admin = gov.is_system_admin(user)
    if session.user_id and str(session.user_id) != str(user.id) and not is_admin:
        raise HTTPException(403, "This onboarding draft belongs to another user")
    return session

@router.get("/{session_id}")
async def get_onboarding(session_id: str, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """Read a draft session (owner only)."""
    session = await _guard_session(db, session_id, current_user)
    return {
        "session_id": str(session.id),
        "idempotency_key": session.idempotency_key,
        "session_status": session.session_status,
        "current_step": session.current_step,
        "company_name": session.company_name,
        "data": session.data_json or {},
        "activation_result": session.activation_result_json,
        "error": session.error_message,
    }


@router.patch("/{session_id}")
async def save_onboarding(session_id: str, data: dict, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """Save partial onboarding data (draft autosave, owner only)."""
    await _guard_session(db, session_id, current_user)
    svc = NodeActivationService()
    try:
        session = await svc.save_draft(db, session_id, data.get("data", {}), data.get("current_step", 1))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "session_id": str(session.id),
        "session_status": session.session_status,
        "current_step": session.current_step,
        "data": session.data_json or {},
    }


@router.post("/{session_id}/validate")
async def validate_onboarding(session_id: str, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    """Validate completeness, duplicates, and evidence format (owner only)."""
    session = await _guard_session(db, session_id, current_user)
    svc = NodeActivationService()
    result = await svc.validate(db, session)
    result["session_id"] = session_id
    return result


@router.post("/{session_id}/activate")
async def activate_onboarding(session_id: str, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    """Confirm and activate the node. Runs the full lifecycle pipeline (owner only)."""
    session = await _guard_session(db, session_id, current_user)
    svc = NodeActivationService()
    result = await svc.activate(db, session)
    return result


@router.get("/{session_id}/status")
async def onboarding_status(session_id: str, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    """Return activation pipeline status (owner only)."""
    session = await _guard_session(db, session_id, current_user)
    svc = NodeActivationService()
    return await svc.get_status(db, session)
