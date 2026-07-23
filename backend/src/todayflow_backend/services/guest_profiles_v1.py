"""Durable guest_profiles upsert + claim bind to AstroProfile.

SoT for pre-account profiles (PRODUCT_DATA_INTAKE / AUTH_SESSION_CONTRACT_V1).
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import utc_naive_now
from todayflow_backend.services.guest_claim_v1 import _require_open_session

ALLOWED_LOCAL_KEYS = frozenset({"self", "person_a", "person_b"})


def _parse_birth_date(raw: Any) -> date:
    if isinstance(raw, date) and not isinstance(raw, datetime):
        return raw
    text = str(raw or "").strip()
    if not text:
        raise ValueError("birth_date_required")
    return date.fromisoformat(text[:10])


def _parse_birth_time(raw: Any) -> time | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, time):
        return raw
    text = str(raw).strip()
    if not text:
        return None
    # Accept HH:MM or HH:MM:SS
    parts = text.split(":")
    if len(parts) < 2:
        return None
    h, m = int(parts[0]), int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    return time(h, m, s)


def guest_profile_to_dict(row: db_models.GuestProfile) -> dict[str, Any]:
    return {
        "id": row.id,
        "guest_session_id": row.guest_session_id,
        "local_key": row.local_key,
        "display_name": row.display_name,
        "birth_date": row.birth_date.isoformat() if row.birth_date else None,
        "birth_time": row.birth_time.isoformat() if row.birth_time else None,
        "birth_time_known": bool(row.birth_time_known),
        "location_name": row.location_name,
        "latitude": row.latitude,
        "longitude": row.longitude,
        "timezone_name": row.timezone_name,
        "relation": row.relation,
        "is_owner_candidate": bool(row.is_owner_candidate),
        "natal_facts": row.natal_facts if isinstance(row.natal_facts, dict) else None,
        "updated_at": row.updated_at.isoformat() + "Z" if row.updated_at else None,
    }


def upsert_guest_profile(
    db: Session,
    *,
    guest_session_id: str,
    session_secret: str,
    local_key: str,
    display_name: str | None = None,
    birth_date: Any = None,
    birth_time: Any = None,
    birth_time_known: bool | None = None,
    location_name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    timezone_name: str | None = None,
    relation: str | None = None,
    is_owner_candidate: bool | None = None,
    natal_facts: dict | None = None,
) -> dict[str, Any]:
    session = _require_open_session(db, guest_session_id, session_secret)
    key = (local_key or "").strip()
    if key not in ALLOWED_LOCAL_KEYS:
        raise ValueError("invalid_local_key")

    bd = _parse_birth_date(birth_date)
    bt = _parse_birth_time(birth_time)
    known = bool(birth_time_known) if birth_time_known is not None else bool(bt)

    row = (
        db.query(db_models.GuestProfile)
        .filter(
            db_models.GuestProfile.guest_session_id == session.guest_session_id,
            db_models.GuestProfile.local_key == key,
        )
        .first()
    )
    if row is None:
        row = db_models.GuestProfile(
            guest_session_id=session.guest_session_id,
            local_key=key,
            birth_date=bd,
        )

    row.display_name = (display_name or row.display_name or "")[:128] or None
    row.birth_date = bd
    row.birth_time = bt
    row.birth_time_known = known
    row.location_name = location_name
    row.latitude = latitude
    row.longitude = longitude
    row.timezone_name = (timezone_name or row.timezone_name or None)
    if timezone_name:
        row.timezone_name = timezone_name[:64]
    if relation is not None:
        row.relation = (relation or "")[:32] or None
    elif key == "self":
        row.relation = row.relation or "self"
    elif key == "person_b":
        row.relation = row.relation or "partner"
    if is_owner_candidate is not None:
        row.is_owner_candidate = bool(is_owner_candidate)
    elif key == "self" or key == "person_a":
        row.is_owner_candidate = True if key == "self" else bool(row.is_owner_candidate)
    if natal_facts is not None and isinstance(natal_facts, dict):
        row.natal_facts = natal_facts
    row.updated_at = utc_naive_now()
    db.add(row)
    session.updated_at = utc_naive_now()
    db.add(session)
    db.commit()
    db.refresh(row)
    return guest_profile_to_dict(row)


def list_guest_profiles(
    db: Session,
    *,
    guest_session_id: str,
    session_secret: str,
) -> dict[str, Any]:
    session = _require_open_session(db, guest_session_id, session_secret)
    rows = (
        db.query(db_models.GuestProfile)
        .filter(db_models.GuestProfile.guest_session_id == session.guest_session_id)
        .order_by(db_models.GuestProfile.id.asc())
        .all()
    )
    return {
        "guest_session_id": session.guest_session_id,
        "profiles": [guest_profile_to_dict(r) for r in rows],
    }


def upsert_compat_pair(
    db: Session,
    *,
    guest_session_id: str,
    session_secret: str,
    person_a: dict[str, Any],
    person_b: dict[str, Any],
) -> dict[str, Any]:
    _require_open_session(db, guest_session_id, session_secret)

    def _person_fields(person: dict[str, Any], local_key: str, relation: str, owner: bool) -> dict[str, Any]:
        return {
            "local_key": local_key,
            "display_name": person.get("display_name") or person.get("label"),
            "birth_date": person.get("birth_date"),
            "birth_time": person.get("birth_time"),
            "birth_time_known": not bool(person.get("time_unknown", True)),
            "location_name": person.get("location_name"),
            "latitude": person.get("latitude"),
            "longitude": person.get("longitude"),
            "timezone_name": person.get("timezone_name"),
            "relation": relation,
            "is_owner_candidate": owner,
            "natal_facts": person.get("natal_facts") if isinstance(person.get("natal_facts"), dict) else None,
        }

    a = upsert_guest_profile(
        db,
        guest_session_id=guest_session_id,
        session_secret=session_secret,
        **_person_fields(person_a, "person_a", "self", True),
    )
    b = upsert_guest_profile(
        db,
        guest_session_id=guest_session_id,
        session_secret=session_secret,
        **_person_fields(person_b, "person_b", "partner", False),
    )
    return {"guest_session_id": guest_session_id, "profiles": [a, b]}


def bind_guest_profiles_to_user(
    db: Session,
    *,
    guest_session_id: str,
    user_id: int,
    skip_if_user_has_primary: bool = True,
) -> dict[str, Any]:
    """Create AstroProfile rows from durable guest_profiles. Idempotent-ish: skips duplicate birth dates."""
    rows = (
        db.query(db_models.GuestProfile)
        .filter(db_models.GuestProfile.guest_session_id == guest_session_id)
        .order_by(db_models.GuestProfile.id.asc())
        .all()
    )
    if not rows:
        return {"created_profile_ids": [], "skipped": True, "reason": "no_guest_profiles"}

    existing = (
        db.query(db_models.AstroProfile)
        .filter(db_models.AstroProfile.user_id == user_id)
        .all()
    )
    has_primary = any(bool(p.is_primary) for p in existing)
    existing_dates = {
        p.birth_date.isoformat() for p in existing if p.birth_date is not None
    }

    created: list[int] = []
    natal_bound: list[int] = []

    # Prefer self / person_a as primary when user has none.
    ordered = sorted(
        rows,
        key=lambda r: 0 if r.local_key in ("self", "person_a") else 1,
    )

    for row in ordered:
        bd_key = row.birth_date.isoformat() if row.birth_date else ""
        if bd_key and bd_key in existing_dates and skip_if_user_has_primary:
            continue

        make_primary = False
        if not has_primary and row.local_key in ("self", "person_a") and row.is_owner_candidate:
            make_primary = True
            has_primary = True
        elif not has_primary and row.local_key == "self":
            make_primary = True
            has_primary = True

        relation = (row.relation or ("self" if make_primary else "close_person"))[:32]
        label = (row.display_name or "Профиль")[:128]
        profile = db_models.AstroProfile(
            user_id=user_id,
            label=label,
            birth_date=row.birth_date,
            birth_time=row.birth_time if row.birth_time_known else None,
            time_unknown=not bool(row.birth_time_known),
            location_name=row.location_name,
            latitude=row.latitude,
            longitude=row.longitude,
            timezone_name=row.timezone_name,
            relation=relation,
            is_primary=make_primary,
        )
        db.add(profile)
        db.flush()
        created.append(int(profile.id))
        if bd_key:
            existing_dates.add(bd_key)

        if isinstance(row.natal_facts, dict) and row.natal_facts.get("contract_version"):
            try:
                from todayflow_backend.services.natal_facts_contract_v1 import (
                    persist_natal_facts_on_profile,
                    validate_natal_facts,
                )

                mode = "full" if row.birth_time_known and row.latitude is not None else "date_only"
                facts = validate_natal_facts(row.natal_facts, expected_mode=mode)
                persist_natal_facts_on_profile(db, profile.id, facts)
                natal_bound.append(int(profile.id))
            except Exception:
                # Keep AstroProfile; facts can be regenerated later.
                pass

    if created:
        db.flush()
    return {
        "created_profile_ids": created,
        "natal_facts_bound": natal_bound,
        "skipped": False,
    }
