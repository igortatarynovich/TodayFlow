"""UMTS §3.5 — DayModel-derived recommendation alternates for CUM v0."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.db.models import TarotDraw
from todayflow_backend.services.day_model_v1_aggregator import (
    DayModelAggregationError,
    aggregate_day_model_v1,
)
from todayflow_backend.services.day_model_v1_content_mapper import (
    map_day_model_interpretation_to_content_keys,
)
from todayflow_backend.services.day_model_v1_content_resolver import (
    resolve_content_entries_from_mapping,
)
from todayflow_backend.services.day_model_v1_interpreter import interpret_day_model_v1
from todayflow_backend.services.numerology import get_numerology_service
from todayflow_backend.services.tarot import TarotService

CUM_DAY_MODEL_ALTERNATES_V0_CONTRACT = "cum_day_model_alternates_v0"
MAX_ALTERNATES = 2
DEFAULT_ACTION_PLANET = "astrology.planet.mars"

_ALTERNATE_SLOT_ORDER = ("action_hint", "tempo_hint", "reflection_hint")

_ALTERNATE_TEXT_RU: dict[str, str] = {
    "plan": "Сначала запиши 3 шага — потом начни первый.",
    "execute": "Закрой один выбранный кусок работы до конца.",
    "adapt": "Скорректируй план, если условия изменились — один раз за день.",
    "pause": "Не форсируй действие: дождись ясности или одного сигнала.",
    "slow_down": "Замедли темп: один шаг за раз, без спешки.",
    "keep_steady": "Держи ровный темп — без резких переключений.",
    "move": "Сделай маленький конкретный шаг вперёд сегодня.",
    "accelerate": "Ускорь: заверши одну отложенную задачу до вечера.",
    "light": "5 минут записей вечером — что сработало и что нет.",
    "deep": "20 минут размышлений: что важнее всего на завтра?",
}

_TIMING_HINT_RU: dict[str, str] = {
    "action_hint": "сегодня",
    "tempo_hint": "в течение дня",
    "reflection_hint": "вечером",
}

_MEASURABLE_RU: dict[str, str] = {
    "action_hint": "один завершённый шаг",
    "tempo_hint": "темп замечен и соблюдён",
    "reflection_hint": "короткая запись сделана",
}


def _sign_name_to_entity_code(sign_name: str | None) -> str | None:
    if not isinstance(sign_name, str) or not sign_name.strip():
        return None
    slug = sign_name.strip().lower().replace(" ", "_")
    return f"astrology.sign.{slug}"


def _tarot_entity_code(*, user_id: int, reference_date: date, db: Session | None) -> str:
    if db is not None:
        draw = (
            db.query(TarotDraw)
            .filter(TarotDraw.user_id == user_id, TarotDraw.draw_date == reference_date)
            .order_by(TarotDraw.created_at.desc())
            .first()
        )
        if draw and draw.card_id is not None:
            return f"tarot.major.{int(draw.card_id):02d}"

    cards = astrology_ref.tarot_major_arcana()
    seed = TarotService._stable_seed(user_id, reference_date.isoformat())
    card = cards[seed % len(cards)]
    return f"tarot.major.{int(card['id']):02d}"


def _numerology_entity_code(reference_date: date) -> str | None:
    insight = get_numerology_service().daily_number(reference_date=reference_date)
    if not insight or not insight.number:
        return None
    day_number = insight.number.reduced_value or insight.number.value
    if not isinstance(day_number, int) or not 1 <= day_number <= 9:
        return None
    return f"numerology.personal_day.{day_number}"


def resolve_day_model_entity_codes_v0(
    *,
    user_id: int,
    reference_date: date,
    core_profile: dict[str, Any] | None,
    db: Session | None = None,
) -> dict[str, str] | None:
    """Resolve entity codes for aggregate_day_model_v1; None when astrology leg unavailable."""
    astro = core_profile.get("astro") if isinstance(core_profile, dict) else {}
    natal_summary = (
        core_profile.get("natal_summary") if isinstance(core_profile, dict) else {}
    )
    sun_sign = None
    if isinstance(astro, dict):
        sun_sign = astro.get("sun_sign")
    if not sun_sign and isinstance(natal_summary, dict):
        sun_sign = natal_summary.get("sun_sign")

    sign_code = _sign_name_to_entity_code(sun_sign if isinstance(sun_sign, str) else None)
    numerology_code = _numerology_entity_code(reference_date)
    if not sign_code or not numerology_code:
        return None

    return {
        "tarot_entity_code": _tarot_entity_code(user_id=user_id, reference_date=reference_date, db=db),
        "numerology_entity_code": numerology_code,
        "astrology_planet_code": DEFAULT_ACTION_PLANET,
        "astrology_sign_code": sign_code,
    }


def _content_key_suffix(content_key: str) -> str:
    return content_key.rsplit(".", 1)[-1]


def _alternate_text_ru(content_key: str, entry: dict[str, Any]) -> str:
    suffix = _content_key_suffix(content_key)
    if suffix in _ALTERNATE_TEXT_RU:
        return _ALTERNATE_TEXT_RU[suffix]
    medium = entry.get("text_medium")
    if isinstance(medium, str) and medium.strip():
        return medium.strip()[:280]
    short = entry.get("text_short")
    if isinstance(short, str) and short.strip():
        return short.strip()[:280]
    return content_key


def _entry_to_alternate_recommendation(*, entry: dict[str, Any], slot: str) -> dict[str, Any]:
    content_key = str(entry.get("key") or "")
    suffix = _content_key_suffix(content_key)
    return {
        "id": f"rec-dm-{suffix[:48]}",
        "text": _alternate_text_ru(content_key, entry),
        "timing_hint": _TIMING_HINT_RU.get(slot),
        "measurable": _MEASURABLE_RU.get(slot),
        "source": "day_model",
        "evidence_atom_ids": [],
        "knowledge_type_gate": "pattern",
    }


def build_day_model_recommendation_alternates_v0(
    *,
    user_id: int,
    reference_date: date,
    core_profile: dict[str, Any] | None = None,
    db: Session | None = None,
    entity_codes: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Up to 2 alternates from DayModel content slots (no LLM)."""
    codes = entity_codes or resolve_day_model_entity_codes_v0(
        user_id=user_id,
        reference_date=reference_date,
        core_profile=core_profile,
        db=db,
    )
    if not codes:
        return []

    try:
        day_model = aggregate_day_model_v1(**codes, require_all_domains=True)
    except DayModelAggregationError:
        return []

    if day_model.get("degraded"):
        return []

    interpretation = interpret_day_model_v1(day_model)
    if interpretation.get("reflection_mode") == "none":
        slot_order = ("action_hint", "tempo_hint")
    else:
        slot_order = _ALTERNATE_SLOT_ORDER

    mapping = map_day_model_interpretation_to_content_keys(interpretation)
    resolution = resolve_content_entries_from_mapping(mapping)
    entries_by_slot = resolution.get("entries_by_slot") if isinstance(resolution, dict) else {}
    if not isinstance(entries_by_slot, dict):
        return []

    alternates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for slot in slot_order:
        slot_entries = entries_by_slot.get(slot) or []
        if not isinstance(slot_entries, list):
            continue
        for entry in slot_entries:
            if not isinstance(entry, dict):
                continue
            rec = _entry_to_alternate_recommendation(entry=entry, slot=slot)
            if rec["id"] in seen_ids:
                continue
            seen_ids.add(rec["id"])
            alternates.append(rec)
            if len(alternates) >= MAX_ALTERNATES:
                return alternates
    return alternates
