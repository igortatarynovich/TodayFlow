"""Day flow activity windows — labels only.

SoT: Global Day Engine owns window times / supports / cautions.
Natal glance clocks remain geometry (`today_glance_timeline_v1`).
Kimi is not a timeline decision. Bank = fill-empty labels only.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "day_flow_windows_v1"
MODULE = "day_flow_windows_v1"
SURFACE = "windows"
COPY_SOURCE_KIMI = "kimi_v1"
COPY_SOURCE_BANK = "bank_fill"

_JARGON_RE = re.compile(
    r"(трин|квадрат|оппозиц|секстил|соединен|quintile|biquintile|semisquare|"
    r"sesquiquadrate|°|\bлуна\b|\bсолнце\b|\bмеркурий\b|\bвенера\b|\bмарс\b|"
    r"\bюпитер\b|\bсатурн\b|\bуран\b|\bнептун\b|\bплутон\b|"
    r"\bmoon\b|\bsun\b|\bmars\b|\bvenus\b)",
    re.IGNORECASE,
)

_SYS_RU = """Ты пишешь окна «Потока дня» для TodayFlow.

На вход — только реальные timed windows (уже посчитанные часы) + лёгкий контекст дня.
Твоя задача: для каждого driver_id дать человеческое НАЗВАНИЕ окна и короткую ТРАКТОВКУ —
что в это время день хорошо несёт (отдых, дела, контакт, себе, письма, порядок…)
или от чего лучше держаться. Без сюжета конфликта, без сцен, без «сделай / не делай» как шаблона.

Верни ТОЛЬКО JSON:
{
  "schema_version": "day_flow_windows_v1",
  "windows": [
    { "driver_id": "...", "title": "...", "detail": "..." }
  ]
}

Правила:
- ровно те driver_id, что во входе; не добавляй окон; не меняй и не выдумывай часы;
- title — одна короткая строка окна (как подпись на таймлайне);
- detail — 1–2 предложения: почему/для чего это окно (можно упомянуть фазу Луны по-человечески);
- valence во входе: favorable ≈ lean-in, caution ≈ тише / не давить в эту тему;
- без названий планет и аспектов в title/detail; без градусов;
- без conflict / «сила против силы» / ловушек сюжета.
"""


def fingerprint_for_windows(glance_rows: list[dict[str, Any]]) -> str:
    parts = []
    for row in glance_rows:
        parts.append(
            f"{row.get('driver_id')}|{row.get('time_local')}|{row.get('valence')}"
        )
    raw = "\n".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:40]


def _clean(text: Any, *, max_len: int) -> str:
    s = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(s) > max_len:
        s = s[: max_len - 1].rstrip() + "…"
    return s


def _has_jargon(text: str) -> bool:
    return bool(_JARGON_RE.search(text or ""))


def validate_windows_payload(
    payload: dict[str, Any] | None,
    *,
    allowed_ids: set[str],
) -> list[dict[str, str]] | None:
    if not isinstance(payload, dict):
        return None
    if str(payload.get("schema_version") or "") != SCHEMA_VERSION:
        return None
    rows = payload.get("windows")
    if not isinstance(rows, list) or not rows:
        return None
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        did = str(row.get("driver_id") or "").strip()
        if not did or did not in allowed_ids or did in seen:
            continue
        title = _clean(row.get("title"), max_len=90)
        detail = _clean(row.get("detail"), max_len=280)
        if not title or _has_jargon(title) or (detail and _has_jargon(detail)):
            continue
        seen.add(did)
        out.append({"driver_id": did, "title": title, "detail": detail})
    if not out:
        return None
    return out


def load_cached_day_flow_windows(
    db: Session,
    *,
    user_id: int,
    local_date: date,
    fingerprint: str,
) -> dict[str, Any] | None:
    from todayflow_backend.db import models

    day_iso = local_date.isoformat()
    rows = (
        db.query(models.GenerationLog)
        .filter(
            models.GenerationLog.user_id == int(user_id),
            models.GenerationLog.module == MODULE,
            models.GenerationLog.surface == SURFACE,
            models.GenerationLog.status == "success",
        )
        .order_by(models.GenerationLog.id.desc())
        .limit(20)
        .all()
    )
    for row in rows:
        inp = row.input_payload if isinstance(row.input_payload, dict) else {}
        if str(inp.get("fingerprint") or "") != fingerprint:
            continue
        if str(inp.get("target_date") or "") != day_iso:
            continue
        body = row.normalized_response if isinstance(row.normalized_response, dict) else None
        if not body:
            continue
        return dict(body)
    return None


def persist_day_flow_windows(
    db: Session,
    *,
    user_id: int,
    local_date: date,
    fingerprint: str,
    payload: dict[str, Any],
    model: str | None,
) -> None:
    from todayflow_backend.services.learning import get_learning_service

    try:
        get_learning_service().log_generation(
            db,
            module=MODULE,
            surface=SURFACE,
            user_id=int(user_id),
            model=model,
            locale="ru",
            input_payload={
                "target_date": local_date.isoformat(),
                "fingerprint": fingerprint,
                "schema_version": SCHEMA_VERSION,
            },
            normalized_response=payload,
            status="success",
        )
    except Exception:
        logger.debug("day_flow_windows log_generation failed", exc_info=True)


def _kitchen_for_row(
    row: dict[str, Any],
    activations_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    act = activations_by_id.get(str(row.get("driver_id") or "")) or {}
    return {
        "driver_id": str(row.get("driver_id") or ""),
        "time_local": str(row.get("time_local") or ""),
        "valence": str(row.get("valence") or ""),
        "kitchen": {
            "transiting_planet": act.get("transiting_planet"),
            "aspect": act.get("aspect"),
            "natal_point": act.get("natal_point"),
            "rank": act.get("rank"),
        },
    }


def build_kimi_user_payload(
    *,
    glance_rows: list[dict[str, Any]],
    activations: list[dict[str, Any]] | None,
    moon_phase: dict[str, Any] | None,
    profile_light: dict[str, Any] | None,
) -> dict[str, Any]:
    by_id = {
        str(a.get("id") or ""): a
        for a in (activations or [])
        if isinstance(a, dict) and a.get("id")
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "windows": [_kitchen_for_row(r, by_id) for r in glance_rows],
        "moon_phase": moon_phase or {},
        "profile_light": profile_light or {},
    }


def call_day_flow_windows_kimi(
    user_payload: dict[str, Any],
    *,
    allowed_ids: set[str],
) -> tuple[dict[str, Any] | None, str | None]:
    """Returns (validated payload with windows list wrapped, model_id)."""
    from todayflow_backend.core.llm_openai_compatible import (
        chat_completion_text,
        get_openai_compatible_client,
        is_llm_chat_configured,
        resolve_default_chat_model,
        resolve_max_tokens,
    )

    if not is_llm_chat_configured():
        return None, None
    client = get_openai_compatible_client()
    if client is None:
        return None, None
    model = resolve_default_chat_model()
    raw = chat_completion_text(
        client,
        model=model,
        messages=[
            {"role": "system", "content": _SYS_RU},
            {
                "role": "user",
                "content": json.dumps(user_payload, ensure_ascii=False)[:12_000],
            },
        ],
        temperature=0.55,
        max_tokens=resolve_max_tokens(900),
        json_object=True,
    )
    if not raw:
        return None, model
    try:
        parsed = json.loads(raw)
    except Exception:
        # tolerate fenced / trailing noise
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            return None, model
        try:
            parsed = json.loads(m.group(0))
        except Exception:
            return None, model
    windows = validate_windows_payload(parsed if isinstance(parsed, dict) else None, allowed_ids=allowed_ids)
    if not windows:
        return None, model
    return {"schema_version": SCHEMA_VERSION, "windows": windows}, model


def merge_window_copy(
    glance_rows: list[dict[str, Any]],
    overlay: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Apply Kimi titles/details by driver_id; keep bank label when miss."""
    by_id: dict[str, dict[str, str]] = {}
    if isinstance(overlay, dict):
        for w in overlay.get("windows") or []:
            if isinstance(w, dict) and w.get("driver_id"):
                by_id[str(w["driver_id"])] = {
                    "title": str(w.get("title") or "").strip(),
                    "detail": str(w.get("detail") or "").strip(),
                }
    out: list[dict[str, Any]] = []
    for row in glance_rows:
        r = dict(row)
        did = str(r.get("driver_id") or "")
        hit = by_id.get(did)
        if hit and hit.get("title"):
            r["label_short"] = hit["title"]
            r["detail"] = hit.get("detail") or None
            r["copy_source"] = COPY_SOURCE_KIMI
        else:
            r.setdefault("detail", None)
            r["copy_source"] = COPY_SOURCE_BANK
        out.append(r)
    return out


def apply_cached_or_bank(
    db: Session,
    *,
    user_id: int,
    local_date: date,
    glance_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not glance_rows:
        return []
    fp = fingerprint_for_windows(glance_rows)
    cached = load_cached_day_flow_windows(
        db, user_id=user_id, local_date=local_date, fingerprint=fp
    )
    return merge_window_copy(glance_rows, cached)


def ensure_day_flow_windows_for_user(
    db: Session,
    *,
    user: Any,
    local_date: date,
    timezone_name: str,
    locale: str = "ru",
) -> str:
    """No-op: Global Day Engine owns windows. Kimi is not a timeline decision.

    Natal glance clocks remain geometry (`today_glance_timeline_v1`).
    Label fill-empty uses ``apply_cached_or_bank`` only.
    """
    logger.info(
        "day_flow_windows kimi skipped user=%s date=%s — engine owns windows",
        getattr(user, "id", None),
        local_date,
    )
    return "skipped_engine_owns_windows"


def _release_db_transaction(db: Session) -> None:
    """Return the pooled connection before long non-DB work (LLM)."""
    try:
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    try:
        db.expire_all()
    except Exception:
        pass
