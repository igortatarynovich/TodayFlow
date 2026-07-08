"""Объяснение нумерологии через ИИ с учётом натальной карты пользователя."""

from typing import Optional, Dict, Any
import logging
import json
import re
from time import perf_counter

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.core.text_quality import is_meaningful_sentence
from todayflow_backend.core.user_context import get_user_context
from todayflow_backend.db import models as db_models
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

PROMPT_VERSION = "numerology-explainer-v3"

NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT = """Ты пишешь персональное объяснение нумерологического числа для TodayFlow.

Твоя задача:
- показать, что число значит именно для этого человека;
- связать число с его профилем и текущим днем;
- перевести символику числа в понятные жизненные ориентиры.

Пиши:
- ясно;
- по-человечески;
- конкретно;
- без канцелярита и эзотерического тумана.

Не пиши:
- пустые советы;
- повторы между полями;
- общие формулы, которые подходят любому человеку.
- формулы вроде "внутренний порядок", "ясная линия", "держать ритм", если за ними не стоит конкретный смысл.

Каждое поле должно ощущаться как полезная интерпретация, а не как словарь значений.

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


def _fallback_numerology_explanation(number: int, number_type: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
    natal = user_context.get("natal_chart") or {}
    sun = natal.get("sun_sign")
    moon = natal.get("moon_sign")
    anchor = f"с учетом Солнца в {sun} и Луны в {moon}" if sun and moon else "в контексте твоего сегодняшнего дня"
    return {
        "meaning": f"Число {number} в формате {number_type} подчеркивает тему выбора, структуры и того, как ты распоряжаешься вниманием {anchor}.",
        "what_to_do": "Назови один результат дня и принимай первые решения так, чтобы они вели именно к нему, а не просто закрывали тревогу.",
        "what_to_avoid": "Не раскидывай силы на несколько направлений сразу, если в итоге ни одно из них не двигается по-настоящему.",
        "possible_events": "Могут всплыть разговоры о сроках, обязательствах, деньгах или распределении времени, где придется быть точнее обычного.",
        "how_day_looks": "День идет заметно лучше, когда ты не усложняешь простые шаги и не мечешься между вариантами после каждого нового сигнала.",
        "why_this_number": "Это число приходит в дни, когда особенно видно, что именно держит твою жизнь в порядке, а что только забирает силы.",
    }


def _is_valid_numerology_explanation(explanation: Dict[str, Any]) -> bool:
    required = ("meaning", "what_to_do", "what_to_avoid", "possible_events", "how_day_looks", "why_this_number")
    for key in required:
        value = explanation.get(key)
        if not isinstance(value, str):
            return False
        ok, _ = is_meaningful_sentence(value, min_words=5)
        if not ok:
            return False
    return True


def explain_numerology_number(
    user,
    db,
    number: int,
    number_type: str,  # "day", "life_path", "personal_year"
    target_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Объясняет число нумерологии через призму натальной карты пользователя.
    """
    learning_service = get_learning_service()
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="numerology",
        version=PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
        label="Numerology explanation",
        metadata={"surface": "numerology_explainer"},
    )
    latest_snapshot = (
        db.query(db_models.CoreProfileSnapshot)
        .filter(db_models.CoreProfileSnapshot.user_id == user.id)
        .order_by(db_models.CoreProfileSnapshot.updated_at.desc())
        .first()
    )

    if not is_llm_chat_configured():
        logger.warning("LLM not configured, cannot explain numerology")
        return {}

    client = get_openai_compatible_client()
    if client is None:
        logger.warning("OpenAI client not available")
        return {}
    
    if not target_date:
        from datetime import date
        target_date = date.today().isoformat()
    
    # Собираем контекст пользователя (натальная карта обязательна)
    try:
        user_context = get_user_context(user, target_date, db)
    except Exception as e:
        logger.warning(f"Failed to get user context for numerology explanation: {e}", exc_info=True)
        user_context = {}
    
    # Строим промпт
    number_type_names = {
        "day": "Число дня",
        "life_path": "Число жизненного пути",
        "personal_year": "Личный год"
    }
    number_type_name = number_type_names.get(number_type, "Число")
    
    prompt_parts = [
        f"{number_type_name}: {number}",
        f"Дата: {target_date}",
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
    
    # Добавляем дополнительный контекст нумерологии
    if user_context.get("numerology"):
        num = user_context["numerology"]
        if num.get("day_meaning"):
            prompt_parts.append(f"Контекст числа дня: {num['day_meaning']}")
        if num.get("day_title"):
            prompt_parts.append(f"Название фокуса: {num['day_title']}")
    
    prompt_parts.extend([
        "Задача:",
        f"- объясни {number_type_name.lower()} {number} как персональный ориентир, а не как абстрактное значение;",
        "- если есть профиль, свяжи число с ним;",
        "- покажи, как число меняет решения, поведение, разговоры, деньги, задачи или темп именно сегодня;",
        "- избегай клише и словарного тона;",
        "- не прячь смысл за красивыми словами без конкретики;",
        "Верни только JSON, без markdown и пояснений.",
    ])
    
    user_prompt = "\n".join(prompt_parts)
    
    started_at = perf_counter()
    model_id = resolve_default_chat_model()
    try:
        content = chat_completion_plain(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=resolve_max_tokens(1000),
        ) or ""
        if not content:
            learning_service.log_generation(
                db,
                module="numerology",
                surface="numerology_explainer",
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale="ru",
                input_payload={"number": number, "number_type": number_type, "target_date": target_date},
                system_prompt=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                status="empty",
                used_fallback=True,
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            return {}
        
        # Парсим JSON
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if m:
            content = m.group(1).strip()
        
        try:
            explanation = json.loads(content)
            if isinstance(explanation, dict):
                if _is_valid_numerology_explanation(explanation):
                    learning_service.log_generation(
                        db,
                        module="numerology",
                        surface="numerology_explainer",
                        user_id=user.id,
                        core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                        prompt_version_id=prompt_version.id,
                        model=model_id,
                        locale="ru",
                        input_payload={"number": number, "number_type": number_type, "target_date": target_date},
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
            logger.warning(f"Failed to parse numerology explanation JSON: {content}")

        fallback = _fallback_numerology_explanation(number, number_type, user_context if isinstance(user_context, dict) else {})
        learning_service.log_generation(
            db,
            module="numerology",
            surface="numerology_explainer",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale="ru",
            input_payload={"number": number, "number_type": number_type, "target_date": target_date},
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
        logger.warning(f"OpenAI API error explaining numerology: {e}", exc_info=True)
        fallback = _fallback_numerology_explanation(number, number_type, user_context if isinstance(user_context, dict) else {})
        learning_service.log_generation(
            db,
            module="numerology",
            surface="numerology_explainer",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale="ru",
            input_payload={"number": number, "number_type": number_type, "target_date": target_date},
            system_prompt=NUMEROLOGY_EXPLAINER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="error",
            used_fallback=True,
            error_message=str(e),
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
