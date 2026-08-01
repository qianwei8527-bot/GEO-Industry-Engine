from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user, security
import uuid
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import (hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, hash_jti, jti_and_family)

router = APIRouter()

async def _issue_refresh(db, user_id, family=None, jti=None):
    """Issue a refresh token and persist its JTI hash (raw token never stored)."""
    from app.models.refresh_token import RefreshToken
    from app.core.security import create_refresh_token, hash_jti
    jti = jti or str(uuid.uuid4())
    family = family or str(uuid.uuid4())
    token = create_refresh_token(user_id, family=family, jti=jti)
    rec = RefreshToken(
        user_id=user_id, token_jti_hash=hash_jti(jti), token_family=family,
        issued_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(rec)
    await db.commit()
    return token


async def _revoke_family(db, family: str, reason: str):
    """Revoke every token in a family (reuse detection / logout)."""
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import select
    rows = (await db.execute(select(RefreshToken).where(RefreshToken.token_family == family, RefreshToken.revoked_at.is_(None)))).scalars().all()
    for r in rows:
        r.revoked_at = datetime.now(timezone.utc)
        r.revoke_reason = reason
    await db.commit()



@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        phone=data.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = create_access_token(user.id)
    refresh = await _issue_refresh(db, user.id)
    user.last_login_at = datetime.utcnow()
    await db.commit()
    return TokenResponse(access_token=token, refresh_token=refresh, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token(user.id)
    refresh = await _issue_refresh(db, user.id)
    return TokenResponse(access_token=token, refresh_token=refresh, user=UserResponse.model_validate(user))


@router.post("/refresh")
async def refresh(data: dict, db: AsyncSession = Depends(get_db)):
    """Exchange a refresh token with rotation.

    C6.3 Gate 0: revocation is durable; reusing an already-rotated token
    revokes the entire token family. Disabled users cannot refresh.
    """
    from app.models.refresh_token import RefreshToken
    from app.core.security import hash_jti, jti_and_family, create_access_token
    from sqlalchemy import select
    token = (data.get("refresh_token") or "").strip()
    jti, family = jti_and_family(token)
    if not jti:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    rec = (await db.execute(select(RefreshToken).where(RefreshToken.token_jti_hash == hash_jti(jti)))).scalars().first()
    if not rec:
        raise HTTPException(status_code=401, detail="Unknown refresh token")
    if rec.revoked_at is not None:
        # Reuse detection: revoke whole family.
        await _revoke_family(db, rec.token_family, "reuse_detected")
        raise HTTPException(status_code=401, detail="Refresh token was revoked")
    if rec.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")
    user = await db.get(User, rec.user_id)
    if not user or not user.is_active:
        await _revoke_family(db, rec.token_family, "user_disabled")
        raise HTTPException(status_code=401, detail="User disabled")
    # Rotate: revoke old, issue new in same family
    rec.revoked_at = datetime.now(timezone.utc)
    rec.revoke_reason = "rotated"
    new_refresh = await _issue_refresh(db, user.id, family=rec.token_family)
    rec.replaced_by = jti  # replaced by the new jti (recorded as raw jti; storage uses hash)
    await db.commit()
    new_access = create_access_token(user.id)
    return {"access_token": new_access, "refresh_token": new_refresh}


@router.post("/logout")
async def logout(data: dict = None, credentials=Depends(security), db: AsyncSession = Depends(get_db)):
    """Revoke the presented refresh token family (durable)."""
    from app.core.security import jti_and_family
    rt = ((data or {}).get("refresh_token") or "").strip()
    if rt:
        _, family = jti_and_family(rt)
        if family:
            await _revoke_family(db, family, "logout")
    from app.services.governance import get_governance_service
    user = await get_current_user(credentials, db)
    await get_governance_service().audit(db, user.id, "auth_logout", "user", str(user.id), reason="logout")
    return {"status": "logged_out"}


@router.get("/me")
async def me(credentials=Depends(security), db: AsyncSession = Depends(get_db)):
    """Return the current authenticated user."""
    user = await get_current_user(credentials, db)
    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}/role")
async def set_user_role(user_id: str, data: dict, credentials=Depends(security), db: AsyncSession = Depends(get_db)):
    """Grant REVIEWER/ADMIN role. Only system_admin may do this (C6.3 Gate 0)."""
    from app.services.governance import get_governance_service
    actor = await get_current_user(credentials, db)
    gov = get_governance_service()
    if not gov.is_system_admin(actor):
        raise HTTPException(status_code=403, detail="only system_admin can grant roles")
    target = await db.get(User, uuid.UUID(user_id))
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    role = (data.get("role") or "").strip()
    if role not in ("admin", "reviewer"):
        raise HTTPException(status_code=400, detail="only admin/reviewer roles are grantable")
    target.role = role
    await db.commit()
    await gov.audit(db, actor.id, "role_granted", "user", user_id, reason=f"granted {role}",
                    actor_label=actor.name)
    return {"status": "ok", "user_id": user_id, "role": role}
