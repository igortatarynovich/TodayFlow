"""Account profile and stored astro-data endpoints."""

from __future__ import annotations

import math
import os
import unicodedata
from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user
from todayflow_backend.api.reports import try_warm_natal_chart_cache_for_profile
from todayflow_backend.core import models as api_models
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.core_profile import CoreProfileService, get_core_profile_service
from todayflow_backend.services.geocode import Geocoder
from todayflow_backend.services import astro as astro_service_mod
from todayflow_backend.services.numerology import NumerologyError, NumerologyService, get_numerology_service

router = APIRouter(prefix="/account", tags=["account"])

ALLOWED_ASTRO_PROFILE_RELATIONS = {"self", "partner", "child", "close_person"}

# Сколько раз можно поменять дату/время/место рождения после создания профиля (уточнения, а не бесконечные правки).
MAX_ASTRO_BIRTH_FACTS_CORRECTIONS = 3

# Минимальный интервал между изменениями фактов рождения (сек). 0 = выключено (тесты / отладка).
ASTRO_BIRTH_FACTS_COOLDOWN_SECONDS = int(os.environ.get("ASTRO_BIRTH_FACTS_COOLDOWN_SECONDS", "86400"))


def _birth_facts_corrections_meta(profile: db_models.AstroProfile) -> dict[str, int]:
    used = int(getattr(profile, "birth_facts_correction_count", 0) or 0)
    mx = MAX_ASTRO_BIRTH_FACTS_CORRECTIONS
    return {
        "birth_facts_corrections_used": used,
        "birth_facts_corrections_max": mx,
        "birth_facts_corrections_remaining": max(0, mx - used),
    }


def _birth_facts_snapshot_tuple(
    birth_date: date,
    birth_time: time | None,
    time_unknown: bool,
    timezone_offset_minutes: int | None,
    timezone_name: str | None,
    location_name: str | None,
    latitude: float | None,
    longitude: float | None,
) -> tuple:
    lat = latitude
    lon = longitude
    return (
        birth_date.isoformat(),
        birth_time.isoformat() if birth_time else None,
        bool(time_unknown),
        timezone_offset_minutes,
        (timezone_name or "").strip().lower() or None,
        (location_name or "").strip().lower() or None,
        round(float(lat), 6) if lat is not None else None,
        round(float(lon), 6) if lon is not None else None,
    )


def _birth_facts_snapshot_from_profile(profile: db_models.AstroProfile) -> tuple:
    return _birth_facts_snapshot_tuple(
        profile.birth_date,
        profile.birth_time,
        bool(profile.time_unknown),
        profile.timezone_offset_minutes,
        profile.timezone_name,
        profile.location_name,
        profile.latitude,
        profile.longitude,
    )


def _birth_facts_cooldown_remaining_seconds(profile: db_models.AstroProfile) -> int:
    last = getattr(profile, "birth_facts_last_changed_at", None)
    if last is None:
        return 0
    cooldown = ASTRO_BIRTH_FACTS_COOLDOWN_SECONDS
    if cooldown <= 0:
        return 0
    elapsed = (datetime.utcnow() - last).total_seconds()
    return max(0, int(math.ceil(cooldown - elapsed)))


def _birth_facts_cooldown_meta(profile: db_models.AstroProfile) -> dict[str, int]:
    return {"birth_facts_cooldown_remaining_seconds": _birth_facts_cooldown_remaining_seconds(profile)}


def _settings_or_create(db: Session, user: db_models.User) -> db_models.UserSettings:
    settings = (
        db.query(db_models.UserSettings)
        .filter(db_models.UserSettings.user_id == user.id)
        .first()
    )
    if settings is None:
        settings = db_models.UserSettings(user_id=user.id, subscriptions=[])
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def _settings_payload(settings: db_models.UserSettings, user: db_models.User) -> dict:
    return {
        "email": user.email,
        "greeting": settings.greeting,
        "first_name": settings.first_name,
        "last_name": settings.last_name,
        "country": settings.country,
        "language": settings.language,
        "locale": settings.locale,
        "stay_logged_in": settings.stay_logged_in,
        "newsletter_opt_in": settings.newsletter_opt_in,
        "push_opt_in": settings.push_opt_in,
        "subscriptions": settings.subscriptions or [],
        "astrology_level": getattr(settings, "astrology_level", "beginner") or "beginner",
        "text_preference": getattr(settings, "text_preference", "detailed") or "detailed",
    }


class ProfileUpdatePayload(BaseModel):
    email: Optional[EmailStr] = None
    greeting: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None
    stay_logged_in: Optional[bool] = None
    newsletter_opt_in: Optional[bool] = None
    push_opt_in: Optional[bool] = None
    subscriptions: Optional[list[str]] = None
    astrology_level: Optional[str] = None  # 'beginner', 'intermediate', 'advanced'
    text_preference: Optional[str] = None  # 'brief', 'detailed', 'comprehensive'


class CoreProfileResponse(BaseModel):
    profile_version: str
    generated_at: str
    is_ready: bool
    missing_fields: list[str]
    profile_hash: str
    person: dict
    astro: dict
    numerology: dict
    baseline: dict
    profiles: dict | None = None
    interpretation: dict | None = None
    daily_interpretation: dict | None = None
    living: dict | None = None
    natal_summary: dict | None = None  # сжатое текстовое резюме карты для персонализации (без сырых координат)


class CoreSetupPayload(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    label: str = "Я"
    birth_date: date
    birth_time: Optional[time] = None
    time_unknown: bool = False
    timezone_offset_minutes: Optional[int] = None
    timezone_name: Optional[str] = None
    location_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class CoreSetupResponse(BaseModel):
    status: str
    core_profile: CoreProfileResponse
    astro_profile: dict
    numerology_profile: dict


class AstroProfileSaveResponse(BaseModel):
    """Ответ POST/PUT /account/astro-data и POST .../astro-data/{id}/primary: строка профиля + актуальный core (как GET /account/core-profile для выбранного контекста)."""

    id: int
    label: str | None = None
    relation: str | None = None
    birth_date: str
    birth_time: str | None = None
    time_unknown: bool
    timezone_offset_minutes: int | None = None
    timezone_name: str | None = None
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    is_primary: bool
    created_at: str | None = None
    birth_facts_corrections_used: int
    birth_facts_corrections_max: int
    birth_facts_corrections_remaining: int
    birth_facts_cooldown_remaining_seconds: int
    core_profile: CoreProfileResponse


class ProfileSummaryResponse(BaseModel):
    generated_at: str
    profile_hash: str
    is_ready: bool
    missing_fields: list[str]
    display_name: str | None
    core_trio: dict
    baseline: dict
    rings_preview: dict
    living_summary: str | None = None


class ProfileBuildStatusResponse(BaseModel):
    status: str
    is_ready: bool
    profile_hash: str
    generated_at: str
    missing_fields: list[str]
    has_snapshot: bool


@router.get("/profile")
def get_profile(
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
) -> dict:
    settings = _settings_or_create(db, user)
    return _settings_payload(settings, user)


@router.put("/profile")
def update_profile(
    payload: ProfileUpdatePayload,
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
) -> dict:
    locale = request_locale(request)
    settings = _settings_or_create(db, user)

    if payload.email and payload.email != user.email:
        existing = db.query(db_models.User).filter(db_models.User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail=translate("account.errors.emailTaken", locale=locale))
        user.email = payload.email

    for field in [
        "greeting",
        "first_name",
        "last_name",
        "country",
        "language",
        "locale",
        "stay_logged_in",
        "newsletter_opt_in",
        "push_opt_in",
        "astrology_level",
        "text_preference",
    ]:
        value = getattr(payload, field)
        if value is not None:
            # Validate astrology_level and text_preference
            if field == "astrology_level" and value not in ["beginner", "intermediate", "advanced"]:
                raise HTTPException(
                    status_code=400,
                    detail=translate("account.errors.invalidAstrologyLevel", locale=locale, default="Invalid astrology level. Must be 'beginner', 'intermediate', or 'advanced'.")
                )
            if field == "text_preference" and value not in ["brief", "detailed", "comprehensive"]:
                raise HTTPException(
                    status_code=400,
                    detail=translate("account.errors.invalidTextPreference", locale=locale, default="Invalid text preference. Must be 'brief', 'detailed', or 'comprehensive'.")
                )
            setattr(settings, field, value)

    if payload.subscriptions is not None:
        settings.subscriptions = payload.subscriptions

    db.add(user)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return _settings_payload(settings, user)


@router.get("/core-profile", response_model=CoreProfileResponse)
def get_core_profile(
    astro_profile_id: Optional[int] = None,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    service: CoreProfileService = Depends(get_core_profile_service),
) -> CoreProfileResponse:
    return CoreProfileResponse(**service.build(db, user, astro_profile_id=astro_profile_id))


@router.get("/profile-summary", response_model=ProfileSummaryResponse)
def get_profile_summary(
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    service: CoreProfileService = Depends(get_core_profile_service),
) -> ProfileSummaryResponse:
    core = service.build(db, user)
    astro = core.get("astro") or {}
    numerology = core.get("numerology") or {}
    baseline = core.get("baseline") or {}
    person = core.get("person") or {}
    living = core.get("living") or {}

    core_trio = {
        "sun_sign": astro.get("sun_sign"),
        "birth_time_known": not bool(astro.get("time_unknown")) if astro.get("birth_date") else None,
        "life_path": numerology.get("life_path"),
    }
    # Preview-only placeholder before full Meaning Rings snapshot wiring in frontend runtime.
    rings_preview = {
        "Mind": 0,
        "Body": 0,
        "Love": 0,
        "Wealth": 0,
        "Purpose": 0,
        "Energy": 0,
    }

    return ProfileSummaryResponse(
        generated_at=str(core.get("generated_at") or ""),
        profile_hash=str(core.get("profile_hash") or ""),
        is_ready=bool(core.get("is_ready")),
        missing_fields=list(core.get("missing_fields") or []),
        display_name=person.get("display_name"),
        core_trio=core_trio,
        baseline=baseline,
        rings_preview=rings_preview,
        living_summary=living.get("summary") if isinstance(living, dict) else None,
    )


@router.get("/profile-build-status", response_model=ProfileBuildStatusResponse)
def get_profile_build_status(
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    service: CoreProfileService = Depends(get_core_profile_service),
) -> ProfileBuildStatusResponse:
    core = service.build(db, user)
    profile_hash = str(core.get("profile_hash") or "")
    has_snapshot = False
    if profile_hash:
        has_snapshot = (
            db.query(db_models.CoreProfileSnapshot.id)
            .filter(
                db_models.CoreProfileSnapshot.user_id == user.id,
                db_models.CoreProfileSnapshot.profile_hash == profile_hash,
            )
            .first()
            is not None
        )
    is_ready = bool(core.get("is_ready"))
    status = "ready" if is_ready else ("building" if has_snapshot else "queued")

    return ProfileBuildStatusResponse(
        status=status,
        is_ready=is_ready,
        profile_hash=profile_hash,
        generated_at=str(core.get("generated_at") or ""),
        missing_fields=list(core.get("missing_fields") or []),
        has_snapshot=has_snapshot,
    )


class AstroProfilePayload(BaseModel):
    label: str
    relation: Optional[str] = None
    birth_date: date
    birth_time: Optional[time] = None
    time_unknown: bool = False
    timezone_offset_minutes: Optional[int] = None
    timezone_name: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None
    is_primary: bool = False


class AstroProfileUpdatePayload(BaseModel):
    label: Optional[str] = None
    relation: Optional[str] = None
    birth_date: Optional[date] = None
    birth_time: Optional[time] = None
    time_unknown: Optional[bool] = None
    timezone_offset_minutes: Optional[int] = None
    timezone_name: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None
    is_primary: Optional[bool] = None


def _normalize_relation(value: str | None, *, is_primary: bool = False) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in ALLOWED_ASTRO_PROFILE_RELATIONS:
        return "self" if is_primary else "close_person"
    return normalized


def _astro_profile_to_dict(profile: db_models.AstroProfile) -> dict:
    return {
        "id": profile.id,
        "label": profile.label,
        "relation": _normalize_relation(profile.relation, is_primary=profile.is_primary),
        "birth_date": profile.birth_date.isoformat(),
        "birth_time": profile.birth_time.isoformat() if profile.birth_time else None,
        "time_unknown": profile.time_unknown,
        "timezone_offset_minutes": profile.timezone_offset_minutes,
        "timezone_name": profile.timezone_name,
        "location_name": profile.location_name,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "notes": profile.notes,
        "is_primary": profile.is_primary,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        **_birth_facts_corrections_meta(profile),
        **_birth_facts_cooldown_meta(profile),
    }


def _astro_profile_save_response(
    *,
    profile: db_models.AstroProfile,
    core_profile_service: CoreProfileService,
    db: Session,
    user: db_models.User,
) -> AstroProfileSaveResponse:
    """Для основного профиля — тот же контекст, что GET /core-profile без query; для вторичного — с astro_profile_id как у GET с этим id."""
    astro_profile_id = None if profile.is_primary else profile.id
    core = core_profile_service.build(db, user, astro_profile_id=astro_profile_id)
    merged = {**_astro_profile_to_dict(profile), "core_profile": CoreProfileResponse(**core)}
    return AstroProfileSaveResponse(**merged)


def _get_max_profiles(user: db_models.User, db: Session) -> int:
    """Определяет максимальное количество профилей в зависимости от подписки."""
    # Проверяем активные подписки
    active_subscriptions = (
        db.query(db_models.Subscription)
        .filter(
            db_models.Subscription.user_id == user.id,
            db_models.Subscription.status == "active"
        )
        .all()
    )
    
    # Если есть активная подписка Pro или Plus
    for sub in active_subscriptions:
        if sub.plan_id in ["pro", "plus", "full_access"]:
            return 10  # Pro/Plus: до 10 профилей
        elif sub.plan_id in ["lite_plus"]:
            return 3  # Lite Plus: до 3 профилей
    
    # Если пользователь платный (legacy)
    if user.is_paid:
        return 5
    
    # Бесплатный план: только 1 профиль
    return 1


def _get_primary_profile(user: db_models.User, db: Session) -> db_models.AstroProfile | None:
    primary = (
        db.query(db_models.AstroProfile)
        .filter(db_models.AstroProfile.user_id == user.id, db_models.AstroProfile.is_primary.is_(True))
        .first()
    )
    if primary:
        return primary
    return (
        db.query(db_models.AstroProfile)
        .filter(db_models.AstroProfile.user_id == user.id)
        .order_by(db_models.AstroProfile.created_at.asc())
        .first()
    )


def _resolve_coordinates(
    geocoder: Geocoder,
    location_name: str | None,
    latitude: float | None,
    longitude: float | None,
) -> tuple[float | None, float | None]:
    if latitude is not None and longitude is not None:
        return latitude, longitude
    geo = geocoder.lookup(location_name)
    if geo:
        return float(geo["latitude"]), float(geo["longitude"])
    return latitude, longitude


def _normalize_numerology_name(value: str) -> str:
    translit = str.maketrans({
        "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ё": "E", "Ж": "ZH", "З": "Z",
        "И": "I", "Й": "I", "К": "K", "Л": "L", "М": "M", "Н": "N", "О": "O", "П": "P", "Р": "R",
        "С": "S", "Т": "T", "У": "U", "Ф": "F", "Х": "H", "Ц": "TS", "Ч": "CH", "Ш": "SH", "Щ": "SH",
        "Ъ": "", "Ы": "Y", "Ь": "", "Э": "E", "Ю": "YU", "Я": "YA",
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z",
        "и": "i", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
        "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
        "І": "I", "і": "i", "Ї": "I", "ї": "i", "Є": "E", "є": "e",
    })
    converted = (value or "").translate(translit)
    normalized = unicodedata.normalize("NFKD", converted)
    normalized = "".join(ch for ch in normalized if ch.isalpha() or ch in {" ", "-"})
    return " ".join(normalized.split())


def _ensure_primary(db: Session, user: db_models.User, new_primary_id: Optional[int] = None) -> None:
    if new_primary_id is None:
        return
    db.query(db_models.AstroProfile).filter(
        db_models.AstroProfile.user_id == user.id, db_models.AstroProfile.id != new_primary_id
    ).update({db_models.AstroProfile.is_primary: False}, synchronize_session=False)
    # «self» допустимо только у основного профиля; иначе в ответе API остаётся self.
    db.query(db_models.AstroProfile).filter(
        db_models.AstroProfile.user_id == user.id,
        db_models.AstroProfile.id != new_primary_id,
        func.lower(db_models.AstroProfile.relation) == "self",
    ).update({db_models.AstroProfile.relation: "close_person"}, synchronize_session=False)


@router.get("/astro-data")
def list_astro_profiles(
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
) -> dict:
    profiles = (
        db.query(db_models.AstroProfile)
        .filter(db_models.AstroProfile.user_id == user.id)
        .order_by(db_models.AstroProfile.created_at.asc())
        .all()
    )
    max_profiles = _get_max_profiles(user, db)
    return {
        "profiles": [_astro_profile_to_dict(p) for p in profiles],
        "max_profiles": max_profiles,
        "current_count": len(profiles),
        "can_create_more": len(profiles) < max_profiles
    }


@router.post("/astro-data", response_model=AstroProfileSaveResponse)
async def create_astro_profile(
    payload: AstroProfilePayload,
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
    astro_service: astro_service_mod.AstroService = Depends(lambda: astro_service_mod.AstroService()),
) -> AstroProfileSaveResponse:
    locale = request_locale(request)
    
    # Проверяем лимит профилей
    existing_profiles = (
        db.query(db_models.AstroProfile)
        .filter(db_models.AstroProfile.user_id == user.id)
        .count()
    )
    
    max_profiles = _get_max_profiles(user, db)
    if existing_profiles >= max_profiles:
        raise HTTPException(
            status_code=403,
            detail=translate(
                "account.errors.maxProfilesReached",
                locale=locale,
                default=f"Maximum {max_profiles} profile(s) allowed. Upgrade your subscription to create more profiles."
            )
        )
    
    latitude, longitude = _resolve_coordinates(
        geocoder,
        payload.location_name,
        payload.latitude,
        payload.longitude,
    )
    profile = db_models.AstroProfile(
        user_id=user.id,
        label=payload.label,
        relation=_normalize_relation(payload.relation, is_primary=payload.is_primary),
        birth_date=payload.birth_date,
        birth_time=payload.birth_time,
        time_unknown=payload.time_unknown,
        timezone_offset_minutes=payload.timezone_offset_minutes,
        timezone_name=payload.timezone_name,
        location_name=payload.location_name,
        latitude=latitude,
        longitude=longitude,
        notes=payload.notes,
        is_primary=payload.is_primary,
    )
    db.add(profile)
    db.commit()
    if payload.is_primary:
        _ensure_primary(db, user, profile.id)
        db.commit()
    db.refresh(profile)

    await try_warm_natal_chart_cache_for_profile(
        db, profile, geocoder, locale, astro_service=astro_service
    )
    db.refresh(profile)

    return _astro_profile_save_response(
        profile=profile,
        core_profile_service=core_profile_service,
        db=db,
        user=user,
    )


@router.post("/core-setup", response_model=CoreSetupResponse)
async def upsert_core_setup(
    payload: CoreSetupPayload,
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    numerology_service: NumerologyService = Depends(get_numerology_service),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
    astro_service: astro_service_mod.AstroService = Depends(lambda: astro_service_mod.AstroService()),
) -> CoreSetupResponse:
    locale = request_locale(request)
    settings = _settings_or_create(db, user)

    settings.first_name = payload.first_name.strip()
    settings.last_name = (payload.last_name or "").strip() or None
    db.add(settings)

    latitude, longitude = _resolve_coordinates(
        geocoder,
        payload.location_name,
        payload.latitude,
        payload.longitude,
    )

    primary = _get_primary_profile(user, db)
    if primary is None:
        primary = db_models.AstroProfile(
            user_id=user.id,
            label=payload.label.strip() or "Я",
            relation="self",
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            time_unknown=payload.time_unknown,
            timezone_offset_minutes=payload.timezone_offset_minutes,
            timezone_name=payload.timezone_name,
            location_name=payload.location_name.strip(),
            latitude=latitude,
            longitude=longitude,
            notes=payload.notes,
            is_primary=True,
        )
        db.add(primary)
    else:
        snapshot_before = _birth_facts_snapshot_from_profile(primary)
        snapshot_proposed = _birth_facts_snapshot_tuple(
            payload.birth_date,
            payload.birth_time,
            payload.time_unknown,
            payload.timezone_offset_minutes,
            payload.timezone_name,
            payload.location_name.strip(),
            latitude,
            longitude,
        )
        facts_would_change = snapshot_before != snapshot_proposed
        if facts_would_change and _birth_facts_cooldown_remaining_seconds(primary) > 0:
            raise HTTPException(
                status_code=403,
                detail=translate(
                    "account.errors.birthFactsCooldown",
                    locale=locale,
                    default=(
                        "Birth date, time, and place were updated recently. "
                        "Please wait before changing them again."
                    ),
                ),
            )

        primary.label = payload.label.strip() or primary.label or "Я"
        primary.relation = "self"
        primary.birth_date = payload.birth_date
        primary.birth_time = payload.birth_time
        primary.time_unknown = payload.time_unknown
        primary.timezone_offset_minutes = payload.timezone_offset_minutes
        primary.timezone_name = payload.timezone_name
        primary.location_name = payload.location_name.strip()
        primary.latitude = latitude
        primary.longitude = longitude
        primary.notes = payload.notes
        primary.is_primary = True
        if facts_would_change:
            primary.birth_facts_last_changed_at = datetime.utcnow()
        db.add(primary)
        # Invalidate natal cache, profile input changed.
        cached = (
            db.query(db_models.CachedNatalChart)
            .filter(db_models.CachedNatalChart.astro_profile_id == primary.id)
            .first()
        )
        if cached:
            db.delete(cached)

    db.commit()
    _ensure_primary(db, user, primary.id)
    db.commit()
    db.refresh(primary)

    full_name = " ".join([settings.first_name or "", settings.last_name or ""]).strip()
    if not full_name:
        raise HTTPException(
            status_code=400,
            detail=translate("account.errors.missingName", locale=locale, default="First name is required for numerology."),
        )

    try:
        numerology_profile = numerology_service.compute_profile(
            full_name=full_name,
            birth_date=payload.birth_date.isoformat(),
            locale=locale,
        )
    except NumerologyError as exc:
        if exc.code != "invalidName":
            raise HTTPException(
                status_code=400,
                detail=translate("numerology.errors.invalidBirthDate", locale=locale, default="Invalid birth date."),
            )
        fallback_name = _normalize_numerology_name(full_name)
        if not fallback_name:
            raise HTTPException(
                status_code=400,
                detail=translate("account.errors.missingName", locale=locale, default="First name is required for numerology."),
            )
        numerology_profile = numerology_service.compute_profile(
            full_name=fallback_name,
            birth_date=payload.birth_date.isoformat(),
            locale=locale,
        )
    numerology_service.save_profile(user.id, numerology_profile, locale=locale)

    await try_warm_natal_chart_cache_for_profile(
        db, primary, geocoder, locale, astro_service=astro_service
    )

    core = core_profile_service.build(db, user, astro_profile_id=primary.id)
    return CoreSetupResponse(
        status="ok",
        core_profile=CoreProfileResponse(**core),
        astro_profile=_astro_profile_to_dict(primary),
        numerology_profile=numerology_profile.model_dump(),
    )


def _get_profile_or_404(
    profile_id: int,
    user: db_models.User,
    db: Session,
    locale: str,
) -> db_models.AstroProfile:
    profile = (
        db.query(db_models.AstroProfile)
        .filter(db_models.AstroProfile.id == profile_id, db_models.AstroProfile.user_id == user.id)
        .first()
    )
    if profile is None:
        raise HTTPException(status_code=404, detail=translate("account.errors.astroProfileNotFound", locale=locale))
    return profile


@router.put("/astro-data/{profile_id}", response_model=AstroProfileSaveResponse)
async def update_astro_profile(
    profile_id: int,
    payload: AstroProfileUpdatePayload,
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
    astro_service: astro_service_mod.AstroService = Depends(lambda: astro_service_mod.AstroService()),
) -> AstroProfileSaveResponse:
    locale = request_locale(request)
    profile = _get_profile_or_404(profile_id, user, db, locale)

    snapshot_before = _birth_facts_snapshot_from_profile(profile)
    count_before = int(getattr(profile, "birth_facts_correction_count", 0) or 0)

    merge_birth_date = payload.birth_date if payload.birth_date is not None else profile.birth_date
    merge_birth_time = payload.birth_time if payload.birth_time is not None else profile.birth_time
    merge_time_unknown = payload.time_unknown if payload.time_unknown is not None else profile.time_unknown
    merge_tz_off = (
        payload.timezone_offset_minutes
        if payload.timezone_offset_minutes is not None
        else profile.timezone_offset_minutes
    )
    merge_tz_name = payload.timezone_name if payload.timezone_name is not None else profile.timezone_name
    merge_location = payload.location_name if payload.location_name is not None else profile.location_name
    merge_lat = payload.latitude if payload.latitude is not None else profile.latitude
    merge_lon = payload.longitude if payload.longitude is not None else profile.longitude

    res_lat, res_lon = _resolve_coordinates(geocoder, merge_location, merge_lat, merge_lon)
    snapshot_proposed = _birth_facts_snapshot_tuple(
        merge_birth_date,
        merge_birth_time,
        bool(merge_time_unknown),
        merge_tz_off,
        merge_tz_name,
        merge_location,
        res_lat,
        res_lon,
    )
    facts_changed = snapshot_before != snapshot_proposed

    if facts_changed and _birth_facts_cooldown_remaining_seconds(profile) > 0:
        raise HTTPException(
            status_code=403,
            detail=translate(
                "account.errors.birthFactsCooldown",
                locale=locale,
                default=(
                    "Birth date, time, and place were updated recently. "
                    "Please wait before changing them again."
                ),
            ),
        )

    if facts_changed and count_before >= MAX_ASTRO_BIRTH_FACTS_CORRECTIONS:
        raise HTTPException(
            status_code=403,
            detail=translate(
                "account.errors.birthFactsCorrectionLimit",
                locale=locale,
                default=(
                    "Date, time, and birth place can only be updated a few times per profile. "
                    "You can still change the profile name and notes."
                ),
            ),
        )

    for field in [
        "label",
        "relation",
        "birth_date",
        "birth_time",
        "time_unknown",
        "timezone_offset_minutes",
        "timezone_name",
        "location_name",
        "latitude",
        "longitude",
        "notes",
        "is_primary",
    ]:
        value = getattr(payload, field)
        if value is not None:
            setattr(profile, field, value)

    profile.relation = _normalize_relation(profile.relation, is_primary=bool(profile.is_primary))

    profile.latitude, profile.longitude = _resolve_coordinates(
        geocoder,
        profile.location_name,
        profile.latitude,
        profile.longitude,
    )

    snapshot_after = _birth_facts_snapshot_from_profile(profile)
    if snapshot_before != snapshot_after:
        profile.birth_facts_correction_count = count_before + 1
        profile.birth_facts_last_changed_at = datetime.utcnow()

    db.add(profile)
    db.commit()
    if payload.is_primary:
        _ensure_primary(db, user, profile.id)
        db.commit()
    db.refresh(profile)

    cached = (
        db.query(db_models.CachedNatalChart)
        .filter(db_models.CachedNatalChart.astro_profile_id == profile.id)
        .first()
    )
    if cached:
        db.delete(cached)
        db.commit()

    await try_warm_natal_chart_cache_for_profile(
        db, profile, geocoder, locale, astro_service=astro_service
    )
    db.refresh(profile)

    return _astro_profile_save_response(
        profile=profile,
        core_profile_service=core_profile_service,
        db=db,
        user=user,
    )


@router.delete("/astro-data/{profile_id}")
def delete_astro_profile(
    profile_id: int,
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
) -> dict:
    locale = request_locale(request)
    profile = _get_profile_or_404(profile_id, user, db, locale)
    db.delete(profile)
    db.commit()
    return {"status": "deleted"}


@router.post("/astro-data/{profile_id}/primary", response_model=AstroProfileSaveResponse)
async def set_primary_astro_profile(
    profile_id: int,
    request: Request,
    user: db_models.User = Depends(require_user),
    db: Session = Depends(get_session),
    core_profile_service: CoreProfileService = Depends(get_core_profile_service),
    geocoder: Geocoder = Depends(lambda: Geocoder()),
    astro_service: astro_service_mod.AstroService = Depends(lambda: astro_service_mod.AstroService()),
) -> AstroProfileSaveResponse:
    locale = request_locale(request)
    profile = _get_profile_or_404(profile_id, user, db, locale)
    profile.is_primary = True
    profile.relation = "self"
    db.add(profile)
    db.commit()
    _ensure_primary(db, user, profile.id)
    db.commit()
    db.refresh(profile)

    await try_warm_natal_chart_cache_for_profile(
        db, profile, geocoder, locale, astro_service=astro_service
    )
    db.refresh(profile)

    return _astro_profile_save_response(
        profile=profile,
        core_profile_service=core_profile_service,
        db=db,
        user=user,
    )
