"""Агрегаты поверхности Today из `meaning_events` (DE-5, без ML).

Используются в `DayContext.layers.behavior_patterns` и в `learning_context`.
После снятия validation UI (2026-07-05) опирается на поведение: mood, actions,
proximity choices (sphere_feedback), questions, practices — не echo/confirm формы.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from todayflow_backend.db import models

_PAYLOAD_SCAN_TYPES = frozenset(
    {
        "mood_selected",
        "head_topic_selected",
        "sphere_opened",
        "tarot_selected",
        "action_option_selected",
        "sphere_feedback",
        "number_selected",
        "day_focus_outcome",
        "compatibility_echo",
        "compatibility_scenario_switch",
        "compatibility_topic_select",
        "compatibility_view",
        "guidance_ask",
    }
)

_HONEST_STEP_LABELS: dict[str, str] = {
    "talk": "разговор",
    "work": "работа",
    "money": "деньги",
    "relations": "отношения",
    "body": "тело / энергия",
    "unknown": "пока не знаю",
}

_GUIDANCE_TEXT_TOPIC_NEEDLES: dict[str, tuple[str, ...]] = {
    "работа": ("работ", "проект", "задач", "дел", "карьер", "коллег"),
    "деньги": ("деньг", "доход", "финанс", "оплат", "бюдж", "зарплат"),
    "отношения": ("отнош", "партнер", "люб", "контакт", "разговор", "брак"),
    "семья": ("сем", "дом", "ребен", "родител", "близк"),
    "состояние": ("устал", "энерг", "стресс", "состоя", "трев", "спокой", "выгор"),
    "решение": ("реш", "выбор", "сомне", "менять", "остав"),
}

_PROXIMITY_LABELS: dict[str, str] = {
    "wait": "подождать",
    "see_differently": "посмотреть иначе",
    "first_step": "сделать первый шаг",
    "unsure": "пока не ясно",
    "pause": "пауза",
    "move": "движение",
    "both": "и то, и другое",
    "clarity": "ясность",
    "patience": "терпение",
}


def _payload_dict(raw: Any) -> dict[str, Any]:
    return raw if isinstance(raw, dict) else {}


def _payload_str(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        val = payload.get(key)
        if val is None:
            continue
        s = str(val).strip()
        if s and s.lower() != "null":
            return s[:120]
    return ""


def _proximity_label(choice_id: str) -> str:
    return _PROXIMITY_LABELS.get(choice_id, choice_id.replace("_", " "))


def _honest_step_label(step_id: str) -> str:
    return _HONEST_STEP_LABELS.get(step_id, step_id.replace("_", " "))


def _guidance_semantic_themes(*, question: str, lane: str) -> list[str]:
    """Semantic top-K buckets from guidance question (no LLM)."""
    themes: list[str] = []
    lane_slug = lane.strip().lower()
    if lane_slug:
        themes.append(f"lane:{lane_slug}")
    q = question.strip().lower()
    if q:
        for topic, needles in _GUIDANCE_TEXT_TOPIC_NEEDLES.items():
            if any(needle in q for needle in needles):
                themes.append(f"topic:{topic}")
    return themes


def build_meaning_surface_patterns_v0(
    db: Session,
    *,
    user_id: int,
    reference_date: date,
    window_days: int = 28,
) -> dict[str, Any] | None:
    """Сводка за окно [reference_date - window_days + 1, reference_date]. None если событий нет."""
    wd = max(7, min(60, int(window_days)))
    end = reference_date
    start = end - timedelta(days=wd - 1)

    total = (
        db.query(func.count(models.MeaningEvent.id))
        .filter(
            models.MeaningEvent.user_id == user_id,
            models.MeaningEvent.local_date >= start,
            models.MeaningEvent.local_date <= end,
        )
        .scalar()
    )
    if not total:
        return None

    type_rows = (
        db.query(models.MeaningEvent.event_type, func.count().label("cnt"))
        .filter(
            models.MeaningEvent.user_id == user_id,
            models.MeaningEvent.local_date >= start,
            models.MeaningEvent.local_date <= end,
        )
        .group_by(models.MeaningEvent.event_type)
        .order_by(func.count().desc())
        .limit(24)
        .all()
    )
    by_event_type: list[dict[str, Any]] = [{"event_type": str(et), "count": int(c or 0)} for et, c in type_rows]
    type_counts: Counter[str] = Counter({str(et): int(c or 0) for et, c in type_rows})

    mood_c: Counter[str] = Counter()
    topic_c: Counter[str] = Counter()
    sphere_c: Counter[str] = Counter()
    action_idx_c: Counter[str] = Counter()
    action_kind_c: Counter[str] = Counter()
    proximity_c: Counter[str] = Counter()
    proximity_target_c: Counter[str] = Counter()
    focus_outcome_c: Counter[str] = Counter()
    honest_step_c: Counter[str] = Counter()
    guidance_lane_c: Counter[str] = Counter()
    guidance_semantic_c: Counter[str] = Counter()
    tarot_main = 0
    tarot_clarifier = 0
    tarot_applied = 0
    compat_format_c: Counter[str] = Counter()
    compat_echo_c: Counter[str] = Counter()
    compat_tone_c: Counter[str] = Counter()

    detail_rows = (
        db.query(models.MeaningEvent.event_type, models.MeaningEvent.payload)
        .filter(
            models.MeaningEvent.user_id == user_id,
            models.MeaningEvent.local_date >= start,
            models.MeaningEvent.local_date <= end,
            models.MeaningEvent.event_type.in_(tuple(_PAYLOAD_SCAN_TYPES)),
        )
        .order_by(models.MeaningEvent.id.desc())
        .limit(4000)
        .all()
    )
    for et, raw_pl in detail_rows:
        pl = _payload_dict(raw_pl)
        if et == "mood_selected":
            mid = _payload_str(pl, "mood_id", "mood")
            if mid:
                mood_c[mid] += 1
        elif et == "head_topic_selected":
            tid = _payload_str(pl, "topic_id", "head_topic")
            if tid:
                topic_c[tid] += 1
        elif et == "sphere_opened":
            sid = _payload_str(pl, "sphere_id", "today_sphere_opened")
            if sid:
                sphere_c[sid] += 1
        elif et == "action_option_selected":
            idx = pl.get("action_option_index")
            if idx is not None:
                action_idx_c[str(idx)] += 1
            action_kind = _payload_str(pl, "action")
            if action_kind:
                action_kind_c[action_kind] += 1
        elif et == "sphere_feedback":
            choice = _payload_str(pl, "proximity_choice")
            if choice:
                proximity_c[choice] += 1
            target = _payload_str(pl, "target")
            if target and choice:
                proximity_target_c[f"{target}:{choice}"] += 1
            honest = _payload_str(pl, "tarot_honest_step", "honest_step")
            if honest and honest.lower() not in {"unset", "null", "unknown"}:
                honest_step_c[honest] += 1
        elif et == "guidance_ask":
            lane = _payload_str(pl, "lane")
            if lane:
                guidance_lane_c[lane] += 1
            question = _payload_str(pl, "question")
            for theme in _guidance_semantic_themes(question=question, lane=lane):
                guidance_semantic_c[theme] += 1
        elif et == "day_focus_outcome":
            outcome = _payload_str(pl, "outcome", "day_focus_outcome")
            if outcome:
                focus_outcome_c[outcome] += 1
        elif et == "tarot_selected":
            if pl.get("applied_to_today") is True:
                tarot_applied += 1
                continue
            role = str(pl.get("role") or "").strip().lower()
            if role == "clarifier":
                tarot_clarifier += 1
            else:
                tarot_main += 1
        elif et == "compatibility_echo":
            echo_val = _payload_str(pl, "echo")
            if echo_val:
                compat_echo_c[echo_val] += 1
            fmt = _payload_str(pl, "format_id", "scenario_id")
            if fmt:
                compat_format_c[fmt] += 1
            tone = _payload_str(pl, "tone_mode")
            if tone:
                compat_tone_c[tone] += 1
        elif et in {"compatibility_scenario_switch", "compatibility_topic_select", "compatibility_view"}:
            fmt = _payload_str(pl, "format_id", "to_scenario_id", "scenario_id", "selection_id")
            if fmt:
                compat_format_c[fmt] += 1
            tone = _payload_str(pl, "tone_mode")
            if tone:
                compat_tone_c[tone] += 1

    def _rank(counter: Counter[str], n: int) -> list[dict[str, Any]]:
        return [{"id": k, "count": c} for k, c in counter.most_common(n)]

    guidance_asks = int(type_counts.get("guidance_ask", 0))
    practices_done = int(type_counts.get("practice_completed", 0))
    tarot_deepen = int(type_counts.get("tarot_deepen_started", 0))
    support_picks = int(type_counts.get("support_selected", 0))
    number_picks = int(type_counts.get("number_selected", 0))
    day_promise_sets = int(action_kind_c.get("day_promise_set", 0))

    tags: dict[str, Any] = {
        "top_mood_ids": _rank(mood_c, 5),
        "top_head_topics": _rank(topic_c, 5),
        "top_sphere_ids": _rank(sphere_c, 5),
        "top_action_option_indices": _rank(action_idx_c, 4),
        "top_action_kinds": _rank(action_kind_c, 5),
        "top_honest_step_ids": _rank(honest_step_c, 6),
        "day_promise_sets": day_promise_sets,
        "top_guidance_lanes": _rank(guidance_lane_c, 5),
        "top_guidance_themes": _rank(guidance_semantic_c, 8),
        "focus_sessions_started": int(type_counts.get("focus_started", 0)),
        "evening_reflections_submitted": int(type_counts.get("evening_reflection_submitted", 0)),
        "guidance_questions_asked": guidance_asks,
        "practices_completed": practices_done,
        "tarot_deepen_sessions": tarot_deepen,
        "support_selections": support_picks,
        "number_day_engagements": number_picks,
        "ritual_proximity": {
            "top_choices": _rank(proximity_c, 5),
            "top_target_choices": _rank(proximity_target_c, 5),
        },
        "day_focus_outcomes": _rank(focus_outcome_c, 4),
        "tarot_engagement": {
            "main_picks": tarot_main,
            "clarifier_picks": tarot_clarifier,
            "applied_to_today": tarot_applied,
        },
        "compatibility_engagement": {
            "echo_yes": int(compat_echo_c.get("yes", 0)),
            "echo_partial": int(compat_echo_c.get("partial", 0)),
            "echo_no": int(compat_echo_c.get("no", 0)),
            "top_format_ids": _rank(compat_format_c, 5),
            "top_tone_modes": _rank(compat_tone_c, 3),
            "scenario_switches": int(type_counts.get("compatibility_scenario_switch", 0)),
            "deep_opens": int(type_counts.get("compatibility_deep_open", 0)),
            "views": int(type_counts.get("compatibility_view", 0)),
        },
    }

    hints: list[str] = []
    if int(type_counts.get("focus_started", 0)) >= 4:
        hints.append("Часто отмечает старт фокуса на шаге дня (короткие слоты).")
    if int(type_counts.get("evening_reflection_submitted", 0)) >= 3:
        hints.append("Регулярно сохраняет вечернюю рефлексию в Today.")
    if mood_c:
        mid, mc = mood_c.most_common(1)[0]
        if mc >= 3:
            hints.append(f"В ритуале чаще выбирает настроение «{mid}» ({mc} раз).")
    if sphere_c:
        sid, sc = sphere_c.most_common(1)[0]
        if sc >= 3:
            hints.append(f"Чаще открывает сферу «{sid}» на главном экране ({sc}).")
    if int(type_counts.get("tarot_selected", 0)) >= 5:
        hints.append("Активно проходит блок карты дня в ритуале.")
    if proximity_c:
        pid, pc = proximity_c.most_common(1)[0]
        if pc >= 3:
            hints.append(
                f"После символов дня чаще выбирает «{_proximity_label(pid)}» ({pc} раз)."
            )
    if day_promise_sets >= 2:
        hints.append(f"Регулярно формулирует обещание дня ({day_promise_sets} раз).")
    if honest_step_c:
        hid, hc = honest_step_c.most_common(1)[0]
        if hc >= 2:
            hints.append(
                f"Честный шаг дня чаще про «{_honest_step_label(hid)}» ({hc} раз)."
            )
    if guidance_asks >= 2:
        hints.append(f"Задаёт вопросы в разделе «Вопросы» ({guidance_asks} за окно).")
    if guidance_semantic_c:
        gt, gc = guidance_semantic_c.most_common(1)[0]
        if gc >= 2:
            hints.append(f"В вопросах повторяется тема «{gt.replace(':', ' / ')}» ({gc}).")
    if practices_done >= 2:
        hints.append(f"Завершает практики из Today ({practices_done} раз).")
    if tarot_deepen >= 2:
        hints.append(f"Уходит в углубление таро после Today ({tarot_deepen} раз).")
    if compat_format_c:
        fid, fc = compat_format_c.most_common(1)[0]
        if fc >= 2:
            hints.append(f"Чаще исследует сценарий совместимости «{fid}» ({fc} раз).")
    compat_views = int(type_counts.get("compatibility_view", 0))
    if compat_views >= 3 and not compat_format_c:
        hints.append(f"Регулярно смотрит разборы совместимости ({compat_views} просмотров).")

    return {
        "contract_version": "meaning_surface_patterns_v0",
        "window_days": wd,
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "total_events": int(total),
        "by_event_type": by_event_type,
        "tags": tags,
        "pattern_hints": hints[:6],
    }
