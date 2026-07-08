"""Многошаговый LLM-контур Guidance: шаг 1 — синтез answer-блока с картами; editorial остаётся шагом 2 в question_editorial."""

from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any

from todayflow_backend.core import models as core_models
from todayflow_backend.core.content_openness_policy import (
    LLM_SAFETY_BOUNDARY_EN,
    LLM_SAFETY_BOUNDARY_RU,
    LLM_USER_VOICE_EN,
    LLM_USER_VOICE_RU,
)
from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_guidance_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.services.generation_orchestrator import build_guidance_orchestration_meta

logger = logging.getLogger(__name__)
PROMPT_VERSION = "guidance-session-answer-v1"

_KEYS = ("clarity", "explanation", "forecast", "decision", "today")

SYSTEM_RU = f"""Ты редактор ответа TodayFlow Guidance (таро + вопрос пользователя).
Тебе дают шаблонный JTBD-ответ, расклад (позиции и значения карт), краткий профиль и оценку вопроса.

{LLM_SAFETY_BOUNDARY_RU}

{LLM_USER_VOICE_RU}

Задача: переписать пять полей ответа так, чтобы они явно опирались на карты и позиции — практично и по-русски, в том же духе что шаблон; конкретные выводы из расклада, без предсказания дат и «судьбы».

Верни строго JSON-объект с ключами: clarity, explanation, forecast, decision, today (строки)."""

SYSTEM_EN = f"""You refine a TodayFlow Guidance answer (tarot + user question).
You receive a template JTBD answer, spread positions and card meanings, a compact profile, and question hints.

{LLM_SAFETY_BOUNDARY_EN}

{LLM_USER_VOICE_EN}

Rewrite the five fields so they clearly reference the cards and positions — practical English; concrete spread insights, no date fortune-telling or fatalism.

Return a strict JSON object with keys: clarity, explanation, forecast, decision, today (strings)."""


def _card_lines(cards: list[core_models.TarotSpreadCard], *, limit: int = 14) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for c in cards[:limit]:
        pos = c.position
        title = pos.title if isinstance(pos, core_models.TarotSpreadPosition) else str(pos)
        pid = pos.id if isinstance(pos, core_models.TarotSpreadPosition) else None
        lines.append(
            {
                "position_id": pid,
                "position": title,
                "card": c.card.name if c.card else "",
                "orientation": c.orientation,
                "meaning_excerpt": (c.meaning or "")[:320],
            }
        )
    return lines


def _parse_answer_json(raw: str) -> dict[str, str] | None:
    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    out: dict[str, str] = {}
    for k in _KEYS:
        v = data.get(k)
        if not isinstance(v, str) or not v.strip():
            return None
        out[k] = " ".join(v.split()).strip()
    return out


def refine_guidance_session_answer(
    *,
    question: str,
    lane: str,
    spread_title: str,
    template_answer: dict[str, str],
    modular_profile: dict[str, Any],
    cards: list[core_models.TarotSpreadCard],
    structural: dict[str, Any],
    question_assessment: dict[str, Any],
    today_context: str | None,
    locale: str | None,
    learning_service: Any | None = None,
    db: Any | None = None,
    user_id: int | None = None,
) -> dict[str, str] | None:
    """Шаг 1 пайплайна: LLM поверх шаблона и расклада. При сбое — None (остаётся шаблон)."""
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None

    is_en = (locale or "").startswith("en")
    user_payload = {
        "question": question,
        "lane": lane,
        "spread_title": spread_title,
        "template_answer": {k: template_answer.get(k, "") for k in _KEYS},
        "cards": _card_lines(cards),
        "structural": {
            "dominant_card_name": structural.get("dominant_card_name"),
            "tension_position_id": structural.get("tension_position_id"),
            "conflict_note": (structural.get("conflict_note") or "")[:400],
            "themes": structural.get("themes") if isinstance(structural.get("themes"), list) else [],
        },
        "question_assessment": {
            "flags": question_assessment.get("flags"),
            "suggestion": question_assessment.get("suggestion"),
            "weak_reading_warning": question_assessment.get("weak_reading_warning"),
        },
        "modular_profile": modular_profile,
        "today_context": (today_context or "").strip()[:400] or None,
    }
    user_message = (
        "Синтезируй ответ по данным (JSON):\n"
        if not is_en
        else "Synthesize the answer from this JSON:\n"
    ) + json.dumps(user_payload, ensure_ascii=False)

    started = perf_counter()
    model_id = resolve_guidance_chat_model()
    orchestration_meta = build_guidance_orchestration_meta(
        lane=lane,
        spread_title=spread_title,
        prompt_version=PROMPT_VERSION,
        structural=structural,
        question_assessment=question_assessment,
    )
    try:
        content = chat_completion_text(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_EN if is_en else SYSTEM_RU},
                {"role": "user", "content": user_message},
            ],
            temperature=0.45,
            max_tokens=resolve_max_tokens(1400),
            json_object=settings.guidance_llm_json_object,
        )
        parsed = _parse_answer_json(content) if content else None
        if not parsed:
            return None
        if learning_service and db is not None:
            try:
                pv = learning_service.get_or_create_prompt_version(
                    db,
                    module="questions",
                    version=PROMPT_VERSION,
                    prompt_kind="guidance_session",
                    prompt_text=SYSTEM_RU,
                    label="guidance_llm_step1",
                    metadata={"lane": lane},
                )
                learning_service.log_generation(
                    db,
                    module="questions",
                    surface="guidance_reading_llm",
                    user_id=user_id,
                    prompt_version_id=pv.id,
                    model=model_id,
                    locale=locale or "ru",
                    input_payload={
                        "lane": lane,
                        "spread_title": spread_title,
                        "orchestration": orchestration_meta,
                    },
                    system_prompt=SYSTEM_RU,
                    user_prompt=user_message[:8000],
                    raw_response=content[:12000],
                    normalized_response=parsed,
                    status="success",
                    used_fallback=False,
                    duration_ms=int((perf_counter() - started) * 1000),
                )
            except Exception:
                logger.debug("guidance llm log failed", exc_info=True)
        return parsed
    except Exception as exc:
        logger.warning("Guidance LLM step1 failed: %s", exc, exc_info=True)
        return None


def refine_guidance_clarification_answer(
    *,
    parent_question: str,
    clarification_goal: str,
    goal_label: str,
    template_answer: dict[str, str],
    modular_profile: dict[str, Any],
    cards: list[core_models.TarotSpreadCard],
    parent_summary: str,
    locale: str | None,
    learning_service: Any | None = None,
    db: Any | None = None,
    user_id: int | None = None,
) -> dict[str, str] | None:
    """LLM для одной уточняющей карты (уже после шаблонного answer)."""
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None

    is_en = (locale or "").startswith("en")
    sys = (
        "You refine a one-card clarification for TodayFlow Guidance. "
        "Keep focus on the clarification goal; tie to the single card; return JSON with "
        "clarity, explanation, forecast, decision, today."
        if is_en
        else "Ты уточняешь ответ TodayFlow одной картой. Фокус — цель уточнения; опирайся на единственную карту. "
        "Верни JSON: clarity, explanation, forecast, decision, today."
    )
    payload = {
        "parent_question": parent_question,
        "parent_summary_excerpt": parent_summary[:500],
        "clarification_goal": clarification_goal,
        "goal_label": goal_label,
        "template_answer": {k: template_answer.get(k, "") for k in _KEYS},
        "cards": _card_lines(cards, limit=2),
        "modular_profile": modular_profile,
    }
    user_message = json.dumps(payload, ensure_ascii=False)
    started = perf_counter()
    model_id = resolve_guidance_chat_model()
    orchestration_meta = build_guidance_orchestration_meta(
        lane="clarify",
        spread_title=goal_label,
        prompt_version="guidance-clarify-answer-v1",
        structural={"dominant_card_name": _card_lines(cards, limit=1)[0]["card"] if cards else None},
        question_assessment={"flags": [clarification_goal]},
    )
    try:
        content = chat_completion_text(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=resolve_max_tokens(900),
            json_object=settings.guidance_llm_json_object,
        )
        parsed = _parse_answer_json(content) if content else None
        if parsed and learning_service and db is not None:
            try:
                pv = learning_service.get_or_create_prompt_version(
                    db,
                    module="questions",
                    version="guidance-clarify-answer-v1",
                    prompt_kind="guidance_clarify",
                    prompt_text=sys,
                    label="guidance_llm_clarify",
                    metadata={},
                )
                learning_service.log_generation(
                    db,
                    module="questions",
                    surface="guidance_clarify_llm",
                    user_id=user_id,
                    prompt_version_id=pv.id,
                    model=model_id,
                    locale=locale or "ru",
                    input_payload={
                        "goal": clarification_goal,
                        "orchestration": orchestration_meta,
                    },
                    system_prompt=sys,
                    user_prompt=user_message[:6000],
                    raw_response=content[:8000],
                    normalized_response=parsed,
                    status="success",
                    used_fallback=False,
                    duration_ms=int((perf_counter() - started) * 1000),
                )
            except Exception:
                logger.debug("guidance clarify llm log failed", exc_info=True)
        return parsed
    except Exception as exc:
        logger.warning("Guidance clarify LLM failed: %s", exc, exc_info=True)
        return None
