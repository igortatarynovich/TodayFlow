"""DE-9: детерминированный слой «вчера + тренд» для DayContext (без LLM)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from todayflow_backend.db.models import DayConnection, MeaningEvent
from todayflow_backend.services.fusion_scores import compute_fusion_scores_and_flow_signals_map_for_dates
from todayflow_backend.services.guide_flow_signals import GUIDE_MEANING_COMPLETION_EVENT_TYPES

# DE-9 v1.4: смысловые события по дням (серверные счётчики, не доверяем клиенту).
HISTORY_MEANING_ENGAGEMENT_TYPES: tuple[str, ...] = (
    "sphere_opened",
    "action_option_selected",
    "evening_reflection_submitted",
    "mood_selected",
)
HISTORY_MEANING_SIGNAL_TYPES: tuple[str, ...] = tuple(
    dict.fromkeys((*GUIDE_MEANING_COMPLETION_EVENT_TYPES, *HISTORY_MEANING_ENGAGEMENT_TYPES))
)


def _fetch_meaning_signal_counts_by_date(
    db: Session,
    *,
    user_id: int,
    dates: list[date],
) -> dict[date, dict[str, int]]:
    if not dates:
        return {}
    rows = (
        db.query(
            MeaningEvent.local_date,
            MeaningEvent.event_type,
            func.count(MeaningEvent.id),
        )
        .filter(
            MeaningEvent.user_id == user_id,
            MeaningEvent.local_date.in_(dates),
            MeaningEvent.event_type.in_(HISTORY_MEANING_SIGNAL_TYPES),
        )
        .group_by(MeaningEvent.local_date, MeaningEvent.event_type)
        .all()
    )
    out: dict[date, dict[str, int]] = {d: {} for d in dates}
    for ld, et, cnt in rows:
        if ld in out and et:
            out[ld][str(et)] = int(cnt or 0)
    return out


def _completions_total(signals: dict[str, int]) -> int:
    return sum(int(signals.get(t, 0) or 0) for t in GUIDE_MEANING_COMPLETION_EVENT_TYPES)


def _meaning_day_active(signals: dict[str, int], day_flow: dict[str, bool] | None) -> bool:
    if isinstance(day_flow, dict) and any(day_flow.values()):
        return True
    if _completions_total(signals) > 0:
        return True
    return any(int(signals.get(t, 0) or 0) > 0 for t in HISTORY_MEANING_ENGAGEMENT_TYPES)


def _clip_text(text: str | None, *, max_len: int = 220) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def _build_reflection_excerpt(dc: DayConnection | None) -> dict[str, Any] | None:
    """DE-9 v1.5: урезанные тексты вчерашнего DayConnection для LLM/UI (только сервер, caps)."""
    if dc is None:
        return None
    er = _clip_text(dc.evening_reflection, max_len=220)
    mi = _clip_text(dc.morning_intention, max_len=160)
    obs_raw = dc.evening_observations if isinstance(dc.evening_observations, dict) else {}
    obs: dict[str, str] = {}
    for k in ("noticed", "hardest", "easier_than_expected"):
        v = _clip_text(str(obs_raw.get(k) or ""), max_len=140)
        if v:
            obs[k] = v
    q = str(dc.question_of_day_answer or "").strip()[:80]
    qd = str(dc.quick_decision_answer or "").strip()[:16]
    if not er and not mi and not obs and not q and not qd:
        return None
    return {
        "contract_version": "day_connection_excerpt_v0",
        "evening_reflection": er or None,
        "evening_observations": obs or None,
        "morning_intention": mi or None,
        "question_of_day_answer": q or None,
        "quick_decision_answer": qd or None,
        "has_reflection": bool(er or obs),
    }


def _axis_int(scores: dict[str, Any] | None, key: str, *, default: int = 50) -> int:
    if not isinstance(scores, dict):
        return default
    try:
        return int(scores.get(key, default))
    except (TypeError, ValueError):
        return default


def build_history_layer_v0(
    db: Session,
    *,
    user_id: int,
    target_date: date,
    today_fusion_scores: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Вчерашние fusion scores + флаги DayConnection; серия за 7 календарных дней назад (включая вчера);
    сводка avg/min/max; дельта относительно вчера по текущим scores из fusion «сегодня».
    O7: `fusion_score_delta_trustworthy` / `yesterday_fusion_has_flow_markers` — были ли вчера отметки Flow,
    на которых осмысленно строится сравнение с сегодняшними баллами.
    """
    yesterday = target_date - timedelta(days=1)
    trailing_dates = [target_date - timedelta(days=i) for i in range(1, 8)]
    score_map, flow_signal_map = compute_fusion_scores_and_flow_signals_map_for_dates(db, user_id, trailing_dates)
    meaning_by_date = _fetch_meaning_signal_counts_by_date(db, user_id=user_id, dates=trailing_dates)

    dc_y = (
        db.query(DayConnection)
        .filter(DayConnection.user_id == user_id, DayConnection.date == yesterday)
        .first()
    )
    dc_by_date = {
        row.date: row
        for row in db.query(DayConnection)
        .filter(DayConnection.user_id == user_id, DayConnection.date.in_(trailing_dates))
        .all()
    }
    default_scores = {"energy": 50, "emotional_balance": 50, "focus": 50}
    y_scores = dict(score_map.get(yesterday, default_scores))

    y_flow: dict[str, bool] | None = None
    if dc_y:
        y_flow = {
            "morning_completed": bool(dc_y.morning_completed),
            "day_completed": bool(dc_y.day_completed),
            "evening_completed": bool(dc_y.evening_completed),
        }

    series: list[dict[str, Any]] = []
    trailing_7d_meaning_active_days = 0
    for d in trailing_dates:
        day_signals = meaning_by_date.get(d, {})
        day_flow_flags: dict[str, bool] | None = None
        dc_day = dc_by_date.get(d)
        if dc_day:
            day_flow_flags = {
                "morning_completed": bool(dc_day.morning_completed),
                "day_completed": bool(dc_day.day_completed),
                "evening_completed": bool(dc_day.evening_completed),
            }
        meaning_active = _meaning_day_active(day_signals, day_flow_flags)
        if meaning_active:
            trailing_7d_meaning_active_days += 1
        series.append(
            {
                "date": d.isoformat(),
                "scores": dict(score_map.get(d, default_scores)),
                "meaning_completions_total": _completions_total(day_signals),
                "meaning_active": meaning_active,
            }
        )

    def _agg(axis: str) -> dict[str, Any]:
        vals: list[int] = []
        for d in trailing_dates:
            raw = score_map.get(d, default_scores).get(axis, 50)
            try:
                vals.append(int(raw))
            except (TypeError, ValueError):
                vals.append(50)
        return {
            "avg": round(sum(vals) / len(vals), 1),
            "min": min(vals),
            "max": max(vals),
            "days": len(vals),
        }

    te = _axis_int(today_fusion_scores, "energy")
    tbal = _axis_int(today_fusion_scores, "emotional_balance")
    tf = _axis_int(today_fusion_scores, "focus")

    ye = int(y_scores.get("energy", 50))
    ybal = int(y_scores.get("emotional_balance", 50))
    yf = int(y_scores.get("focus", 50))

    yesterday_has_flow = bool(flow_signal_map.get(yesterday, False))
    trailing_7d_flow_days = sum(1 for d in trailing_dates if flow_signal_map.get(d, False))
    trailing_7d_summary_trustworthy = trailing_7d_flow_days > 0

    y_meaning_signals = {
        k: v for k, v in meaning_by_date.get(yesterday, {}).items() if int(v or 0) > 0
    }
    y_meaning_active = _meaning_day_active(y_meaning_signals, y_flow)
    y_reflection = _build_reflection_excerpt(dc_y)

    return {
        "contract_version": "day_history_v0",
        "yesterday": {
            "date": yesterday.isoformat(),
            "fusion_scores": y_scores,
            "day_flow": y_flow,
            "meaning_day_signals": y_meaning_signals,
            "meaning_completions_total": _completions_total(y_meaning_signals),
            "meaning_active": y_meaning_active,
            "reflection_excerpt": y_reflection,
        },
        "fusion_scores_trailing_7d": series,
        "trailing_7d_summary": {
            "energy": _agg("energy"),
            "emotional_balance": _agg("emotional_balance"),
            "focus": _agg("focus"),
        },
        "fusion_score_delta_vs_yesterday": {
            "energy": te - ye,
            "emotional_balance": tbal - ybal,
            "focus": tf - yf,
        },
        # O7: клиент не показывает «к сегодня: ±…», если вчера не было отметок Flow под формулу fusion.
        "yesterday_fusion_has_flow_markers": yesterday_has_flow,
        "fusion_score_delta_trustworthy": yesterday_has_flow,
        # O7: недельная сводка по умолчанию из дефолтных 50 — не показывать без хотя бы одного дня с отметками.
        "trailing_7d_flow_days": trailing_7d_flow_days,
        "trailing_7d_summary_trustworthy": trailing_7d_summary_trustworthy,
        "trailing_7d_meaning_active_days": trailing_7d_meaning_active_days,
    }
