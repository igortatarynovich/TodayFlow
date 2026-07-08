"""DE-6: сжатый слой намерения дня для DayContext и narrative (без новых таблиц)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.services.day_logic_shared_v0 import humanize_day_focus_key


def build_intent_layer_v0(
    *,
    morning_intention: str | None,
    morning_focus: str | None,
    head_topic: str | None,
    question_of_day_answer: str | None = None,
    quick_decision_answer: str | None = None,
) -> dict[str, Any] | None:
    """Собирает `layers.intent` для `day_context_v0`; None если нечего передать."""
    mi = (morning_intention or "").strip()
    mf = (morning_focus or "").strip()
    ht = (head_topic or "").strip()
    qd = (question_of_day_answer or "").strip()
    qdc = (quick_decision_answer or "").strip()
    if not (mi or mf or ht or qd or qdc):
        return None

    parts: list[str] = []
    if mi:
        parts.append(f"Цель/намерение на день: {mi[:400]}")
    if mf:
        parts.append(f"Фокус утра: {humanize_day_focus_key(mf)[:100]}")
    if ht:
        parts.append(f"Тема «в голове» после ритуала: {ht[:100]}")
    if qd:
        parts.append(f"Ответ на вопрос дня: {qd[:100]}")
    if qdc:
        parts.append(f"Мини-решение: {qdc[:20]}")
    what_matters = " ".join(parts)[:900]

    return {
        "contract_version": "intent_slice_v0",
        "morning_intention": mi[:2000] if mi else None,
        "morning_focus": mf[:100] if mf else None,
        "head_topic": ht[:120] if ht else None,
        "question_of_day_answer": qd[:120] if qd else None,
        "quick_decision_answer": qdc[:16] if qdc else None,
        "what_matters_line": what_matters,
    }
