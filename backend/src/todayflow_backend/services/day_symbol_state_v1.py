"""Unified server SoT for card-of-day and day-number reveal.

Product canon (DAY_LIFECYCLE_V1 / DAY_SYMBOL_REVEAL_CANON_V1):
- System prebakes card + number at day assemble (identity stored, not public until reveal).
- Ritual reveal only opens what was already laid out — does not reassemble the day.
- Card: prebaked id is SoT; client pick is theater and may be ignored if prebaked.
- Number: system-calculated from local_date; reveal flips visibility.
- GET never creates/reveals/mutates. Only POST reveal/claim changes reveal flags.
- Before reveal: no id/name/number/meaning in any public payload.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from todayflow_backend.data import card_base_v1, number_base_v1
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import utc_naive_now
from todayflow_backend.services.numerology import NumerologyService, get_numerology_service
from todayflow_backend.services.tarot import TarotService

logger = logging.getLogger(__name__)

DAY_SYMBOL_STATE_V1 = "day_symbol_state_v1"

STATUS_NOT_REVEALED = "not_revealed"
STATUS_REVEALED = "revealed"
STATUS_GENERATION_PENDING = "generation_pending"
STATUS_READY = "ready"
STATUS_ERROR = "error"

_REVEALED_OK = frozenset({STATUS_REVEALED, STATUS_READY})


def owner_key_for_user(user_id: int) -> str:
    return f"u:{int(user_id)}"


def owner_key_for_guest(guest_session_id: str) -> str:
    gid = (guest_session_id or "").strip()
    if not gid or len(gid) > 64:
        raise ValueError("invalid_guest_session_id")
    return f"g:{gid}"


def resolve_local_date(*, local_date: str | date | None, timezone_name: str | None) -> date:
    if isinstance(local_date, date):
        return local_date
    if isinstance(local_date, str) and local_date.strip():
        return date.fromisoformat(local_date.strip()[:10])
    tz_name = (timezone_name or "UTC").strip() or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
    return datetime.now(tz).date()


def _empty_view(*, local_date: date, timezone_name: str) -> dict[str, Any]:
    return {
        "contract_version": DAY_SYMBOL_STATE_V1,
        "local_date": local_date.isoformat(),
        "timezone_name": timezone_name or "UTC",
        "card": {
            "status": STATUS_NOT_REVEALED,
            "revealed": False,
        },
        "number": {
            "status": STATUS_NOT_REVEALED,
            "revealed": False,
        },
    }


def get_state_row(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
) -> db_models.DaySymbolState | None:
    return (
        db.query(db_models.DaySymbolState)
        .filter(
            db_models.DaySymbolState.owner_key == owner_key,
            db_models.DaySymbolState.local_date == local_date,
        )
        .first()
    )


def is_card_revealed(row: db_models.DaySymbolState | None) -> bool:
    return bool(row and str(row.card_status or "") in _REVEALED_OK and row.card_id)


def is_number_revealed(row: db_models.DaySymbolState | None) -> bool:
    return bool(row and str(row.number_status or "") in _REVEALED_OK and row.number_reduced is not None)


def public_view(
    row: db_models.DaySymbolState | None,
    *,
    local_date: date,
    timezone_name: str = "UTC",
    tarot_service: TarotService | None = None,
) -> dict[str, Any]:
    """Client-safe view: identity only when revealed."""
    if row is None:
        return _empty_view(local_date=local_date, timezone_name=timezone_name)

    out = {
        "contract_version": DAY_SYMBOL_STATE_V1,
        "local_date": row.local_date.isoformat(),
        "timezone_name": row.timezone_name or timezone_name or "UTC",
        "card": {
            "status": row.card_status or STATUS_NOT_REVEALED,
            "revealed": is_card_revealed(row),
            "revealed_at": row.card_revealed_at.isoformat() if row.card_revealed_at else None,
            "reveal_source": row.card_reveal_source,
        },
        "number": {
            "status": row.number_status or STATUS_NOT_REVEALED,
            "revealed": is_number_revealed(row),
            "revealed_at": row.number_revealed_at.isoformat() if row.number_revealed_at else None,
            "reveal_source": row.number_reveal_source,
        },
    }

    if is_card_revealed(row):
        card_id = int(row.card_id) if str(row.card_id).isdigit() else None
        orientation = row.card_orientation or "upright"
        base = card_base_v1.get_base_meaning(card_id, orientation) if card_id is not None else None
        svc = tarot_service or TarotService()
        card = None
        try:
            if card_id is not None:
                card = svc.get_card_by_id(card_id)
        except Exception:
            card = None
        name = (base or {}).get("name_ru") or (card.name if card else None)
        keywords = list((base or {}).get("keywords") or [])
        if not keywords and card:
            keywords = list(card.keywords or [])
        meaning = (base or {}).get("meaning")
        if not meaning and card:
            meaning = (
                card.upright if card_base_v1.normalize_orientation(orientation) == "upright" else card.reversed
            )
        out["card"].update(
            {
                "id": card_id if card_id is not None else row.card_id,
                "orientation": card_base_v1.normalize_orientation(orientation),
                "name": name,
                "keywords": keywords,
                "meaning": meaning,
                "generated_at": row.card_generated_at.isoformat() if row.card_generated_at else None,
            }
        )

    if is_number_revealed(row):
        reduced = int(row.number_reduced) if row.number_reduced is not None else None
        num_base = number_base_v1.get_number_base(reduced) if reduced is not None else None
        out["number"].update(
            {
                "value": row.number_value,
                "reduced_value": row.number_reduced,
                "is_master": bool(row.number_is_master),
                "title": (num_base or {}).get("title") or row.number_title,
                "summary": (num_base or {}).get("base_meaning") or row.number_summary,
                "generated_at": row.number_generated_at.isoformat() if row.number_generated_at else None,
            }
        )
    return out


def redacted_tarot_card_dict(view: dict[str, Any]) -> dict[str, Any]:
    card = view.get("card") if isinstance(view.get("card"), dict) else {}
    if not card.get("revealed"):
        return {"selection_status": "not_selected", "status": STATUS_NOT_REVEALED}
    return {
        "selection_status": "selected",
        "status": STATUS_REVEALED,
        "id": card.get("id"),
        "name": card.get("name"),
        "orientation": card.get("orientation"),
        "meaning": card.get("meaning"),
        "keywords": card.get("keywords") or [],
    }


def redacted_numerology_dict(view: dict[str, Any]) -> dict[str, Any]:
    num = view.get("number") if isinstance(view.get("number"), dict) else {}
    if not num.get("revealed"):
        return {"selection_status": "not_selected", "status": STATUS_NOT_REVEALED}
    return {
        "selection_status": "selected",
        "status": STATUS_REVEALED,
        "value": num.get("value"),
        "reduced_value": num.get("reduced_value"),
        "is_master": num.get("is_master"),
        "title": num.get("title"),
        "summary": num.get("summary"),
    }


def redacted_explanations(*, card_revealed: bool, number_revealed: bool) -> tuple[dict, dict]:
    empty = {"status": STATUS_NOT_REVEALED, "personalized": False}
    return (
        {} if card_revealed else dict(empty),
        {} if number_revealed else dict(empty),
    )


def _ensure_row(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
    timezone_name: str,
    user_id: int | None,
    guest_session_id: str | None,
) -> db_models.DaySymbolState:
    row = get_state_row(db, owner_key=owner_key, local_date=local_date)
    if row:
        if timezone_name and row.timezone_name != timezone_name:
            row.timezone_name = timezone_name
        return row
    row = db_models.DaySymbolState(
        owner_key=owner_key,
        user_id=user_id,
        guest_session_id=guest_session_id,
        local_date=local_date,
        timezone_name=timezone_name or "UTC",
        card_status=STATUS_NOT_REVEALED,
        number_status=STATUS_NOT_REVEALED,
    )
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        existing = get_state_row(db, owner_key=owner_key, local_date=local_date)
        if existing is None:
            raise
        return existing
    return row


def _stable_day_card_id(*, owner_key: str, local_date: date) -> int:
    digest = hashlib.sha256(f"{owner_key}|{local_date.isoformat()}|day_card".encode()).hexdigest()
    return int(digest[:8], 16) % 78


def _stable_day_card_orientation(*, owner_key: str, local_date: date) -> str:
    """Stable upright/reversed from the same day-card digest family (not hardcode upright)."""
    digest = hashlib.sha256(
        f"{owner_key}|{local_date.isoformat()}|day_card_orientation".encode()
    ).hexdigest()
    return "reversed" if (int(digest[:8], 16) % 2) == 1 else "upright"


def ensure_symbols_prebaked(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
    timezone_name: str,
    user_id: int | None = None,
    guest_session_id: str | None = None,
    numerology_service: NumerologyService | None = None,
    locale: str = "ru",
) -> db_models.DaySymbolState:
    """Lay out card + number for the day without revealing them (assemble-once package)."""
    row = _ensure_row(
        db,
        owner_key=owner_key,
        local_date=local_date,
        timezone_name=timezone_name,
        user_id=user_id,
        guest_session_id=guest_session_id,
    )
    now = utc_naive_now()
    changed = False

    if row.number_reduced is None and not is_number_revealed(row):
        svc = numerology_service or get_numerology_service()
        insight = svc.daily_number(reference_date=local_date, locale=locale or "ru", reveal=True)
        number = insight.number
        if number is not None:
            row.number_value = int(number.value) if number.value is not None else int(number.reduced_value)
            row.number_reduced = int(number.reduced_value)
            row.number_is_master = bool(number.is_master)
            row.number_title = str(number.title or "")[:120]
            row.number_summary = str(number.summary or "")
            row.number_generated_at = now
            # Keep hidden until ritual reveal.
            row.number_status = STATUS_NOT_REVEALED
            row.number_revealed_at = None
            changed = True

    if not row.card_id and not is_card_revealed(row):
        row.card_id = str(_stable_day_card_id(owner_key=owner_key, local_date=local_date))
        row.card_orientation = _stable_day_card_orientation(
            owner_key=owner_key, local_date=local_date
        )
        row.card_generated_at = now
        row.card_status = STATUS_NOT_REVEALED
        row.card_revealed_at = None
        changed = True
    elif row.card_id and not row.card_orientation and not is_card_revealed(row):
        row.card_orientation = _stable_day_card_orientation(
            owner_key=owner_key, local_date=local_date
        )
        changed = True

    if changed:
        row.updated_at = now
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def reveal_card(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
    timezone_name: str,
    card_id: int,
    orientation: str = "upright",
    reveal_source: str,
    idempotency_key: str,
    user_id: int | None = None,
    guest_session_id: str | None = None,
    tarot_service: TarotService | None = None,
) -> dict[str, Any]:
    """Reveal the day's card (prebaked at assemble when present). Idempotent on idempotency_key."""
    key = (idempotency_key or "").strip()
    if not key:
        raise ValueError("idempotency_key_required")
    orient = (orientation or "upright").strip().lower()
    if orient not in ("upright", "reversed"):
        orient = "upright"

    svc = tarot_service or TarotService()

    # Idempotency: same key returns existing reveal for THIS owner only.
    by_idem = (
        db.query(db_models.DaySymbolState)
        .filter(
            db_models.DaySymbolState.owner_key == owner_key,
            db_models.DaySymbolState.card_idempotency_key == key,
        )
        .first()
    )
    if by_idem is not None:
        return public_view(by_idem, local_date=by_idem.local_date, timezone_name=by_idem.timezone_name, tarot_service=svc)

    row = _ensure_row(
        db,
        owner_key=owner_key,
        local_date=local_date,
        timezone_name=timezone_name,
        user_id=user_id,
        guest_session_id=guest_session_id,
    )
    if is_card_revealed(row):
        # Already revealed for this day — return same card (no silent swap)
        return public_view(row, local_date=local_date, timezone_name=timezone_name, tarot_service=svc)

    # Assemble-once: if the day package already laid out a card, reveal that identity.
    if row.card_id and str(row.card_id).strip().isdigit():
        resolved_id = int(str(row.card_id).strip())
    else:
        resolved_id = int(card_id)
    resolved = svc.get_card_by_id(resolved_id)
    if resolved is None:
        raise ValueError("unknown_tarot_card")

    now = utc_naive_now()
    row.card_id = str(resolved_id)
    if not row.card_orientation:
        row.card_orientation = orient
    row.card_generated_at = row.card_generated_at or now
    row.card_revealed_at = now
    row.card_reveal_source = (reveal_source or "ritual")[:64]
    row.card_idempotency_key = key[:128]
    row.card_status = STATUS_READY
    row.updated_at = now
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        again = (
            db.query(db_models.DaySymbolState)
            .filter(
                db_models.DaySymbolState.owner_key == owner_key,
                db_models.DaySymbolState.card_idempotency_key == key,
            )
            .first()
        )
        if again:
            return public_view(again, local_date=again.local_date, timezone_name=again.timezone_name, tarot_service=svc)
        # Concurrent first reveal for this owner/day may race on uq_day_symbol_owner_date.
        existing = get_state_row(db, owner_key=owner_key, local_date=local_date)
        if existing is not None and is_card_revealed(existing):
            return public_view(existing, local_date=local_date, timezone_name=timezone_name, tarot_service=svc)
        raise
    return public_view(row, local_date=local_date, timezone_name=timezone_name, tarot_service=svc)


def reveal_number(
    db: Session,
    *,
    owner_key: str,
    local_date: date,
    timezone_name: str,
    reveal_source: str,
    idempotency_key: str,
    user_id: int | None = None,
    guest_session_id: str | None = None,
    numerology_service: NumerologyService | None = None,
) -> dict[str, Any]:
    """System-calculated day number → reveal. Idempotent on idempotency_key."""
    key = (idempotency_key or "").strip()
    if not key:
        raise ValueError("idempotency_key_required")

    by_idem = (
        db.query(db_models.DaySymbolState)
        .filter(
            db_models.DaySymbolState.owner_key == owner_key,
            db_models.DaySymbolState.number_idempotency_key == key,
        )
        .first()
    )
    if by_idem is not None:
        return public_view(by_idem, local_date=by_idem.local_date, timezone_name=by_idem.timezone_name)

    row = _ensure_row(
        db,
        owner_key=owner_key,
        local_date=local_date,
        timezone_name=timezone_name,
        user_id=user_id,
        guest_session_id=guest_session_id,
    )
    if is_number_revealed(row):
        return public_view(row, local_date=local_date, timezone_name=timezone_name)

    now = utc_naive_now()
    # Prefer prebaked identity from assemble; compute only if missing.
    if row.number_reduced is None:
        svc = numerology_service or get_numerology_service()
        insight = svc.daily_number(reference_date=local_date, locale="ru", reveal=True)
        number = insight.number
        if number is None:
            row.number_status = STATUS_ERROR
            db.add(row)
            db.commit()
            raise ValueError("number_generation_failed")
        row.number_value = int(number.value) if number.value is not None else int(number.reduced_value)
        row.number_reduced = int(number.reduced_value)
        row.number_is_master = bool(number.is_master)
        row.number_title = str(number.title or "")[:120]
        row.number_summary = str(number.summary or "")
        row.number_generated_at = now

    row.number_revealed_at = now
    row.number_reveal_source = (reveal_source or "ritual")[:64]
    row.number_idempotency_key = key[:128]
    row.number_status = STATUS_READY
    row.updated_at = now
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        again = (
            db.query(db_models.DaySymbolState)
            .filter(
                db_models.DaySymbolState.owner_key == owner_key,
                db_models.DaySymbolState.number_idempotency_key == key,
            )
            .first()
        )
        if again:
            return public_view(again, local_date=again.local_date, timezone_name=again.timezone_name)
        existing = get_state_row(db, owner_key=owner_key, local_date=local_date)
        if existing is not None and is_number_revealed(existing):
            return public_view(existing, local_date=local_date, timezone_name=timezone_name)
        raise
    return public_view(row, local_date=local_date, timezone_name=timezone_name)


def claim_guest_symbols_to_user(
    db: Session,
    *,
    guest_session_id: str,
    user_id: int,
    local_date: date | None = None,
    commit: bool = True,
) -> dict[str, Any]:
    """Transfer guest day symbol state to authenticated user (idempotent).

    When ``commit=False``, caller owns the transaction (used by full guest claim).
    """
    gkey = owner_key_for_guest(guest_session_id)
    ukey = owner_key_for_user(user_id)
    q = db.query(db_models.DaySymbolState).filter(db_models.DaySymbolState.owner_key == gkey)
    if local_date is not None:
        q = q.filter(db_models.DaySymbolState.local_date == local_date)
    guest_rows = list(q.all())
    transferred = 0
    for grow in guest_rows:
        existing = get_state_row(db, owner_key=ukey, local_date=grow.local_date)
        if existing is None:
            grow.owner_key = ukey
            grow.user_id = user_id
            grow.guest_session_id = guest_session_id
            grow.updated_at = utc_naive_now()
            db.add(grow)
            transferred += 1
            continue
        # Merge: keep user reveal if present; else copy from guest
        changed = False
        if not is_card_revealed(existing) and is_card_revealed(grow):
            existing.card_status = grow.card_status
            existing.card_id = grow.card_id
            existing.card_orientation = grow.card_orientation
            existing.card_generated_at = grow.card_generated_at
            existing.card_revealed_at = grow.card_revealed_at
            existing.card_reveal_source = grow.card_reveal_source
            if grow.card_idempotency_key and not existing.card_idempotency_key:
                existing.card_idempotency_key = f"claim:{grow.card_idempotency_key}"[:128]
            changed = True
        if not is_number_revealed(existing) and is_number_revealed(grow):
            existing.number_status = grow.number_status
            existing.number_value = grow.number_value
            existing.number_reduced = grow.number_reduced
            existing.number_is_master = grow.number_is_master
            existing.number_title = grow.number_title
            existing.number_summary = grow.number_summary
            existing.number_generated_at = grow.number_generated_at
            existing.number_revealed_at = grow.number_revealed_at
            existing.number_reveal_source = grow.number_reveal_source
            if grow.number_idempotency_key and not existing.number_idempotency_key:
                existing.number_idempotency_key = f"claim:{grow.number_idempotency_key}"[:128]
            changed = True
        if changed:
            existing.updated_at = utc_naive_now()
            db.add(existing)
            transferred += 1
        # Drop guest row to avoid double-claim
        db.delete(grow)
    if commit:
        db.commit()
    else:
        db.flush()
    return {
        "contract_version": DAY_SYMBOL_STATE_V1,
        "transferred_rows": transferred,
        "user_id": user_id,
        "guest_session_id": guest_session_id,
    }


def ritual_context_from_symbol_view(view: dict[str, Any]) -> dict[str, Any]:
    """Only revealed fields for day_story / brief / narrative."""
    ritual: dict[str, Any] = {}
    card = view.get("card") if isinstance(view.get("card"), dict) else {}
    num = view.get("number") if isinstance(view.get("number"), dict) else {}
    if card.get("revealed") and card.get("id") is not None:
        ritual["tarot_main_id"] = card.get("id")
    if card.get("revealed") and card.get("name"):
        ritual["tarot_name_ru"] = card.get("name")
    if num.get("revealed") and num.get("reduced_value") is not None:
        ritual["numerology_value"] = num.get("reduced_value")
    return ritual


def fingerprint_symbol_view(view: dict[str, Any]) -> str:
    raw = (
        f"c:{view.get('card', {}).get('status')}:{view.get('card', {}).get('id')}|"
        f"n:{view.get('number', {}).get('status')}:{view.get('number', {}).get('reduced_value')}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
