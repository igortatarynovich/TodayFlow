"""Объяснение карт таро через ИИ с учётом натальной карты пользователя.

Base meaning SoT: card_base_v1 (canon TAROT_CARD_BASE_V1).
LLM may personalize what_to_do / avoid / events / how_day_looks / why_this_card —
never overwrite traditional base meaning.
"""

from typing import Optional, Dict, Any
import logging
import json
import re
from time import perf_counter

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.core.text_quality import is_meaningful_sentence
from todayflow_backend.core.user_context import get_user_context
from todayflow_backend.data import card_base_v1
from todayflow_backend.db import models as db_models
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

PROMPT_VERSION = "tarot-explainer-v4"

TAROT_EXPLAINER_SYSTEM_PROMPT = """Ты пишешь персональное объяснение карты дня для TodayFlow.

Традиционное значение карты уже зафиксировано системой (поле base_meaning в контексте).
Не переписывай и не заменяй его. Твоя задача — только персональный слой:
- почему эта карта важна сегодня для конкретного человека;
- как это проявится в обычной жизни;
- что делать / чего избегать.

Пиши:
- конкретно;
- живо;
- без тумана и красивостей ради красивостей;
- с ощущением личного сопровождения;
- так, чтобы человек видел себя и свой день, а не абстрактную символику;
- лаконично: короткие абзацы, один фокус на поле — пользователь углубляется в приложении по шагам.

Не пиши:
- общие духовные штампы;
- пафос;
- фразы, которые подходят кому угодно;
- обороты вроде "внутренняя ось", "лишний шум", "просто доверься", "не распыляйся";
- повторы между полями;
- дословное повторение формулировок из раздела «Сегодня», дневного гороскопа или интерпретаций раскладов — это отдельные слои.

Каждое поле должно быть полезным и читаемым.

Верни только валидный JSON:
{
  "what_to_do": "...",
  "what_to_avoid": "...",
  "possible_events": "...",
  "how_day_looks": "...",
  "why_this_card": "..."
}
"""


def _base_meaning_text(card_id: int | None, card_name: str, orientation: str) -> str | None:
    cid = card_id
    if cid is None:
        cid = card_base_v1.resolve_card_id_by_name(card_name)
    if cid is None:
        return None
    row = card_base_v1.get_base_meaning(int(cid), orientation)
    if not row:
        return None
    return str(row.get("meaning") or "").strip() or None


def _apply_base_meaning(
    explanation: Dict[str, Any],
    *,
    card_id: int | None,
    card_name: str,
    orientation: str,
) -> Dict[str, Any]:
    """Force meaning from card_base_v1 when available (SoT for traditional prose)."""
    base = _base_meaning_text(card_id, card_name, orientation)
    if not base:
        return explanation
    out = dict(explanation)
    out["meaning"] = base
    out["meaning_source"] = "card_base_v1"
    return out


def _fallback_tarot_explanation(
    card_name: str,
    orientation: str,
    user_context: Dict[str, Any],
    *,
    card_id: int | None = None,
) -> Dict[str, Any]:
    natal = user_context.get("natal_chart") or {}
    sun = natal.get("sun_sign")
    moon = natal.get("moon_sign")
    natal_anchor = f"через сочетание Солнца в {sun} и Луны в {moon}" if sun and moon else "через твой текущий способ реагировать на день"
    orient = "в прямом положении" if (orientation or "").lower() == "upright" else "в перевернутом положении"
    base = _base_meaning_text(card_id, card_name, orientation)
    return {
        "meaning": base
        or f"Карта {card_name} {orient} выводит на первый план тему выбора и того, куда сегодня уходит твое лучшее внимание {natal_anchor}.",
        "what_to_do": "Перед важным разговором или задачей спроси себя, что здесь действительно стоит довести до результата именно сегодня.",
        "what_to_avoid": "Не отвечай слишком быстро и не обещай лишнего только потому, что хочешь сразу снять напряжение.",
        "possible_events": "Может возникнуть момент, где придется выбрать между удобным решением на сейчас и более честным шагом с прицелом дальше.",
        "how_day_looks": "День складывается удачнее, когда ты не суетишься и не берешь на себя больше, чем реально можешь удержать.",
        "why_this_card": "Эта карта приходит в дни, когда важнее не скорость, а точность: как в решениях, так и в том, кому и чему ты сегодня отдаешь силы.",
        "meaning_source": "card_base_v1" if base else "fallback_template",
    }


def _is_valid_tarot_explanation(explanation: Dict[str, Any]) -> bool:
    # meaning is injected from card_base_v1 — validate personalization fields only.
    required = ("what_to_do", "what_to_avoid", "possible_events", "how_day_looks", "why_this_card")
    for key in required:
        value = explanation.get(key)
        if not isinstance(value, str):
            return False
        ok, _ = is_meaningful_sentence(value, min_words=5)
        if not ok:
            return False
    return True


def explain_tarot_card(
    user,
    db,
    card_name: str,
    orientation: str = "upright",
    target_date: Optional[str] = None,
    card_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Объясняет карту таро через призму натальной карты пользователя.
    Traditional meaning always comes from card_base_v1 when resolvable.
    """
    learning_service = get_learning_service()
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="tarot",
        version=PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=TAROT_EXPLAINER_SYSTEM_PROMPT,
        label="Daily tarot explanation",
        metadata={"surface": "daily_card_explainer", "base_meaning_sot": "card_base_v1"},
    )
    resolved_id = card_id if card_id is not None else card_base_v1.resolve_card_id_by_name(card_name)
    base_meaning = _base_meaning_text(resolved_id, card_name, orientation)
    latest_snapshot = (
        db.query(db_models.CoreProfileSnapshot)
        .filter(db_models.CoreProfileSnapshot.user_id == user.id)
        .order_by(db_models.CoreProfileSnapshot.updated_at.desc())
        .first()
    )

    if not target_date:
        from datetime import date
        target_date = date.today().isoformat()

    # Собираем контекст пользователя (натальная карта обязательна)
    try:
        user_context = get_user_context(user, target_date, db)
    except Exception as e:
        logger.warning(f"Failed to get user context for tarot explanation: {e}", exc_info=True)
        user_context = {}

    if not is_llm_chat_configured():
        logger.warning("LLM not configured, cannot explain tarot card")
        return _apply_base_meaning(
            _fallback_tarot_explanation(
                card_name, orientation, user_context if isinstance(user_context, dict) else {}, card_id=resolved_id
            ),
            card_id=resolved_id,
            card_name=card_name,
            orientation=orientation,
        )

    client = get_openai_compatible_client()
    if client is None:
        logger.warning("OpenAI client not available")
        return _apply_base_meaning(
            _fallback_tarot_explanation(
                card_name, orientation, user_context if isinstance(user_context, dict) else {}, card_id=resolved_id
            ),
            card_id=resolved_id,
            card_name=card_name,
            orientation=orientation,
        )
    
    # Строим промпт
    prompt_parts = [
        f"Карта таро: {card_name}",
        f"Ориентация: {orientation}",
        f"Дата: {target_date}",
    ]
    if base_meaning:
        prompt_parts.append(f"base_meaning (не переписывать): {base_meaning}")
    
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
    
    prompt_parts.extend([
        "Задача:",
        "- объясни, что эта карта меняет именно сегодня;",
        "- свяжи ее с профилем человека, если данные есть;",
        "- покажи смысл через обычные сцены дня: работа, деньги, отношения, бытовые решения, усталость, переписка;",
        "- сделай текст живым, понятным и без мистических клише;",
        "- не повторяй одну и ту же мысль разными словами в разных полях;",
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
                {"role": "system", "content": TAROT_EXPLAINER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=resolve_max_tokens(1000),
        ) or ""
        if not content:
            learning_service.log_generation(
                db,
                module="tarot",
                surface="daily_card_explainer",
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale="ru",
                input_payload={
                    "card_name": card_name,
                    "card_id": resolved_id,
                    "orientation": orientation,
                    "target_date": target_date,
                },
                system_prompt=TAROT_EXPLAINER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                status="empty",
                used_fallback=True,
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            return _apply_base_meaning(
                _fallback_tarot_explanation(
                    card_name,
                    orientation,
                    user_context if isinstance(user_context, dict) else {},
                    card_id=resolved_id,
                ),
                card_id=resolved_id,
                card_name=card_name,
                orientation=orientation,
            )
        
        # Парсим JSON
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if m:
            content = m.group(1).strip()
        
        try:
            explanation = json.loads(content)
            if isinstance(explanation, dict):
                if _is_valid_tarot_explanation(explanation):
                    explanation = _apply_base_meaning(
                        explanation,
                        card_id=resolved_id,
                        card_name=card_name,
                        orientation=orientation,
                    )
                    learning_service.log_generation(
                        db,
                        module="tarot",
                        surface="daily_card_explainer",
                        user_id=user.id,
                        core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                        prompt_version_id=prompt_version.id,
                        model=model_id,
                        locale="ru",
                        input_payload={
                            "card_name": card_name,
                            "card_id": resolved_id,
                            "orientation": orientation,
                            "target_date": target_date,
                        },
                        system_prompt=TAROT_EXPLAINER_SYSTEM_PROMPT,
                        user_prompt=user_prompt,
                        raw_response=content,
                        normalized_response=explanation,
                        status="success",
                        used_fallback=False,
                        duration_ms=int((perf_counter() - started_at) * 1000),
                    )
                    return explanation
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse tarot explanation JSON: {content}")

        fallback = _apply_base_meaning(
            _fallback_tarot_explanation(
                card_name,
                orientation,
                user_context if isinstance(user_context, dict) else {},
                card_id=resolved_id,
            ),
            card_id=resolved_id,
            card_name=card_name,
            orientation=orientation,
        )
        learning_service.log_generation(
            db,
            module="tarot",
            surface="daily_card_explainer",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale="ru",
            input_payload={
                "card_name": card_name,
                "card_id": resolved_id,
                "orientation": orientation,
                "target_date": target_date,
            },
            system_prompt=TAROT_EXPLAINER_SYSTEM_PROMPT,
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
        logger.warning(f"OpenAI API error explaining tarot card: {e}", exc_info=True)
        fallback = _apply_base_meaning(
            _fallback_tarot_explanation(
                card_name,
                orientation,
                user_context if isinstance(user_context, dict) else {},
                card_id=resolved_id,
            ),
            card_id=resolved_id,
            card_name=card_name,
            orientation=orientation,
        )
        learning_service.log_generation(
            db,
            module="tarot",
            surface="daily_card_explainer",
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale="ru",
            input_payload={
                "card_name": card_name,
                "card_id": resolved_id,
                "orientation": orientation,
                "target_date": target_date,
            },
            system_prompt=TAROT_EXPLAINER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="error",
            used_fallback=True,
            error_message=str(e),
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
