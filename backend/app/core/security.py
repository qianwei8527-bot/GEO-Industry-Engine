import uuid
from datetime import datetime, timedelta
import bcrypt
from jose import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False

import hashlib


def create_refresh_token(user_id: uuid.UUID, family: str = None, jti: str = None,
                         expires_delta: timedelta | None = None) -> str:
    to_encode = {"sub": str(user_id), "type": "refresh",
                 "jti": jti or str(uuid.uuid4()), "family": family or str(uuid.uuid4())}
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode()).hexdigest()


def jti_and_family(token: str):
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return None, None
    return payload.get("jti"), payload.get("family")


def create_access_token(user_id: uuid.UUID, expires_delta: timedelta | None = None) -> str:
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except:
        return None
