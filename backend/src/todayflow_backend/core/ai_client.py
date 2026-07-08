"""Клиент AI (OpenAI-совместимый) для генерации текстов TodayFlow.

Если задан ключ LLM (`OPENAI_API_KEY` или `LLM_CHAT_API_KEY`, опционально `OPENAI_BASE_URL`) —
Writer использует LLM для прогнозов. Иначе — только Lexicon.
"""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any, Dict, List, Optional

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.core.text_quality import has_action_verb, is_meaningful_sentence
from todayflow_backend.db.models import CoreProfileSnapshot
from todayflow_backend.db.session import SessionLocal
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

FORECAST_PROMPT_VERSION = "forecast-blocks-v2"
DAY_MEANING_PROMPT_VERSION = "forecast-day-meaning-v2"


SYSTEM_PROMPT = """Ты пишешь персональный прогноз дня для TodayFlow.

Твоя задача:
- соединить профиль человека и контекст дня;
- объяснить это человеческим языком;
- дать ощущение ясности, а не мистического тумана.

Приоритеты:
- конкретика важнее красивых общих фраз;
- жизненные сцены важнее абстракций;
- одно полезное наблюдение лучше трех пустых;
- если упоминаешь знак, планету, число или карту, сразу объясняй, как это проявляется сегодня.

Запрещено:
- "будь в потоке", "слушай себя", "энергия дня ведет тебя", "всё возможно";
- безличные фразы, которые подходят кому угодно;
- повторы между блоками;
- слишком эзотерический или пафосный тон.

Стиль:
- теплый, уверенный, спокойный;
- редакторский и понятный;
- короткие ясные предложения;
- без канцелярита.

Формат:
- theme: одно цельное предложение, 12-28 слов;
- notice: два отдельных наблюдения, каждое 10-24 слова;
- scene: две жизненные сцены, каждая 10-24 слова;
- micro_action: одно маленькое действие на 30 секунд - 2 минуты, в повелительной форме.

Верни только JSON:
{"theme":"...","notice":["...","..."],"scene":["...","..."],"micro_action":"..."}
"""


def _build_user_prompt(
    plan: Dict[str, Any], 
    request: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> str:
    theme_phrase = plan.get("theme", {}).get("phrase", {}) or {}
    notice_items = plan.get("notice", []) or []
    scene_items = plan.get("scene", []) or []
    micro_phrase = plan.get("micro_action", {}).get("phrase", {}) or {}
    markers = plan.get("markers", {}) or {}

    theme_text = theme_phrase.get("text", "")
    notice_texts = [i.get("phrase", {}).get("text", "") for i in notice_items if i.get("phrase")]
    scene_texts = [i.get("phrase", {}).get("text", "") for i in scene_items if i.get("phrase")]
    micro_text = micro_phrase.get("text", "")

    needs = user_context.get("needs") if user_context else request.get("context") or ""
    needs_map = {
        "money": "деньги, финансовая стабильность, изобилие",
        "love": "любовь, отношения, близость, романтика",
        "calm": "спокойствие, умиротворение, баланс, гармония",
        "work": "работа, карьера, профессиональный рост, достижения",
        "health": "здоровье, энергия, тело, самочувствие",
        "relationship": "отношения, общение, связи с людьми",
        "creativity": "творчество, вдохновение, самовыражение",
        "spirituality": "духовность, смысл, связь с высшим"
    }
    needs_description = needs_map.get(needs.lower(), needs) if needs else "общее благополучие и гармония"
    
    parts = [f"Дата прогноза: {request.get('date', 'сегодня')}."]

    has_natal_chart = False
    if user_context and user_context.get("natal_chart"):
        natal = user_context["natal_chart"]
        has_natal_chart = True
        natal_info = []
        if natal.get("sun_sign"):
            natal_info.append(f"Солнце: {natal['sun_sign']}")
        if natal.get("moon_sign"):
            natal_info.append(f"Луна: {natal['moon_sign']}")
        if natal.get("ascendant"):
            natal_info.append(f"Асцендент: {natal['ascendant']}")
        if natal.get("planets"):
            key_planets = [p for p in natal["planets"] if p.get("name") in ["Venus", "Mars", "Mercury", "Jupiter", "Saturn"]]
            for p in key_planets:
                planet_name_ru = {
                    "Venus": "Венера",
                    "Mars": "Марс",
                    "Mercury": "Меркурий",
                    "Jupiter": "Юпитер",
                    "Saturn": "Сатурн",
                }.get(p.get("name"), p.get("name"))
                natal_info.append(f"{planet_name_ru}: {p.get('sign')}")
        if natal_info:
            parts.append("Профиль пользователя:")
            parts.extend(f"- {line}" for line in natal_info)
    if not has_natal_chart:
        parts.append("Профиль пользователя: полной натальной карты нет. Не выдумывай лишнее, опирайся на контекст дня.")

    day_context: List[str] = []
    if user_context and user_context.get("numerology"):
        num = user_context["numerology"]
        if num.get("day_number"):
            day_context.append(f"Число дня: {num['day_number']}")
            if num.get("day_meaning"):
                day_context.append(f"Смысл числа дня: {num['day_meaning']}")
            if num.get("day_title"):
                day_context.append(f"Фокус числа дня: {num['day_title']}")
        if num.get("life_path"):
            day_context.append(f"Число жизненного пути: {num['life_path']}")
        if num.get("personal_year"):
            day_context.append(f"Личный год: {num['personal_year']}")

    if user_context and user_context.get("tarot_card"):
        tarot = user_context["tarot_card"]
        day_context.append(f"Карта дня: {tarot.get('card_name', '')} ({tarot.get('orientation', 'прямая')})")

    if day_context:
        parts.append("Контекст дня:")
        parts.extend(f"- {line}" for line in day_context)

    parts.append(f"Запрос пользователя: {needs_description}.")

    if user_context and user_context.get("profile"):
        profile = user_context["profile"]
        if profile.get("axes") or profile.get("modulators"):
            parts.append("Психологический контекст:")
            if profile.get("axes"):
                parts.append(f"- Оси: {profile['axes']}")
            if profile.get("modulators"):
                parts.append(f"- Модуляторы: {profile['modulators']}")

    parts.extend([
        "Опорные фразы. Используй их только как материал, не копируй буквально:",
        f"- theme: {theme_text or '(нет)'}",
        f"- notice: {notice_texts}",
        f"- scene: {scene_texts}",
        f"- micro_action: {micro_text or '(нет)'}",
        (
            f"Маркерные детали: body={markers.get('body', [])}; social={markers.get('social', [])}; "
            f"domestic={markers.get('domestic', [])}; micro_action={markers.get('micro_action', [])}."
        ),
        (
            "Задача: напиши цельный прогноз дня для одного человека. Объясни, что сегодня усиливается, "
            "на что смотреть, где это проявится в обычной жизни и какой маленький шаг даст ощущение опоры."
        ),
        "Если данных мало, лучше дать спокойный и полезный текст, чем выдумывать глубину.",
        "Только JSON, без markdown и пояснений.",
    ])
    return "\n".join(parts)


def _parse_llm_json(raw: str) -> Optional[Dict[str, Any]]:
    raw = raw.strip()
    # Убираем markdown code block если есть
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if m:
        raw = m.group(1).strip()
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and "theme" in data and "notice" in data and "scene" in data and "micro_action" in data:
            return data
    except json.JSONDecodeError:
        pass
    return None


def _fallback_blocks(request: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    needs = ((user_context or {}).get("needs") or request.get("context") or "general").lower()
    natal = (user_context or {}).get("natal_chart") or {}
    sun = natal.get("sun_sign")
    moon = natal.get("moon_sign")
    anchor = f"Солнце в {sun} и Луна в {moon}" if sun and moon else "твой личный ритм"

    need_focus = {
        "money": "финансовые договоренности и цена твоего времени",
        "love": "качество диалога и эмоциональная ясность",
        "calm": "снижение лишнего шума и восстановление ресурса",
        "work": "приоритизация задач и управляемый темп",
        "health": "режим тела, вода и короткое восстановление",
    }.get(needs, "один главный приоритет дня")

    return {
        "theme": f"Через {anchor} день лучше раскрывается там, где ты выбираешь один ясный приоритет вместо рассыпанного внимания на {need_focus}.",
        "notice": [
            "Утром особенно важно понять, что действительно главное, а что только шумит и просит немедленной реакции.",
            "В разговорах и договоренностях сегодня лучше работает простота: меньше намеков, больше прямых формулировок и конкретных сроков.",
        ],
        "scene": [
            "В работе, деньгах или домашних делах хороший результат даст короткий понятный план без попытки удержать в голове всё сразу.",
            "В отношениях и переписке заметно проявится твой тон: спокойный ответ укрепит контакт, резкий ответ создаст лишнее напряжение.",
        ],
        "micro_action": "Запиши один главный результат дня и один шаг, который можно сделать в ближайшие десять минут.",
    }


def _is_valid_forecast_blocks(blocks: Dict[str, Any]) -> bool:
    theme = str(blocks.get("theme") or "")
    notice = blocks.get("notice") or []
    scene = blocks.get("scene") or []
    micro_action = str(blocks.get("micro_action") or "")

    ok_theme, _ = is_meaningful_sentence(theme, min_words=6)
    if not ok_theme:
        return False
    if not isinstance(notice, list) or len(notice) < 2:
        return False
    if not isinstance(scene, list) or len(scene) < 2:
        return False
    for line in notice[:2] + scene[:2]:
        ok, _ = is_meaningful_sentence(str(line), min_words=5)
        if not ok:
            return False
    ok_action, _ = is_meaningful_sentence(micro_action, min_words=4)
    if not ok_action or not has_action_verb(micro_action):
        return False
    return True


def generate_forecast_blocks(
    plan: Dict[str, Any], 
    request: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Вызывает OpenAI для генерации блоков прогноза (theme, notice, scene, micro_action).
    plan и request — те же структуры, что у Planner/Writer (dict-представление).
    user_context — контекст пользователя (нумерология, дневники, практики и т.д.).
    Возвращает {'theme': str, 'notice': list[str], 'scene': list[str], 'micro_action': str} или None.
    """
    if not is_llm_chat_configured():
        return None

    client = get_openai_compatible_client()
    if client is None:
        return None

    model_id = resolve_default_chat_model()
    user_prompt = _build_user_prompt(plan, request, user_context)
    started_at = perf_counter()

    try:
        content = chat_completion_plain(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,  # Оптимальный баланс между творчеством и точностью
            max_tokens=resolve_max_tokens(1200),
        )
    except Exception as e:
        logger.warning(f"OpenAI API error: {e}", exc_info=True)
        _log_generation_event(
            module="forecast",
            surface="forecast_blocks",
            prompt_version=FORECAST_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            input_payload={"plan": plan, "request": request},
            raw_response=None,
            normalized_response=None,
            user_context=user_context,
            status="error",
            used_fallback=False,
            error_message=str(e),
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return None

    if not content:
        _log_generation_event(
            module="forecast",
            surface="forecast_blocks",
            prompt_version=FORECAST_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            input_payload={"plan": plan, "request": request},
            raw_response=content,
            normalized_response=None,
            user_context=user_context,
            status="empty",
            used_fallback=False,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return None

    parsed = _parse_llm_json(content)
    if not parsed:
        _log_generation_event(
            module="forecast",
            surface="forecast_blocks",
            prompt_version=FORECAST_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            input_payload={"plan": plan, "request": request},
            raw_response=content,
            normalized_response=None,
            user_context=user_context,
            status="invalid_json",
            used_fallback=False,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return None

    # Нормализуем типы
    theme = parsed.get("theme")
    notice = parsed.get("notice")
    scene = parsed.get("scene")
    micro_action = parsed.get("micro_action")

    if not isinstance(theme, str):
        theme = str(theme) if theme else ""
    if not isinstance(notice, list):
        notice = [notice] if notice else []
    notice = [str(x) for x in notice if x]
    if not isinstance(scene, list):
        scene = [scene] if scene else []
    scene = [str(x) for x in scene if x]
    if not isinstance(micro_action, str):
        micro_action = str(micro_action) if micro_action else ""

    candidate = {
        "theme": theme or "",
        "notice": notice if notice else [],
        "scene": scene if scene else [],
        "micro_action": micro_action or "",
    }
    if not _is_valid_forecast_blocks(candidate):
        logger.warning("LLM forecast blocks rejected by semantic quality checks")
        fallback = _fallback_blocks(request, user_context)
        _log_generation_event(
            module="forecast",
            surface="forecast_blocks",
            prompt_version=FORECAST_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            input_payload={"plan": plan, "request": request},
            raw_response=content,
            normalized_response=fallback,
            user_context=user_context,
            status="fallback",
            used_fallback=True,
            error_message="semantic_validation_failed",
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
    _log_generation_event(
        module="forecast",
        surface="forecast_blocks",
        prompt_version=FORECAST_PROMPT_VERSION,
        model=model_id,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        input_payload={"plan": plan, "request": request},
        raw_response=content,
        normalized_response=candidate,
        user_context=user_context,
        status="success",
        used_fallback=False,
        duration_ms=int((perf_counter() - started_at) * 1000),
    )
    return candidate


SYSTEM_PROMPT_DAY_MEANING = """Ты пишешь ежедневную интерпретацию для TodayFlow на основе уже собранного смысла дня.

Нельзя придумывать новый смысл. Нужно сделать из входных данных живой, точный и читаемый прогноз для конкретного человека.

Приоритеты:
- понять, что сегодня происходит;
- связать это с профилем человека;
- показать, как это проявится в обычной жизни;
- закончить одним маленьким действием.

Не пиши:
- туманные духовные формулы;
- повторы одного и того же смысла в разных блоках;
- абстрактные обещания без связи с жизнью.
- формулировки, которые подошли бы любому человеку;
- сухие технические пересказы астрологии без перевода на бытовой язык.

Пиши:
- коротко;
- конкретно;
- психологически правдоподобно;
- так, чтобы чувствовалось личное сопровождение.

Каждый блок должен быть приземленным:
- theme: один ясный нерв дня;
- notice: на что смотреть в поведении, разговорах, решениях;
- scene: обычные жизненные ситуации, а не красивые метафоры;
- micro_action: маленькое действие, которое действительно можно сделать сразу.

Верни только JSON:
{"theme":"...","notice":["...","..."],"scene":["...","..."],"micro_action":"..."}
"""


def generate_forecast_from_meaning(
    day_meaning: Dict[str, Any],
    interpretation_focus: Dict[str, Any],
    lexicon_entries: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    locale: str = "ru"
) -> Optional[Dict[str, Any]]:
    """
    Генерирует прогноз из DayMeaning (правильный пайплайн).
    
    day_meaning: смысловое состояние дня (из систем)
    interpretation_focus: интерпретационный фокус
    lexicon_entries: подобранные фразы из лексикона (как язык)
    user_context: контекст пользователя (натальная карта и т.д.)
    """
    if not is_llm_chat_configured():
        return None

    client = get_openai_compatible_client()
    if client is None:
        return None

    model_id = resolve_default_chat_model()
    # Формируем промпт на основе DayMeaning
    user_prompt = _build_meaning_prompt(day_meaning, interpretation_focus, lexicon_entries, user_context, locale)
    started_at = perf_counter()

    try:
        content = chat_completion_plain(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_DAY_MEANING},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=resolve_max_tokens(1200),
        )
    except Exception as e:
        logger.warning(f"OpenAI API error: {e}", exc_info=True)
        _log_generation_event(
            module="forecast",
            surface="day_meaning",
            prompt_version=DAY_MEANING_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT_DAY_MEANING,
            user_prompt=user_prompt,
            input_payload={
                "day_meaning": day_meaning,
                "interpretation_focus": interpretation_focus,
                "lexicon_entries": lexicon_entries,
            },
            raw_response=None,
            normalized_response=None,
            user_context=user_context,
            status="error",
            used_fallback=False,
            error_message=str(e),
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return None

    if not content:
        _log_generation_event(
            module="forecast",
            surface="day_meaning",
            prompt_version=DAY_MEANING_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT_DAY_MEANING,
            user_prompt=user_prompt,
            input_payload={
                "day_meaning": day_meaning,
                "interpretation_focus": interpretation_focus,
                "lexicon_entries": lexicon_entries,
            },
            raw_response=content,
            normalized_response=None,
            user_context=user_context,
            status="empty",
            used_fallback=False,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return None

    parsed = _parse_llm_json(content)
    if not parsed:
        _log_generation_event(
            module="forecast",
            surface="day_meaning",
            prompt_version=DAY_MEANING_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT_DAY_MEANING,
            user_prompt=user_prompt,
            input_payload={
                "day_meaning": day_meaning,
                "interpretation_focus": interpretation_focus,
                "lexicon_entries": lexicon_entries,
            },
            raw_response=content,
            normalized_response=None,
            user_context=user_context,
            status="invalid_json",
            used_fallback=False,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return None

    # Нормализуем типы
    theme = parsed.get("theme")
    notice = parsed.get("notice")
    scene = parsed.get("scene")
    micro_action = parsed.get("micro_action")

    if not isinstance(theme, str):
        theme = str(theme) if theme else ""
    if not isinstance(notice, list):
        notice = [notice] if notice else []
    notice = [str(x) for x in notice if x]
    if not isinstance(scene, list):
        scene = [scene] if scene else []
    scene = [str(x) for x in scene if x]
    if not isinstance(micro_action, str):
        micro_action = str(micro_action) if micro_action else ""

    candidate = {
        "theme": theme or "",
        "notice": notice if notice else [],
        "scene": scene if scene else [],
        "micro_action": micro_action or "",
    }
    if not _is_valid_forecast_blocks(candidate):
        logger.warning("LLM day-meaning forecast rejected by semantic quality checks")
        fallback = _fallback_blocks({"context": day_meaning.get("focus_area")}, user_context)
        _log_generation_event(
            module="forecast",
            surface="day_meaning",
            prompt_version=DAY_MEANING_PROMPT_VERSION,
            model=model_id,
            system_prompt=SYSTEM_PROMPT_DAY_MEANING,
            user_prompt=user_prompt,
            input_payload={
                "day_meaning": day_meaning,
                "interpretation_focus": interpretation_focus,
                "lexicon_entries": lexicon_entries,
            },
            raw_response=content,
            normalized_response=fallback,
            user_context=user_context,
            status="fallback",
            used_fallback=True,
            error_message="semantic_validation_failed",
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
    _log_generation_event(
        module="forecast",
        surface="day_meaning",
        prompt_version=DAY_MEANING_PROMPT_VERSION,
        model=model_id,
        system_prompt=SYSTEM_PROMPT_DAY_MEANING,
        user_prompt=user_prompt,
        input_payload={
            "day_meaning": day_meaning,
            "interpretation_focus": interpretation_focus,
            "lexicon_entries": lexicon_entries,
        },
        raw_response=content,
        normalized_response=candidate,
        user_context=user_context,
        status="success",
        used_fallback=False,
        duration_ms=int((perf_counter() - started_at) * 1000),
    )
    return candidate


def _log_generation_event(
    *,
    module: str,
    surface: str,
    prompt_version: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    input_payload: dict[str, Any],
    raw_response: str | None,
    normalized_response: dict[str, Any] | None,
    user_context: Optional[Dict[str, Any]],
    status: str,
    used_fallback: bool,
    error_message: str | None = None,
    duration_ms: int | None = None,
) -> None:
    user_id = (user_context or {}).get("user_id")
    if not user_id:
        return

    db = SessionLocal()
    try:
        learning_service = get_learning_service()
        prompt = learning_service.get_or_create_prompt_version(
            db,
            module=module,
            version=prompt_version,
            prompt_kind="system",
            prompt_text=system_prompt,
            label=surface,
            metadata={"surface": surface},
        )
        latest_snapshot = (
            db.query(CoreProfileSnapshot)
            .filter(CoreProfileSnapshot.user_id == user_id)
            .order_by(CoreProfileSnapshot.updated_at.desc())
            .first()
        )
        learning_service.log_generation(
            db,
            module=module,
            surface=surface,
            user_id=user_id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt.id,
            model=model,
            locale="ru",
            input_payload=input_payload,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            raw_response=raw_response,
            normalized_response=normalized_response,
            status=status,
            used_fallback=used_fallback,
            error_message=error_message,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        logger.debug("Failed to log generation event: %s", exc, exc_info=True)
    finally:
        db.close()


def _build_meaning_prompt(
    day_meaning: Dict[str, Any],
    interpretation_focus: Dict[str, Any],
    lexicon_entries: Dict[str, Any],
    user_context: Optional[Dict[str, Any]],
    locale: str
) -> str:
    """Строит компактный промпт для ИИ на основе DayMeaning."""
    prompt_parts = [
        "Собери прогноз дня из уже определенного смысла.",
        f"Дата: {day_meaning.get('date')}",
        f"Направление: {day_meaning.get('interpretation_direction')}",
        f"Фокусная область: {day_meaning.get('focus_area')}",
        f"Интенсивность: {day_meaning.get('intensity')}",
    ]

    astro_state = day_meaning.get('astro_state', {})
    prompt_parts.append("Астрологический контекст:")
    if astro_state.get('tensions'):
        prompt_parts.append("Напряжения:")
        for tension in astro_state['tensions'][:3]:
            prompt_parts.append(f"- {tension.get('description', str(tension))}")
    if astro_state.get('resources'):
        prompt_parts.append("Ресурсы:")
        for resource in astro_state['resources'][:3]:
            prompt_parts.append(f"- {resource.get('description', str(resource))}")

    numerology = day_meaning.get('numerology_context')
    if numerology:
        prompt_parts.append("Нумерологический контекст:")
        prompt_parts.append(f"- Personal Day: {numerology.get('personal_day')}")
        if numerology.get('personal_year'):
            prompt_parts.append(f"- Personal Year: {numerology.get('personal_year')}")
        if numerology.get('day_number_title'):
            prompt_parts.append(f"- Число дня: {numerology.get('day_number_title')}")

    archetype = day_meaning.get('archetype')
    if archetype:
        prompt_parts.append("Архетип дня:")
        prompt_parts.append(f"- Карта: {archetype.get('name')} ({archetype.get('orientation')})")
        if archetype.get('keywords'):
            prompt_parts.append(f"- Ключевые слова: {', '.join(archetype['keywords'])}")

    if user_context:
        prompt_parts.append("Профиль пользователя:")
        natal_chart = user_context.get('natal_chart')
        if natal_chart:
            prompt_parts.append(f"- Солнце: {natal_chart.get('sun_sign', 'не указано')}")
            prompt_parts.append(f"- Луна: {natal_chart.get('moon_sign', 'не указано')}")
            prompt_parts.append(f"- Асцендент: {natal_chart.get('rising_sign', 'не указано')}")
        else:
            prompt_parts.append("- Полной натальной карты нет.")

    prompt_parts.append("Опорный язык:")
    if lexicon_entries.get('theme'):
        theme_phrases = lexicon_entries['theme']
        if theme_phrases:
            prompt_parts.append(f"- Theme example: {theme_phrases[0].get('text', '')[:100]}")
    if lexicon_entries.get('notice'):
        notice_phrases = lexicon_entries['notice']
        if notice_phrases:
            prompt_parts.append(f"- Notice examples: {', '.join([p.get('text', '')[:50] for p in notice_phrases[:2]])}")

    prompt_parts.append("Задача:")
    prompt_parts.append("- не придумывай новый смысл;")
    prompt_parts.append("- свяжи входные данные в один цельный прогноз;")
    prompt_parts.append("- покажи, как это проявится в разговорах, выборе задач, деньгах, отношениях или бытовых решениях;")
    prompt_parts.append("- избегай шаблонных и мертвых фраз;")
    prompt_parts.append("- если упоминаешь астрологию, нумерологию или карту дня, сразу объясняй человеческим языком, что это меняет сегодня;")
    prompt_parts.append("- не используй слова ради атмосферы, если они не добавляют смысла;")
    prompt_parts.append("Верни только JSON, без markdown и пояснений.")
    
    return "\n".join(prompt_parts)
