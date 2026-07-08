"""Authentication endpoints (placeholder email/password flow)."""

from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.services.insight_depth import billing_to_insight_depth
from todayflow_backend.services.subscription_level import get_subscription_snapshot
from todayflow_backend.db.session import get_session
from todayflow_backend.services import auth as auth_service
from todayflow_backend.services.email import send_password_reset_email
from todayflow_backend.i18n import request_locale, translate

router = APIRouter(prefix="/auth", tags=["auth"])
auth_scheme = HTTPBearer(auto_error=False)


class SignupPayload(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordPayload(BaseModel):
    email: EmailStr


class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str


class ChangePasswordPayload(BaseModel):
    current_password: str
    new_password: str


def _validate_new_password(password: str, *, locale: str) -> None:
    if len(password or "") < 8:
        raise HTTPException(
            status_code=400,
            detail=translate("auth.errors.passwordMinLength", locale=locale, default="Password must contain at least 8 characters"),
        )


@router.post("/signup")
def signup(payload: SignupPayload, request: Request, db: Session = Depends(get_session)) -> dict:
    # Rate limiting will be handled by middleware
    locale = request_locale(request)
    _validate_new_password(payload.password, locale=locale)
    existing = db.query(db_models.User).filter_by(email=payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail=translate("auth.errors.exists", locale=locale))

    user = db_models.User(
        email=payload.email,
        password_hash=auth_service.hash_password(payload.password),
        is_admin=payload.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth_service.create_token(user.id, is_admin=user.is_admin)
    return {"user_id": user.id, "email": user.email, "token": token}


@router.post("/login")
def login(payload: LoginPayload, request: Request, db: Session = Depends(get_session)) -> dict:
    locale = request_locale(request)
    user = db.query(db_models.User).filter_by(email=payload.email).first()
    if not user or not auth_service.verify_password(payload.password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail=translate("auth.errors.invalidCredentials", locale=locale))
    token = auth_service.create_token(user.id, is_admin=user.is_admin)
    return {"user_id": user.id, "email": user.email, "is_paid": user.is_paid, "token": token}


def require_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_session),
) -> db_models.User:
    locale = request_locale(request)
    if credentials is None:
        raise HTTPException(status_code=401, detail=translate("auth.errors.missingCredentials", locale=locale))
    try:
        payload = auth_service.decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail=translate("auth.errors.tokenExpired", locale=locale)) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=translate("auth.errors.invalidToken", locale=locale)) from exc
    user = db.query(db_models.User).filter_by(id=int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail=translate("auth.errors.invalidToken", locale=locale))
    return user


def require_admin(
    request: Request,
    user: db_models.User = Depends(require_user),
) -> db_models.User:
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail=translate("auth.errors.adminRequired", locale=request_locale(request))
        )
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_session),
) -> db_models.User | None:
    if credentials is None:
        return None
    try:
        payload = auth_service.decode_token(credentials.credentials)
    except jwt.PyJWTError:
        return None
    return db.query(db_models.User).filter_by(id=int(payload["sub"])).first()


@router.get("/me")
def get_current_user_profile(
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
) -> dict:
    lite_exists = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id, product_type="lite")
        .order_by(db_models.GeneratedReport.created_at.desc())
        .first()
        is not None
    )
    full_exists = (
        db.query(db_models.GeneratedReport)
        .filter_by(user_id=user.id, product_type="full")
        .order_by(db_models.GeneratedReport.created_at.desc())
        .first()
        is not None
    )
    sub_snap = get_subscription_snapshot(user, db)
    return {
        "user_id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_paid": user.is_paid,
        "has_lite_report": lite_exists,
        "has_full_report": full_exists,
        "subscription_level": sub_snap.level,
        "active_plan_id": sub_snap.active_plan_id,
        "subscription_status": sub_snap.subscription_status,
        "insight_depth_tier": billing_to_insight_depth(sub_snap.level),
    }


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordPayload, request: Request, db: Session = Depends(get_session)) -> dict:
    """Request password reset. Always returns success to prevent email enumeration."""
    locale = request_locale(request)
    user = db.query(db_models.User).filter_by(email=payload.email).first()
    
    # Always return success to prevent email enumeration
    if user:
        # Generate reset token
        token = db_models.PasswordResetToken.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)  # Token valid for 24 hours
        
        reset_token = db_models.PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(reset_token)
        db.commit()
        
        base_url = settings.frontend_app_url or str(request.base_url).rstrip("/")
        reset_url = f"{base_url}/auth/reset-password?token={token}"
        send_password_reset_email(user.email, reset_url)
    
    return {
        "message": translate("auth.forgotPassword.success", locale=locale, default="If an account with this email exists, a password reset link has been sent.")
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordPayload, request: Request, db: Session = Depends(get_session)) -> dict:
    """Reset password using token."""
    locale = request_locale(request)
    _validate_new_password(payload.new_password, locale=locale)
    
    # Find valid token
    reset_token = (
        db.query(db_models.PasswordResetToken)
        .filter_by(token=payload.token)
        .filter(db_models.PasswordResetToken.used_at.is_(None))
        .first()
    )
    
    if not reset_token or not reset_token.is_valid():
        raise HTTPException(
            status_code=400,
            detail=translate("auth.resetPassword.invalidToken", locale=locale, default="Invalid or expired reset token")
        )
    
    # Update user password
    user = db.query(db_models.User).filter_by(id=reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=translate("auth.resetPassword.userNotFound", locale=locale, default="User not found")
        )
    
    user.password_hash = auth_service.hash_password(payload.new_password)
    
    # Mark token as used
    reset_token.used_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": translate("auth.resetPassword.success", locale=locale, default="Password has been reset successfully")
    }


@router.post("/change-password")
def change_password(
    payload: ChangePasswordPayload,
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
) -> dict:
    locale = request_locale(request)
    _validate_new_password(payload.new_password, locale=locale)

    if not user.password_hash:
        raise HTTPException(
            status_code=400,
            detail=translate(
                "auth.changePassword.unavailable",
                locale=locale,
                default="Password change is unavailable for this account. Use password recovery instead.",
            ),
        )

    if not auth_service.verify_password(payload.current_password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail=translate(
                "auth.errors.invalidCredentials",
                locale=locale,
                default="Invalid email or password",
            ),
        )

    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=400,
            detail=translate(
                "auth.changePassword.samePassword",
                locale=locale,
                default="New password must differ from the current password",
            ),
        )

    user.password_hash = auth_service.hash_password(payload.new_password)

    (
        db.query(db_models.PasswordResetToken)
        .filter(db_models.PasswordResetToken.user_id == user.id)
        .filter(db_models.PasswordResetToken.used_at.is_(None))
        .update({"used_at": datetime.utcnow()}, synchronize_session=False)
    )

    db.add(user)
    db.commit()

    return {
        "message": translate(
            "auth.changePassword.success",
            locale=locale,
            default="Password changed successfully",
        )
    }
