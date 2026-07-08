"""Internal admin endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_admin
from todayflow_backend.data import content_system, quality_gate
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services import admin as admin_service
from todayflow_backend.services.tarot import TarotService, get_tarot_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/paragraphs")
def list_paragraphs(admin=Depends(require_admin), db: Session = Depends(get_session)) -> list[dict]:
    _ = admin  # actor not needed for listing but dependency enforces auth
    return admin_service.list_paragraphs(db)


@router.get("/paragraphs/{paragraph_id}")
def get_paragraph(paragraph_id: str, request: Request, admin=Depends(require_admin), db: Session = Depends(get_session)) -> dict:
    _ = admin
    data = admin_service.get_paragraph(db, paragraph_id)
    if not data:
        raise HTTPException(
            status_code=404, detail=translate("admin.errors.paragraphMissing", locale=request_locale(request))
        )
    return data


class TogglePayload(BaseModel):
    lite_enabled: bool | None = None
    full_enabled: bool | None = None


class VariantUpdatePayload(BaseModel):
    text: str


@router.post("/paragraphs/{paragraph_id}/toggle")
def toggle_paragraph(
    request: Request,
    paragraph_id: str,
    payload: TogglePayload,
    admin=Depends(require_admin),
    db: Session = Depends(get_session),
) -> dict:
    try:
        override = admin_service.toggle_paragraph(
            db,
            paragraph_id=paragraph_id,
            lite_enabled=payload.lite_enabled,
            full_enabled=payload.full_enabled,
            actor=admin.email,
        )
        return {
            "paragraph_id": paragraph_id,
            "lite_enabled": override.lite_enabled,
            "full_enabled": override.full_enabled,
        }
    except Exception as exc:
        message = translate("admin.errors.toggleFailed", locale=request_locale(request))
        raise HTTPException(status_code=400, detail=f"{message}: {exc}") from exc


@router.post("/paragraphs/{paragraph_id}/variants/{variant_id}")
def update_variant_text(
    request: Request,
    paragraph_id: str,
    variant_id: str,
    payload: VariantUpdatePayload,
    admin=Depends(require_admin),
    db: Session = Depends(get_session),
) -> dict:
    try:
        override = admin_service.update_variant_text(
            db,
            paragraph_id=paragraph_id,
            variant_id=variant_id,
            text=payload.text,
            actor=admin.email,
        )
        return {
            "paragraph_id": paragraph_id,
            "variant_id": variant_id,
            "text": override.text if override else None,
        }
    except Exception as exc:
        message = translate("admin.errors.variantUpdateFailed", locale=request_locale(request))
        raise HTTPException(status_code=400, detail=f"{message}: {exc}") from exc


@router.get("/paragraphs/audit")
def audit_logs(admin=Depends(require_admin), db: Session = Depends(get_session)) -> list[dict]:
    _ = admin
    return admin_service.list_audit_logs(db)


@router.get("/tarot/reminders/due")
def list_due_tarot_reminders(
    limit: int = Query(25, ge=1, le=200),
    admin=Depends(require_admin),
    tarot_service: TarotService = Depends(get_tarot_service),
) -> list[dict]:
    _ = admin
    rows = tarot_service.list_due_reminders(limit=limit)
    return [
        {
            "user_id": row.user_id,
            "timezone": row.timezone,
            "hour": row.hour,
            "minute": row.minute,
            "next_run_at": row.next_run_at.isoformat() if row.next_run_at else None,
            "last_sent_at": row.last_sent_at.isoformat() if row.last_sent_at else None,
        }
        for row in rows
    ]


@router.post("/tarot/reminders/{user_id}/sent")
def mark_tarot_reminder_sent(
    user_id: int,
    admin=Depends(require_admin),
    tarot_service: TarotService = Depends(get_tarot_service),
) -> dict:
    _ = admin
    tarot_service.record_reminder_sent(user_id)
    return {"status": "ok"}


# ===== Admin Forecasts (Web Canon v1, Вертикаль 3) =====


@router.get("/forecasts", response_model=List[Dict[str, Any]])
def list_admin_forecasts(
    locale: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    include_unpublished: bool = Query(False),
    admin=Depends(require_admin),
) -> List[Dict[str, Any]]:
    """Список DailyForecast для админки (включая unpublished, без Quality Gate фильтра)."""
    raw = content_system.load_daily_forecasts_raw()
    out: List[Dict[str, Any]] = []
    for f in raw:
        if locale is not None and f.get("locale") != locale:
            continue
        d = f.get("date")
        if not isinstance(d, str):
            continue
        if from_date is not None and d < from_date:
            continue
        if to_date is not None and d > to_date:
            continue
        if not include_unpublished and not f.get("published"):
            continue
        out.append(f)
    out.sort(key=lambda x: (x.get("date") or "", x.get("locale") or ""))
    return out


@router.get("/forecasts/{forecast_id}", response_model=Dict[str, Any])
def get_admin_forecast(
    forecast_id: str,
    request: Request,
    admin=Depends(require_admin),
) -> Dict[str, Any]:
    """Один DailyForecast по ID (для админки, включая unpublished)."""
    raw = content_system.load_daily_forecasts_raw()
    for f in raw:
        if f.get("id") == forecast_id:
            return f
    raise HTTPException(status_code=404, detail=translate("admin.errors.forecastNotFound", locale=request_locale(request), default="forecast_not_found"))


class ForecastCreateUpdate(BaseModel):
    """Payload для создания/обновления DailyForecast."""
    id: Optional[str] = None
    date: str
    locale: str
    published: bool = False
    tags: List[str] = []
    blocks: Dict[str, Any]
    markers: Dict[str, Any]


@router.post("/forecasts", response_model=Dict[str, Any])
def create_forecast(
    payload: ForecastCreateUpdate,
    request: Request,
    admin=Depends(require_admin),
) -> Dict[str, Any]:
    """Создать DailyForecast. Автоматически генерирует id если нет."""
    raw = content_system.load_daily_forecasts_raw()
    forecast = payload.model_dump(exclude_none=True)
    if "id" not in forecast or not forecast["id"]:
        date = forecast.get("date", "")
        locale = forecast.get("locale", "ru")
        forecast["id"] = f"forecast-{date}-{locale}"
    # Проверка Quality Gate (но не блокируем сохранение)
    qg_result = _validate_forecast_quality(forecast)
    forecast["_quality_gate_errors"] = qg_result.errors if not qg_result.ok else []
    raw.append(forecast)
    content_system.save_daily_forecasts(raw)
    return forecast


@router.put("/forecasts/{forecast_id}", response_model=Dict[str, Any])
def update_forecast(
    forecast_id: str,
    payload: ForecastCreateUpdate,
    request: Request,
    admin=Depends(require_admin),
) -> Dict[str, Any]:
    """Обновить DailyForecast."""
    raw = content_system.load_daily_forecasts_raw()
    idx = None
    for i, f in enumerate(raw):
        if f.get("id") == forecast_id:
            idx = i
            break
    if idx is None:
        raise HTTPException(status_code=404, detail=translate("admin.errors.forecastNotFound", locale=request_locale(request), default="forecast_not_found"))
    forecast = payload.model_dump(exclude_none=True)
    forecast["id"] = forecast_id
    qg_result = _validate_forecast_quality(forecast)
    forecast["_quality_gate_errors"] = qg_result.errors if not qg_result.ok else []
    raw[idx] = forecast
    content_system.save_daily_forecasts(raw)
    return forecast


@router.delete("/forecasts/{forecast_id}")
def delete_forecast(
    forecast_id: str,
    request: Request,
    admin=Depends(require_admin),
) -> dict:
    """Удалить DailyForecast."""
    raw = content_system.load_daily_forecasts_raw()
    filtered = [f for f in raw if f.get("id") != forecast_id]
    if len(filtered) == len(raw):
        raise HTTPException(status_code=404, detail=translate("admin.errors.forecastNotFound", locale=request_locale(request), default="forecast_not_found"))
    content_system.save_daily_forecasts(filtered)
    return {"status": "ok"}


@router.post("/forecasts/{forecast_id}/publish")
def publish_forecast(
    forecast_id: str,
    request: Request,
    admin=Depends(require_admin),
) -> Dict[str, Any]:
    """Publish/Unpublish DailyForecast (toggle)."""
    raw = content_system.load_daily_forecasts_raw()
    for f in raw:
        if f.get("id") == forecast_id:
            f["published"] = not f.get("published", False)
            content_system.save_daily_forecasts(raw)
            return f
    raise HTTPException(status_code=404, detail=translate("admin.errors.forecastNotFound", locale=request_locale(request), default="forecast_not_found"))


def _validate_forecast_quality(forecast: Dict[str, Any]) -> quality_gate.QualityGateResult:
    """Валидация через Quality Gate (для админки)."""
    body = set(content_system.load_dictionary("body_markers"))
    social = set(content_system.load_dictionary("social_markers"))
    domestic = set(content_system.load_dictionary("domestic_details"))
    micro = set(content_system.load_dictionary("micro_actions"))
    lex = content_system.load_lexicon()
    banned = lex.get("banned_words") or []
    tags_allow = lex.get("tags_allow_list") or []
    return quality_gate.validate_daily_forecast(
        forecast,
        body_markers=body,
        social_markers=social,
        domestic_markers=domestic,
        micro_action_markers=micro,
        banned_words=banned,
        tags_allow_list=tags_allow,
    )


# ===== Admin Lexicon (Web Canon v1, Вертикаль 3) =====


@router.get("/lexicon", response_model=Dict[str, Any])
def get_lexicon(admin=Depends(require_admin)) -> Dict[str, Any]:
    """Получить лексикон (banned_words, tags_allow_list, phrases)."""
    return content_system.load_lexicon()


@router.put("/lexicon", response_model=Dict[str, Any])
def update_lexicon(
    payload: Dict[str, Any],
    admin=Depends(require_admin),
) -> Dict[str, Any]:
    """Обновить лексикон (полная замена)."""
    content_system.save_lexicon(payload)
    return payload


class LexiconPhrase(BaseModel):
    """Фраза лексикона с метаданными."""
    id: Optional[str] = None
    text: str
    context: str  # work | relationship | money | body
    trigger: str  # waiting | overload | uncertainty | comparison | conflict | deadline | etc.
    emotion: str  # tension | irritability | numbness | hope | etc.
    reaction: str  # rush | freeze | overthink | withdraw | please | etc.
    tone: str  # calm | warm | neutral


@router.post("/lexicon/phrases", response_model=Dict[str, Any])
def create_lexicon_phrase(
    payload: LexiconPhrase,
    admin=Depends(require_admin),
) -> Dict[str, Any]:
    """Добавить фразу в лексикон."""
    lex = content_system.load_lexicon()
    phrases = lex.get("phrases") or []
    phrase = payload.model_dump(exclude_none=True)
    if "id" not in phrase or not phrase["id"]:
        max_id = max((int(p.get("id", "lex.0").split(".")[-1]) for p in phrases if isinstance(p.get("id"), str) and p["id"].startswith("lex.")), default=0)
        phrase["id"] = f"lex.{max_id + 1:03d}"
    phrases.append(phrase)
    lex["phrases"] = phrases
    content_system.save_lexicon(lex)
    return phrase


@router.put("/lexicon/phrases/{phrase_id}", response_model=Dict[str, Any])
def update_lexicon_phrase(
    phrase_id: str,
    payload: LexiconPhrase,
    request: Request,
    admin=Depends(require_admin),
) -> Dict[str, Any]:
    """Обновить фразу в лексиконе."""
    lex = content_system.load_lexicon()
    phrases = lex.get("phrases") or []
    idx = None
    for i, p in enumerate(phrases):
        if p.get("id") == phrase_id:
            idx = i
            break
    if idx is None:
        raise HTTPException(status_code=404, detail=translate("admin.errors.phraseNotFound", locale=request_locale(request), default="phrase_not_found"))
    phrase = payload.model_dump(exclude_none=True)
    phrase["id"] = phrase_id
    phrases[idx] = phrase
    lex["phrases"] = phrases
    content_system.save_lexicon(lex)
    return phrase


@router.delete("/lexicon/phrases/{phrase_id}")
def delete_lexicon_phrase(
    phrase_id: str,
    request: Request,
    admin=Depends(require_admin),
) -> dict:
    """Удалить фразу из лексикона."""
    lex = content_system.load_lexicon()
    phrases = lex.get("phrases") or []
    filtered = [p for p in phrases if p.get("id") != phrase_id]
    if len(filtered) == len(phrases):
        raise HTTPException(status_code=404, detail=translate("admin.errors.phraseNotFound", locale=request_locale(request), default="phrase_not_found"))
    lex["phrases"] = filtered
    content_system.save_lexicon(lex)
    return {"status": "ok"}
