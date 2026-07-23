"""Authentication helpers (password hashing + JWT access + opaque refresh)."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import utc_naive_now

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Access JWT — short-lived. Refresh — opaque, long-lived (see contract).
ACCESS_TOKEN_TTL_MINUTES = 60
REFRESH_TTL_DAYS_STAY = 90
REFRESH_TTL_DAYS_SESSION = 1


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(user_id: int, is_admin: bool = False, expires_in_minutes: int = ACCESS_TOKEN_TTL_MINUTES) -> str:
    """Create short-lived access JWT (legacy name kept for call-site compatibility)."""
    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "typ": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
    }
    return jwt.encode(payload, settings.auth_jwt_secret, algorithm=settings.auth_jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.auth_jwt_secret, algorithms=[settings.auth_jwt_algorithm])


def _hash_refresh(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _stay_logged_in(db: Session, user_id: int) -> bool:
    settings_row = (
        db.query(db_models.UserSettings)
        .filter(db_models.UserSettings.user_id == user_id)
        .first()
    )
    if settings_row is None:
        return True
    return bool(settings_row.stay_logged_in if settings_row.stay_logged_in is not None else True)


def _refresh_ttl_days(stay: bool) -> int:
    return REFRESH_TTL_DAYS_STAY if stay else REFRESH_TTL_DAYS_SESSION


def issue_refresh_token(
    db: Session,
    *,
    user_id: int,
    device_label: str | None = None,
    stay_logged_in: bool | None = None,
) -> str:
    """Create and persist a new refresh token; returns plaintext once."""
    stay = _stay_logged_in(db, user_id) if stay_logged_in is None else stay_logged_in
    raw = secrets.token_urlsafe(48)
    row = db_models.RefreshToken(
        user_id=user_id,
        token_hash=_hash_refresh(raw),
        device_label=(device_label or None),
        expires_at=utc_naive_now() + timedelta(days=_refresh_ttl_days(stay)),
    )
    db.add(row)
    db.commit()
    return raw


def revoke_refresh_token(db: Session, raw_token: str) -> bool:
    th = _hash_refresh((raw_token or "").strip())
    if not th:
        return False
    row = (
        db.query(db_models.RefreshToken)
        .filter(db_models.RefreshToken.token_hash == th)
        .filter(db_models.RefreshToken.revoked_at.is_(None))
        .first()
    )
    if row is None:
        return False
    row.revoked_at = utc_naive_now()
    db.add(row)
    db.commit()
    return True


def revoke_all_refresh_tokens(db: Session, user_id: int) -> int:
    now = utc_naive_now()
    q = (
        db.query(db_models.RefreshToken)
        .filter(db_models.RefreshToken.user_id == user_id)
        .filter(db_models.RefreshToken.revoked_at.is_(None))
    )
    count = 0
    for row in q.all():
        row.revoked_at = now
        db.add(row)
        count += 1
    if count:
        db.commit()
    return count


def rotate_refresh_token(
    db: Session,
    *,
    raw_token: str,
    device_label: str | None = None,
) -> tuple[db_models.User, str]:
    """Validate refresh, revoke it, issue a new one (rotation). Returns (user, new_raw)."""
    th = _hash_refresh((raw_token or "").strip())
    if not th:
        raise ValueError("invalid_refresh")
    row = (
        db.query(db_models.RefreshToken)
        .filter(db_models.RefreshToken.token_hash == th)
        .first()
    )
    if row is None or row.revoked_at is not None:
        raise ValueError("invalid_refresh")
    if row.expires_at <= utc_naive_now():
        row.revoked_at = utc_naive_now()
        db.add(row)
        db.commit()
        raise ValueError("expired_refresh")

    user = db.query(db_models.User).filter_by(id=row.user_id).first()
    if user is None:
        raise ValueError("invalid_refresh")

    row.revoked_at = utc_naive_now()
    row.last_used_at = utc_naive_now()
    db.add(row)
    db.commit()

    new_raw = issue_refresh_token(
        db,
        user_id=user.id,
        device_label=device_label or row.device_label,
    )
    return user, new_raw


def issue_token_pair(
    db: Session,
    user: db_models.User,
    *,
    device_label: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Standard auth response for web + mobile clients."""
    access = create_token(user.id, is_admin=user.is_admin)
    refresh = issue_refresh_token(db, user_id=user.id, device_label=device_label)
    body: dict[str, Any] = {
        "user_id": user.id,
        "email": user.email,
        "access_token": access,
        "refresh_token": refresh,
        "expires_in": ACCESS_TOKEN_TTL_MINUTES * 60,
        "token_type": "bearer",
        # Legacy alias
        "token": access,
        "is_paid": bool(user.is_paid),
    }
    if extra:
        body.update(extra)
    return body
