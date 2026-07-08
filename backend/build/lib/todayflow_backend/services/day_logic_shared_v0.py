"""Общие детерминированные куски для `day_narrative_brief_v0` и `day_model_v0` (без LLM)."""

from __future__ import annotations

import re
from typing import Any

_SLUG_TOKEN = re.compile(r"^[a-z][a-z0-9_]{0,24}$")


def humanize_day_focus_key(key: str | None) -> str:
    """Служебные ключи прогноза/рекомендаций → короткая русская формулировка (не для логики, только для текста)."""
    raw = (key or "").strip()
    k = raw.lower()
    mapping = {
        "general": "общий фокус дня",
        "overall": "общий фокус дня",
        "mixed": "несколько тем сразу",
        "none": "без узкой темы",
        "love": "любовь и близость",
        "family": "семья и дом",
        "home": "семья и дом",
        "career": "работа и карьера",
        "work": "работа и карьера",
        "money": "деньги и границы",
        "body": "тело и восстановление",
        "health": "тело и восстановление",
        "dialogue": "смысл и коммуникация",
        "communication": "смысл и коммуникация",
        "identity": "линия про себя",
        "self": "линия про себя",
    }
    if k in mapping:
        return mapping[k]
    if _SLUG_TOKEN.fullmatch(k):
        return "узкая тема дня"
    return raw or "узкая тема дня"


def humanize_day_direction_ru(direction: str | None) -> str:
    """Внутренний классификатор day_model (vector) → фраза для ситуации в guide_decision."""
    d = (direction or "").strip().lower()
    m = {
        "completion": "закрытие и завершение линий",
        "growth": "рост и новые шаги",
        "stabilization": "стабильность и опора",
        "conflict": "напряжение и границы",
        "transition": "переход и перестройка",
    }
    return m.get(d, "переход и перестройка")


def humanize_day_direction_en(direction: str | None) -> str:
    d = (direction or "").strip().lower()
    m = {
        "completion": "closing and finishing open threads",
        "growth": "growth and new steps",
        "stabilization": "stability and grounding",
        "conflict": "tension and boundaries",
        "transition": "transition and recalibration",
    }
    return m.get(d, "transition and recalibration")


def clip_day_logic_text(s: str, max_len: int) -> str:
    t = (s or "").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def foundation_spine_dict(foundation: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(foundation, dict):
        return {}
    sp = foundation.get("spine")
    return sp if isinstance(sp, dict) else {}


def spine_text_fields(spine: dict[str, Any]) -> dict[str, str]:
    return {
        "axis": str(spine.get("day_axis") or spine.get("best_mode") or "").strip(),
        "best_mode": str(spine.get("best_mode") or "").strip(),
        "first_move": str(spine.get("first_move") or "").strip(),
        "main_risk": str(spine.get("main_risk") or "").strip(),
        "do_not_enter": str(spine.get("do_not_enter") or "").strip(),
    }


def fusion_energy_score_int(scores: dict[str, Any] | None, *, default: int = 50) -> int:
    if not isinstance(scores, dict):
        return default
    try:
        return int(scores.get("energy") or default)
    except (TypeError, ValueError):
        return default


def ritual_core_fields(ritual: dict[str, Any] | None) -> dict[str, Any]:
    r = ritual if isinstance(ritual, dict) else {}
    return {
        "tarot_name_ru": str(r.get("tarot_name_ru") or "").strip(),
        "tarot_main_id": r.get("tarot_main_id"),
        "numerology_value": str(r.get("numerology_value") or "").strip(),
        "mood": str(r.get("mood") or "").strip(),
        "head_topic": str(r.get("head_topic") or "").strip(),
    }
