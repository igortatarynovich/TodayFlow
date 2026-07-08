"""OAuth authentication endpoints (Google, Apple)."""

from __future__ import annotations

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services import auth as auth_service

router = APIRouter(prefix="/oauth", tags=["oauth"])

GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
GOOGLE_ALLOWED_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
APPLE_ISSUER = "https://appleid.apple.com"

google_jwk_client = jwt.PyJWKClient(GOOGLE_JWKS_URL)
apple_jwk_client = jwt.PyJWKClient(APPLE_JWKS_URL)


class GoogleOAuthPayload(BaseModel):
    id_token: str
    access_token: str | None = None


class AppleOAuthPayload(BaseModel):
    identity_token: str
    authorization_code: str | None = None
    user: dict | None = None  # Apple user info (email, name)


def _verify_google_id_token(id_token: str) -> dict:
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")

    signing_key = google_jwk_client.get_signing_key_from_jwt(id_token)
    decoded = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.google_client_id,
        options={"require": ["exp", "iat", "sub"]},
    )
    issuer = decoded.get("iss")
    if issuer not in GOOGLE_ALLOWED_ISSUERS:
        raise jwt.InvalidIssuerError("Invalid Google token issuer")
    return decoded


def _verify_apple_identity_token(identity_token: str) -> dict:
    if not settings.apple_client_id:
        raise HTTPException(status_code=503, detail="Apple OAuth is not configured")

    signing_key = apple_jwk_client.get_signing_key_from_jwt(identity_token)
    return jwt.decode(
        identity_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.apple_client_id,
        issuer=APPLE_ISSUER,
        options={"require": ["exp", "iat", "sub"]},
    )


@router.post("/google")
async def google_oauth(
    request: Request,
    payload: GoogleOAuthPayload,
    db: Session = Depends(get_session),
) -> dict:
    """Authenticate user with Google OAuth."""
    locale = request_locale(request)

    try:
        decoded = _verify_google_id_token(payload.id_token)
    except HTTPException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=translate("oauth.google.error", locale=locale, default=exc.detail),
        ) from exc
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=400,
            detail=translate("oauth.google.invalidToken", locale=locale, default="Invalid Google token"),
        ) from None
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=translate("oauth.google.error", locale=locale, default=f"Google authentication failed: {exc}"),
        ) from exc

    email = decoded.get("email")
    if not email:
        raise HTTPException(
            status_code=400,
            detail=translate("oauth.google.noEmail", locale=locale, default="Email not provided by Google"),
        )

    user = db.query(db_models.User).filter_by(email=email).first()
    is_new_user = False
    if not user:
        user = db_models.User(
            email=email,
            password_hash=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new_user = True

    token = auth_service.create_token(user.id, is_admin=user.is_admin)
    return {
        "user_id": user.id,
        "email": user.email,
        "is_paid": user.is_paid,
        "token": token,
        "is_new_user": is_new_user,
    }


@router.post("/apple")
async def apple_oauth(
    request: Request,
    payload: AppleOAuthPayload,
    db: Session = Depends(get_session),
) -> dict:
    """Authenticate user with Apple Sign In."""
    locale = request_locale(request)

    try:
        decoded = _verify_apple_identity_token(payload.identity_token)
    except HTTPException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=translate("oauth.apple.error", locale=locale, default=exc.detail),
        ) from exc
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=400,
            detail=translate("oauth.apple.invalidToken", locale=locale, default="Invalid Apple token"),
        ) from None
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=translate("oauth.apple.error", locale=locale, default=f"Apple authentication failed: {exc}"),
        ) from exc

    email = decoded.get("email")
    if not email and payload.user:
        email = payload.user.get("email")

    if not email:
        raise HTTPException(
            status_code=400,
            detail=translate("oauth.apple.noEmail", locale=locale, default="Email not provided by Apple"),
        )

    user = db.query(db_models.User).filter_by(email=email).first()
    is_new_user = False
    if not user:
        user = db_models.User(
            email=email,
            password_hash=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new_user = True

    token = auth_service.create_token(user.id, is_admin=user.is_admin)
    return {
        "user_id": user.id,
        "email": user.email,
        "is_paid": user.is_paid,
        "token": token,
        "is_new_user": is_new_user,
    }


@router.get("/providers")
async def get_oauth_providers() -> dict:
    """Get available OAuth providers and their configuration."""
    providers = {}

    if settings.google_client_id:
        providers["google"] = {
            "client_id": settings.google_client_id,
            "enabled": True,
        }
    else:
        providers["google"] = {"enabled": False}

    if settings.apple_client_id:
        providers["apple"] = {
            "client_id": settings.apple_client_id,
            "enabled": True,
        }
    else:
        providers["apple"] = {"enabled": False}

    return {"providers": providers}
