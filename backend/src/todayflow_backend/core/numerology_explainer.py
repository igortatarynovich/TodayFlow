"""Объяснение нумерологии через ИИ с учётом натальной карты пользователя.

Base meaning SoT: number_base_v1 (canon NUMBER_BASE_V1).
LLM personalizes bridge fields (what_to_do / avoid / events / how_day_looks / why_this_number)
for the given number_type scale — never invents the digit archetype.
"""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any, Dict, Optional

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.core.text_quality import is_meaningful_sentence
from todayflow_backend.core.user_context import get_user_context
from todayflow_backend.data import number_base_v1
from todayflow_backend.db import models as db_models
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

PROMPT_VERSION = "numerology-explainer-v4"

NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT = """Ты пишешь персональное объяснение нумерологического числа для TodayFlow.

Базовое значение числа уже зафиксировано системой (блок «Базовое значение числа» в контексте).
Не изобретай собственный архетип и не подменяй base_meaning / keywords.
Твоя задача — только персональный слой (бридж):
- связать данное базовое значение с профилем человека и масштабом числа
  (число дня / жизненный путь / личный год — один архетип, разный горизонт времени);
- показать, как это проявится в обычной жизни;
- что делать / чего избегать.

Пиши:
- ясно;
- по-человечески;
- конкретно;
- без канцелярита и эзотерического тумана.

Не пиши:
- пустые советы;
- повторы между полями;
- общие формулы, которые подходят любому человеку;
- формулы вроде "внутренний порядок", "ясная линия", "держать ритм", если за ними не стоит конкретный смысл;
- независимое «значение числа», расходящееся с блоком «Базовое значение».

Поле meaning в ответе должно явно опираться на переданный archetype/keywords
(не словарь «с нуля»). Остальные поля — бридж к дню/профилю.

Верни только валидный JSON:
{
  "meaning": "...",
  "what_to_do": "...",
  "what_to_avoid": "...",
  "possible_events": "...",
  "how_day_looks": "...",
  "why_this_number": "..."
}
"""

_NUMBER_TYPE_NAMES = {
    "day": "Число дня",
    "life_path": "Число жизненного пути",
    "personal_year": "Личный год",
}


def _apply_base_meaning(explanation: Dict[str, Any], number: int) -> Dict[str, Any]:
    """Force meaning from number_base_v1 when available (SoT for digit prose)."""
    row = number_base_v1.get_number_base(number)
    out = dict(explanation)
    if not row:
        out.setdefault("meaning_source", "unavailable")
        return out
    out["meaning"] = row["base_meaning"]
    out["meaning_source"] = "number_base_v1"
    out["archetype"] = row.get("archetype") or row.get("title")
    return out


def _honest_unavailable(number: int, number_type: str) -> Dict[str, Any]:
    return {
        "meaning": "",
        "what_to_do": "",
        "what_to_avoid": "",
        "possible_events": "",
        "how_day_looks": "",
        "why_this_number": "",
        "meaning_source": "unavailable",
        "is_fallback": True,
        "number": number,
        "number_type": number_type,
    }


def _fallback_numerology_explanation(
    number: int,
    number_type: str,
    user_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Base-backed fallback — never invent a digit archetype outside number_base_v1."""
    row = number_base_v1.get_number_base(number)
    if not row:
        return _honest_unavailable(number, number_type)

    natal = user_context.get("natal_chart") or {}
    sun = natal.get("sun_sign")
    moon = natal.get("moon_sign")
    anchor = (
        f"с учетом Солнца в {sun} и Луны в {moon}"
        if sun and moon
        else "в контексте твоего сегодняшнего дня"
    )
    type_name = _NUMBER_TYPE_NAMES.get(number_type, "Число")
    keywords = ", ".join((row.get("keywords") or [])[:3]) or row.get("archetype") or ""
    archetype = row.get("archetype") or row.get("title") or f"число {number}"

    return _apply_base_meaning(
        {
            "meaning": row["base_meaning"],
            "what_to_do": (
                f"Опирайся на архетип «{archetype}» ({keywords}): "
                f"выбери один конкретный шаг в масштабе «{type_name}» {anchor}."
            ),
            "what_to_avoid": (
                f"Не подменяй тему «{archetype}» чужим сценарием и не размывай фокус "
                f"на несколько направлений сразу."
            ),
            "possible_events": (
                f"Могут всплыть ситуации вокруг тем: {keywords} — "
                f"где придётся быть точнее обычного."
            ),
            "how_day_looks": (
                f"День идёт заметно лучше, когда решения держат линию «{archetype}», "
                f"а не метание между случайными сигналами."
            ),
            "why_this_number": (
                f"{type_name} {number} сегодня опирается на базовое значение "
                f"«{archetype}»: {row['base_meaning']}"
            ),
            "is_fallback": True,
        },
        number,
    )


def _is_valid_numerology_explanation(explanation: Dict[str, Any], number: int) -> bool:
    required = (
        "meaning",
        "what_to_do",
        "what_to_avoid",
        "possible_events",
        "how_day_looks",
        "why_this_number",
    )
    for key in required:
        value = explanation.get(key)
        if not isinstance(value, str):
            return False
        ok, _ = is_meaningful_sentence(value, min_words=5)
        if not ok:
            return False
    # meaning must touch base anchors (before we force-overwrite from bank)
    if number_base_v1.get_number_base(number):
        if not number_base_v1.meaning_aligned_with_base(str(explanation.get("meaning") or ""), number):
            return False
    return True


def explain_numerology_number(
    user,
    db,
    number: int,
    number_type: str,  # "day", "life_path", "personal_year"
    target_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Объясняет число нумерологии через призму натальной карты пользователя.
    Архетип цифры — только из number_base_v1.
    """
    try:
        number_int = int(number)
    except (TypeError, ValueError):
        return _honest_unavailable(0, number_type)

    learning_service = get_learning_service()
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="numerology",
        version=PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
        label="Numerology explanation",
        metadata={
            "surface": "numerology_explainer",
            "base_meaning_sot": "number_base_v1",
        },
    )
    latest_snapshot = (
        db.query(db_models.CoreProfileSnapshot)
        .filter(db_models.CoreProfileSnapshot.user_id == user.id)
        .order_by(db_models.CoreProfileSnapshot.updated_at.desc())
        .first()
    )

    if not target_date:
        from datetime import date

        target_date = date.today().isoformat()

    try:
        user_context = get_user_context(user, target_date, db)
    except Exception as e:
        logger.warning(
            "Failed to get user context for numerology explanation: %s", e, exc_info=True
        )
        user_context = {}

    base_block = number_base_v1.format_base_prompt_block(number_int)
    if not base_block:
        logger.warning("number_base_v1 missing row for value=%s", number_int)
        return _honest_unavailable(number_int, number_type)

    if not is_llm_chat_configured():
        logger.warning("LLM not configured, using number_base_v1 fallback")
        return _fallback_numerology_explanation(
            number_int, number_type, user_context if isinstance(user_context, dict) else {}
        )

    client = get_openai_compatible_client()
    if client is None:
        logger.warning("OpenAI client not available, using number_base_v1 fallback")
        return _fallback_numerology_explanation(
            number_int, number_type, user_context if isinstance(user_context, dict) else {}
        )

    number_type_name = _NUMBER_TYPE_NAMES.get(number_type, "Число")

    prompt_parts = [
        f"{number_type_name}: {number_int}",
        f"Дата: {target_date}",
        base_block,
        (
            "Масштаб: архетип цифры один и тот же; "
            f"бридж-поля должны учитывать, что это именно «{number_type_name}», "
            "а не абстрактный словарь."
        ),
    ]

    if user_context.get("natal_chart"):
        natal = user_context["natal_chart"]
        natal_info = []
        if natal.get("sun_sign"):
            natal_info.append(f"Солнце в {natal['sun_sign']}")
        if natal.get("moon_sign"):
            natal_info.append(f"Луна в {natal['moon_sign']}")
        if natal.get("ascendant"):
            natal_info.append(f"Асцендент в {natal['ascendant']}")
        if natal.get("planets"):
            for p in natal["planets"][:5]:
                natal_info.append(f"{p.get('name')} в {p.get('sign')}")

        if natal_info:
            prompt_parts.append("Профиль пользователя:")
            prompt_parts.extend(f"- {line}" for line in natal_info)
    else:
        prompt_parts.append("Профиль пользователя: полной натальной карты нет.")

    if user_context.get("numerology"):
        num = user_context["numerology"]
        if num.get("day_meaning"):
            prompt_parts.append(f"Контекст числа дня: {num['day_meaning']}")
        if num.get("day_title"):
            prompt_parts.append(f"Название фокуса: {num['day_title']}")

    prompt_parts.extend(
        [
            "Задача:",
            "- не изобретай собственное значение числа — используй блок «Базовое значение»;",
            f"- переведи архетип в личный контекст масштаба «{number_type_name}»;",
            "- если есть профиль, свяжи число с ним;",
            "- покажи, как число меняет решения, поведение, разговоры, деньги, задачи или темп;",
            "- избегай клише и словарного тона;",
            "Верни только JSON, без markdown и пояснений.",
        ]
    )

    user_prompt = "\n".join(prompt_parts)

    started_at = perf_counter()
    model_id = resolve_default_chat_model()
    try:
        content = (
            chat_completion_plain(
                client,
                model=model_id,
                messages=[
                    {"role": "system", "content": NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=resolve_max_tokens(1000),
            )
            or ""
        )
        if not content:
            fallback = _fallback_numerology_explanation(
                number_int, number_type, user_context if isinstance(user_context, dict) else {}
            )
            learning_service.log_generation(
                db,
                module="numerology",
                surface="numerology_explainer",
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale="ru",
                input_payload={
                    "number": number_int,
                    "number_type": number_type,
                    "target_date": target_date,
                },
                system_prompt=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                normalized_response=fallback,
                status="empty",
                used_fallback=True,
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            return fallback

        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if m:
            content = m.group(1).strip()

        try:
            explanation = json.loads(content)
            if isinstance(explanation, dict) and _is_valid_numerology_explanation(
                explanation, number_int
            ):
                explanation = _apply_base_meaning(explanation, number_int)
                learning_service.log_generation(
                    db,
                    module="numerology",
                    surface="numerology_explainer",
                    user_id=user.id,
                    core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                    prompt_version_id=prompt_version.id,
                    model=model_id,
                    locale="ru",
                    input_payload={
                        "number": number_int,
                        "number_type": number_type,
                        "target_date": target_date,
                    },
                    system_prompt=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    raw_response=content,
                    normalized_response=explanation,
                    status="success",
                    used_fallback=False,
                    duration_ms=int((perf_counter() - started_at) * 1000),
                )
                return explanation
        except json.JSONDecodeError:
            logger.warning("Failed to parse numerology explanation JSON: %s", content)

        fallback = _fallback_numerology_explanation(
            number_int, number_type, user_context if isinstance(user_context, dict) else {}
        )
        learning_service.log_generation(
            db,
            module="numerology",
            surface="numerology_explainer",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale="ru",
            input_payload={
                "number": number_int,
                "number_type": number_type,
                "target_date": target_date,
            },
            system_prompt=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=content,
            normalized_response=fallback,
            status="fallback",
            used_fallback=True,
            error_message="invalid_or_unusable_response",
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
    except Exception as e:
        logger.warning("OpenAI API error explaining numerology: %s", e, exc_info=True)
        fallback = _fallback_numerology_explanation(
            number_int, number_type, user_context if isinstance(user_context, dict) else {}
        )
        learning_service.log_generation(
            db,
            module="numerology",
            surface="numerology_explainer",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale="ru",
            input_payload={
                "number": number_int,
                "number_type": number_type,
                "target_date": target_date,
            },
            system_prompt=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="error",
            used_fallback=True,
            error_message=str(e),
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
