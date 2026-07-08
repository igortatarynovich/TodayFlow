"""DayModel v0 — детерминированный слой смысла дня (канон §10 DAY_ENGINE_AND_COHERENCE).

Не вызывает LLM. Строит шесть полей + шкалы и gate из foundation.spine, ритуала,
fusion.scores и опционально internal_profile. Тексты — опорные формулировки для
промпта и объяснимости; пользовательский лонгрид по-прежнему narrative.
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.day_logic_shared_v0 import (
    clip_day_logic_text as _clip,
    foundation_spine_dict,
    fusion_energy_score_int,
    ritual_core_fields,
    spine_text_fields,
)
from todayflow_backend.services.ritual_cue_sanitize import is_garbage_ritual_action_cue

_DIRECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "completion": (
        "заверш",
        "закры",
        "итог",
        "отпуст",
        "снять",
        "дожать",
        "close",
        "finish",
        "wrap",
        "complete",
    ),
    "growth": ("рост", "расшир", "нов", "учиться", "growth", "expand", "learn", "start fresh"),
    "stabilization": ("стабил", "ровн", "устойчив", "steady", "maintain", "ground", "структур"),
    "conflict": ("конфликт", "напряж", "остры", "clash", "tension", "friction"),
    "transition": ("переход", "смена", "pivot", "shift", "перелом"),
}


def _blob(*parts: str) -> str:
    return " ".join(p for p in parts if p).lower()


def _classify_direction(text: str) -> str:
    b = (text or "").lower()
    for direction, needles in _DIRECTION_KEYWORDS.items():
        if any(n in b for n in needles):
            return direction
    return "transition"


def _emotion_band_from_mood(mood: str) -> str:
    m = (mood or "").lower()
    if any(x in m for x in ("тревож", "anxious", "anxiety", "nervous", "panic", "stress")):
        return "distorted"
    if any(x in m for x in ("спокой", "calm", "рівн", "steady")):
        return "stable"
    if mood.strip():
        return "sensitive"
    return "stable"


def _tempo_from_energy(en_score: int) -> str:
    if en_score < 40:
        return "slow"
    if en_score > 65:
        return "fast"
    return "steady"


def _action_type_from_direction(direction: str) -> str:
    if direction == "completion":
        return "finish"
    if direction == "growth":
        return "start"
    if direction == "stabilization":
        return "continue"
    if direction == "conflict":
        return "leave"
    return "continue"


def _week_energy_trend(history: dict[str, Any]) -> str:
    series = history.get("fusion_scores_trailing_7d")
    if not isinstance(series, list) or len(series) < 6:
        return "unknown"
    if history.get("trailing_7d_summary_trustworthy") is False:
        return "unknown"
    vals: list[int] = []
    for item in series[:6]:
        if not isinstance(item, dict):
            continue
        scores = item.get("scores")
        if not isinstance(scores, dict):
            continue
        try:
            vals.append(int(scores.get("energy", 50)))
        except (TypeError, ValueError):
            vals.append(50)
    if len(vals) < 6:
        return "unknown"
    older = sum(vals[3:6]) / 3.0
    newer = sum(vals[0:3]) / 3.0
    delta = newer - older
    if delta >= 4:
        return "rising"
    if delta <= -4:
        return "falling"
    return "steady"


def _temporal_summary_from_history(history: dict[str, Any] | None, *, en: bool) -> dict[str, Any] | None:
    if not isinstance(history, dict) or history.get("contract_version") != "day_history_v0":
        return None
    yesterday = history.get("yesterday")
    if not isinstance(yesterday, dict):
        return None
    delta_raw = history.get("fusion_score_delta_vs_yesterday")
    d_energy = 0
    if isinstance(delta_raw, dict):
        try:
            d_energy = int(delta_raw.get("energy", 0))
        except (TypeError, ValueError):
            d_energy = 0
    delta_trustworthy = history.get("fusion_score_delta_trustworthy") is not False
    week_trend = _week_energy_trend(history)
    y_flow = yesterday.get("day_flow") if isinstance(yesterday.get("day_flow"), dict) else {}
    completions = int(yesterday.get("meaning_completions_total") or 0)
    meaning_active = bool(yesterday.get("meaning_active"))
    y_signals = yesterday.get("meaning_day_signals")
    y_signals_dict = y_signals if isinstance(y_signals, dict) else {}
    evening_done = bool(y_flow.get("evening_completed")) or int(
        y_signals_dict.get("evening_reflection_submitted", 0) or 0
    ) > 0

    parts: list[str] = []
    if delta_trustworthy:
        if d_energy >= 4:
            parts.append(
                "Energy reads higher than yesterday—keep one lane, don't add heroics."
                if en
                else "Ресурс выше, чем вчера — держи одну линию, без героизма."
            )
        elif d_energy <= -4:
            parts.append(
                "Energy is lower than yesterday—short cycles and one finish line."
                if en
                else "Ресурс ниже вчера — короткие циклы и одна доведённая линия."
            )
    if meaning_active:
        if completions >= 2:
            parts.append(
                "Yesterday had Flow steps—you can lean on that momentum gently."
                if en
                else "Вчера были шаги в Flow — можно мягко опереться на инерцию."
            )
        elif evening_done:
            parts.append(
                "Yesterday closed in the evening—today fits continuing the thread."
                if en
                else "Вчера день закрыт вечером — сегодня логично продолжить нить."
            )
        elif completions == 1:
            parts.append(
                "One small step logged yesterday—enough to build on."
                if en
                else "Вчера был один небольшой шаг — этого достаточно, чтобы опереться."
            )
    rex = yesterday.get("reflection_excerpt")
    if isinstance(rex, dict) and rex.get("has_reflection"):
        er = str(rex.get("evening_reflection") or "").strip()
        if er:
            parts.append(
                "Yesterday's evening note is in day_history—honor it without repeating it verbatim."
                if en
                else "Вчерашняя вечерняя заметка есть в day_history — учти её, не цитируй дословно."
            )
    if week_trend == "rising":
        parts.append(
            "Over the past week energy trended up—don't overload the lift."
            if en
            else "За неделю энергия поднималась — не перегружай подъём."
        )
    elif week_trend == "falling":
        parts.append(
            "Energy dipped over the week—protect recovery and one priority."
            if en
            else "За неделю ресурс просел — береги восстановление и один приоритет."
        )

    summary = _clip(" ".join(parts), 320) if parts else (
        "No strong temporal contrast—stay with today's spine."
        if en
        else "Яркого контраста с вчера нет — опирайся на стержень сегодня."
    )
    return {
        "energy_delta_vs_yesterday": d_energy if delta_trustworthy else None,
        "delta_trustworthy": delta_trustworthy,
        "week_energy_trend": week_trend,
        "yesterday_meaning_active": meaning_active,
        "summary": summary,
    }


def build_day_model_v0(
    *,
    foundation: dict[str, Any] | None,
    ritual: dict[str, Any] | None,
    fusion_scores: dict[str, Any] | None,
    intent_slice: dict[str, Any] | None,
    internal_profile: dict[str, Any] | None,
    locale: str,
    history_slice: dict[str, Any] | None = None,
) -> dict[str, Any]:
    en = (locale or "").strip().lower().startswith("en")
    spine = foundation_spine_dict(foundation)
    sf = spine_text_fields(spine)
    axis = sf["axis"]
    best_mode = sf["best_mode"]
    first_move = sf["first_move"]
    main_risk = sf["main_risk"]
    dne = sf["do_not_enter"]

    rc = ritual_core_fields(ritual)
    mood = rc["mood"]
    card = rc["tarot_name_ru"]
    num = rc["numerology_value"]

    en_score = max(0, min(100, fusion_energy_score_int(fusion_scores)))

    blob_axis = _blob(axis, best_mode)
    direction_axis = _classify_direction(blob_axis)
    emotion_mood = _emotion_band_from_mood(mood)
    # Карта/число: слабый сигнал направления (только если ось пустая)
    card_dir = _classify_direction(card) if card else "transition"
    num_dir = _classify_direction(num) if num else "transition"
    aux_dirs = [d for d in (card_dir, num_dir) if d != "transition"]
    if direction_axis == "transition" and aux_dirs:
        direction_axis = aux_dirs[0]

    tempo_label = _tempo_from_energy(en_score)
    action_type = _action_type_from_direction(direction_axis)

    # Tension: конфликт темпа/энергии и оси, либо эмоции vs стабилизация
    tension_reasons: list[str] = []
    if tempo_label == "fast" and direction_axis in ("completion", "stabilization"):
        tension_reasons.append(
            "High pace signal vs a day that wants closure or steadiness."
            if en
            else "Высокий темп/ресурс при дне про завершение или ровность — риск распыления."
        )
    if emotion_mood == "distorted" and direction_axis == "stabilization":
        tension_reasons.append(
            "Sensitive state vs a day that needs a steady structure."
            if en
            else "Чувствительное состояние при дне про устойчивость — легче сорваться в реакции."
        )
    if direction_axis != card_dir and card_dir != "transition" and card:
        tension_reasons.append(
            "Ritual symbol and daily spine pull in different directions."
            if en
            else "Символ карты и стержень дня тянут в разные стороны."
        )
    tension_summary = (
        " ".join(tension_reasons)[:420]
        if tension_reasons
        else (
            "Sources mostly align; keep one clear lane and avoid extra promises."
            if en
            else "Источники в основном согласованы; держи одну ясную линию и не добавляй лишних обещаний."
        )
    )

    vector_summary = _clip(axis or best_mode, 360) if (axis or best_mode) else (
        "Hold one clear thread for today." if en else "Держи одну ясную нить дня."
    )

    fm_clean = (first_move or "").strip()
    if is_garbage_ritual_action_cue(fm_clean):
        fm_clean = ""
    opportunity_summary = _clip(
        fm_clean or axis or ("One bounded step today." if en else "Один ограниченный шаг сегодня."),
        320,
    )

    risk_parts: list[str] = []
    if main_risk:
        risk_parts.append(_clip(main_risk, 280))
    if dne:
        risk_parts.append(_clip(dne, 200))
    if emotion_mood == "distorted":
        risk_parts.append(
            "If you speed up when emotions spike, you will trade clarity for noise."
            if en
            else "Если ускоряться на фоне эмоций — потеряешь ясность."
        )
    if isinstance(internal_profile, dict):
        sba = internal_profile.get("surface_behavior_aggregates")
        if isinstance(sba, dict):
            hints = sba.get("pattern_hints")
            if isinstance(hints, list) and hints:
                risk_parts.append(_clip(str(hints[0]), 220))
    risk_summary = _clip(" ".join(risk_parts), 480) if risk_parts else (
        "Overloading parallel tracks when the day needs one finish line."
        if en
        else "Параллельные «надо» вместо одной доведённой линии."
    )

    tempo_summary = (
        f"Energy score {en_score}/100 → keep tempo {tempo_label}: short cycles, no heroics."
        if en
        else f"Ресурс {en_score}/100 — темп «{tempo_label}»: короткие циклы, без героизма."
    )

    strat_parts = [
        f"Vector={direction_axis}: {vector_summary[:200]}",
        f"Tempo={tempo_label}.",
        f"Mitigate risk: {risk_summary[:220]}",
    ]
    if fm_clean:
        strat_parts.insert(1, f"Primary move: {fm_clean[:160]}.")
    strategy_summary = _clip(" ".join(strat_parts), 520)

    intent_line = ""
    if isinstance(intent_slice, dict):
        intent_line = str(intent_slice.get("what_matters_line") or "").strip()[:200]

    gate_vector = bool(
        direction_axis != "transition"
        or len(blob_axis) > 16
        or len(fm_clean) > 6
        or len(vector_summary) > 36
    )
    gate_risk = bool(len(risk_summary.strip()) > 12)

    temporal = _temporal_summary_from_history(history_slice, en=en)

    out: dict[str, Any] = {
        "contract_version": "day_model_v0",
        "locale_hint": "en" if en else "ru",
        "scales": {
            "direction": direction_axis,
            "energy_0_100": en_score,
            "emotions": emotion_mood,
            "action_type": action_type,
            "tempo": tempo_label,
            "sources_blob": _clip(blob_axis + " | " + card + " | " + num, 200),
        },
        "vector": {"direction": direction_axis, "summary": vector_summary},
        "tension": {"summary": tension_summary, "signals": tension_reasons[:3] or ["aligned"]},
        "opportunity": {"summary": opportunity_summary, "intent_echo": intent_line or None},
        "risk": {"summary": risk_summary},
        "tempo": {"label": tempo_label, "summary": tempo_summary},
        "strategy": {"summary": strategy_summary, "one_focus": _clip(fm_clean or opportunity_summary, 200)},
        "gate": {
            "vector_defined": gate_vector,
            "tension_defined": True,
            "risk_defined": gate_risk,
        },
    }
    if temporal:
        out["temporal"] = temporal
    return out
