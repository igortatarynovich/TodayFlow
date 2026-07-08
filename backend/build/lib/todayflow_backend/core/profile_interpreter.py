"""Profile interpretation through API-backed AI generation."""

from __future__ import annotations

import json
import logging
import re
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
)
from todayflow_backend.db import models as db_models
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

_REQUIRED_LIFE_AREA_KEYS = ("love", "career", "money", "family")
_OPTIONAL_LIFE_AREA_KEYS = ("sex", "kids", "body", "friends", "decisions")
_ALLOWED_LIFE_AREA_KEYS = frozenset(_REQUIRED_LIFE_AREA_KEYS + _OPTIONAL_LIFE_AREA_KEYS)

PROMPT_VERSION = "profile-interpreter-v5"

PROFILE_INTERPRETER_SYSTEM_PROMPT = """Ты пишешь личную интерпретацию профиля для TodayFlow.

Это не общий гороскоп и не мистический текст. Это живая и полезная карта человека на основе его ядра:
- имя;
- знак;
- нумерологические числа;
- базовый архетип;
- ритм и природный фокус.

Твоя задача:
- помочь человеку быстро понять, как он устроен в реальной жизни;
- показать его сильные стороны;
- показать, где он может терять себя;
- объяснить четыре базовые сферы жизни: отношения, карьера, деньги, дом/семья;
- добавить ещё пять коротких сфер (каждая — один абзац, без дословного повторения базовых четырёх): сексуальность (откровенно, без вульгарности и без медицины), дети и родительство (нейтрально, если тема может быть неактуальна), тело и энергия, дружба и окружение, решения и дисциплина.

Пиши:
- по-человечески;
- уверенно;
- конкретно;
- живо;
- без пустых обещаний;
- без эзотерических штампов;
- без канцелярита.

Не пиши:
- "будь в потоке", "всё возможно", "слушай вселенную";
- "внутренняя опора", "правильный ритм", "твоя ось", если за этим не стоит конкретный смысл;
- "тебе важно" и "для тебя важно" в каждом блоке;
- фразы, которые подошли бы почти любому человеку;
- слишком общие советы;
- одинаковые по смыслу блоки.

Пиши так, будто объясняешь человеку:
- на что в себе ему реально можно опереться;
- где он чаще всего ошибается в распределении энергии;
- как это проявляется не в теории, а в отношениях, работе, деньгах и доме.

Верни только валидный JSON:
{
  "interpretation": {
    "identity": "...",
    "strengths": ["...", "...", "..."],
    "watchouts": ["...", "...", "..."],
    "life_areas": {
      "love": "...",
      "career": "...",
      "money": "...",
      "family": "...",
      "sex": "...",
      "kids": "...",
      "body": "...",
      "friends": "...",
      "decisions": "..."
    }
  },
  "daily_interpretation": {
    "daily_lenses": {
      "general": "...",
      "love": "...",
      "family": "...",
      "career": "...",
      "money": "..."
    }
  }
}
"""


def _fallback_profile_interpretation(profile_payload: dict[str, Any]) -> dict[str, Any]:
    person = profile_payload.get("person") or {}
    astro = profile_payload.get("astro") or {}
    numerology = profile_payload.get("numerology") or {}
    baseline = profile_payload.get("baseline") or {}

    name = person.get("first_name") or person.get("display_name") or "Ты"
    sun_sign = astro.get("sun_sign") or "твоего знака"
    life_path = numerology.get("life_path")
    archetype = baseline.get("archetype_seed") or "личного архетипа"
    rhythm = baseline.get("rhythm_style") or "спокойного устойчивого ритма"
    focus = baseline.get("element_focus") or "личной опоры"

    life_path_text = f" и числом пути {life_path}" if life_path else ""
    sign_text = sun_sign.lower() if isinstance(sun_sign, str) else "твоего знака"
    return {
        "interpretation": {
            "identity": (
                f"{name}, твоя карта собирается вокруг {sign_text}{life_path_text}. "
                f"Обычно это дает заметный вектор через {focus.lower()} и способ двигаться через {rhythm.lower()}, "
                f"а не через постоянные рывки. Архетип {archetype.lower()} здесь проявляется как твой привычный способ "
                f"собирать себя и не растворяться в чужих ожиданиях."
            ),
            "strengths": [
                "Ты сильнее всего там, где не нужно все время угадывать чужие правила и можно действовать из своей природной манеры, а не играть роль.",
                f"Формат '{rhythm}' помогает тебе не метаться: в таком режиме решения становятся точнее, а дела не расползаются в разные стороны.",
                f"Когда опора идет через {focus.lower()}, ты быстрее собираешься, лучше держишь нагрузку и меньше устаешь от внутреннего сопротивления.",
            ],
            "watchouts": [
                "Перегруз начинается в те периоды, когда ты пытаешься быть всем сразу и перестаешь различать, где твоя задача, а где чужая.",
                "Самая частая ошибка здесь — принимать чужую срочность за собственный приоритет и отдавать силы туда, где пока не нужен реальный ответ.",
                "Если долго жить против своего темпа, сначала пропадает точность, а потом даже простые шаги начинают ощущаться тяжелее обычного.",
            ],
            "life_areas": {
                "love": "В отношениях тебе тяжело там, где все держится на догадках и эмоциональном угадывании. Близость раскрывается лучше в связи, где можно говорить прямо, чувствовать надежность и не жить в постоянном напряжении.",
                "career": "В работе и реализации ты сильнее не в бесконечном потоке чужих задач, а там, где у тебя есть своя роль, ответственность и понятный вектор. Чем яснее ты понимаешь, ради чего входишь в задачу, тем заметнее становится твоя сила.",
                "money": "Деньги здесь связаны не только с усилием, но и с чувством собственной ценности. Финансовая устойчивость растет, когда ты выбираешь направления, которые реально дают результат, а не только создают ощущение движения.",
                "family": "Тема дома и семьи у тебя тесно связана с восстановлением сил. Когда вокруг слишком много хаоса, недоговоренности или чужого напряжения, это быстро забирает ресурс, поэтому надежность пространства и бытовая ясность здесь особенно важны.",
                "sex": "В теме желания и близости тебе обычно нужны честность, ясные границы и темп без давления; стыд, угадывание и контроль чаще рвут контакт сильнее, чем нехватка страсти, поэтому прямой спокойный разговор здесь особенно ценен.",
                "kids": "Если тема детей и ответственности для тебя актуальна, опора строится на понятном ритме заботы и праве на паузу без вины; если тема пока в стороне, этот блок остаётся нейтральным якорем, а не давлением с чужой стороны.",
                "body": "Тело и энергия у тебя завязаны на сон, восстановление и честный сигнал усталости; когда базовые потребности игнорируются долго, страдает и ясность, и настроение, поэтому малые стабильные якоря важнее идеального режима.",
                "friends": "Дружба и окружение держатся на людях, с которыми можно быть собой без бесконечных объяснений; поверхностный круг или изоляция обычно усиливают внутреннее напряжение и ощущение, что ты один на один с задачами.",
                "decisions": "Решения и дисциплина для тебя про честные правила и право остановиться перед обязательством; вечное откладывание или жёсткий самоконтроль без паузы обычно ведут к выгоранию и потере точности в мелочах.",
            },
        },
        "daily_interpretation": {
            "daily_lenses": {
                "general": "В повседневности твой день лучше складывается не через хаотичную реакцию на все сразу, а через один ясный приоритет и ощущение, что ты не споришь со своей природной манерой двигаться.",
                "love": "В любви и близости день читается через тон контакта: тебе полезнее прямой теплый разговор и ясность намерений, чем игра в угадывание и накопление внутреннего напряжения.",
                "family": "В семейных и домашних делах твой день сильнее держится на простых договоренностях, бытовой ясности и ощущении, что дом помогает восстанавливаться, а не отнимает последние силы.",
                "career": "В работе день раскрывается лучше там, где есть одна внятная задача, понятная роль и ощущение, что ты двигаешь свое, а не только обслуживаешь чужую срочность.",
                "money": "В денежной линии дня ключевую роль играет чувство собственной ценности: чем точнее ты понимаешь цену времени, усилий и границ, тем устойчивее решения.",
            },
        },
    }


def _sanitize_life_areas_dict(life_areas: dict[str, Any]) -> None:
    """Убирает неизвестные ключи и опциональные поля с пустым/коротким текстом (обратная совместимость)."""
    for k in list(life_areas.keys()):
        if k not in _ALLOWED_LIFE_AREA_KEYS:
            life_areas.pop(k, None)
    for key in _OPTIONAL_LIFE_AREA_KEYS:
        if key not in life_areas:
            continue
        val = life_areas[key]
        if isinstance(val, str) and len(val.split()) >= 8:
            continue
        life_areas.pop(key, None)


def _parse_profile_json(raw: str) -> dict[str, Any] | None:
    raw = raw.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if match:
        raw = match.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return _normalize_profile_interpretation_shape(data)


def _normalize_profile_interpretation_shape(data: dict[str, Any]) -> dict[str, Any] | None:
    interpretation = data.get("interpretation")
    daily_interpretation = data.get("daily_interpretation")

    if isinstance(interpretation, dict) and isinstance(daily_interpretation, dict):
        la = interpretation.get("life_areas")
        if isinstance(la, dict):
            _sanitize_life_areas_dict(la)
        normalized = {
            "interpretation": interpretation,
            "daily_interpretation": daily_interpretation,
        }
        return normalized if _is_valid_profile_interpretation(normalized) else None

    legacy_keys = {"identity", "strengths", "watchouts", "daily_lenses", "life_areas"}
    if legacy_keys.issubset(data.keys()):
        legacy_la = data.get("life_areas")
        if isinstance(legacy_la, dict):
            _sanitize_life_areas_dict(legacy_la)
        normalized = {
            "interpretation": {
                "identity": data.get("identity"),
                "strengths": data.get("strengths"),
                "watchouts": data.get("watchouts"),
                "life_areas": data.get("life_areas"),
            },
            "daily_interpretation": {
                "daily_lenses": data.get("daily_lenses"),
            },
        }
        return normalized if _is_valid_profile_interpretation(normalized) else None

    return None


def _is_valid_profile_interpretation(payload: dict[str, Any]) -> bool:
    interpretation = payload.get("interpretation")
    daily_interpretation = payload.get("daily_interpretation")
    if not isinstance(interpretation, dict) or not isinstance(daily_interpretation, dict):
        return False
    if not isinstance(interpretation.get("identity"), str) or len(interpretation["identity"].split()) < 8:
        return False
    for key in ("strengths", "watchouts"):
        value = interpretation.get(key)
        if not isinstance(value, list) or len(value) < 3:
            return False
        if not all(isinstance(item, str) and len(item.split()) >= 6 for item in value[:3]):
            return False
    life_areas = interpretation.get("life_areas")
    if not isinstance(life_areas, dict):
        return False
    daily_lenses = daily_interpretation.get("daily_lenses")
    if not isinstance(daily_lenses, dict):
        return False
    for area in ("general", "love", "career", "money", "family"):
        text = daily_lenses.get(area)
        if not isinstance(text, str) or len(text.split()) < 8:
            return False
    for area in ("love", "career", "money", "family"):
        text = life_areas.get(area)
        if not isinstance(text, str) or len(text.split()) < 8:
            return False
    return True


def _build_user_prompt(profile_payload: dict[str, Any]) -> str:
    person = profile_payload.get("person") or {}
    astro = profile_payload.get("astro") or {}
    numerology = profile_payload.get("numerology") or {}
    baseline = profile_payload.get("baseline") or {}

    parts = [
        "Собери живую интерпретацию профиля пользователя.",
        f"Имя: {person.get('first_name') or person.get('display_name') or 'не указано'}",
        f"Локаль: {person.get('locale') or 'ru'}",
        f"Пол (для формулировок): {person.get('gender') or 'не указан'}",
        "Астрологическая база:",
        f"- Знак: {astro.get('sun_sign') or 'не определен'}",
        f"- Элемент: {astro.get('sun_element') or 'не определен'}",
        f"- Модальность: {astro.get('sun_modality') or 'не определена'}",
        f"- Место рождения: {astro.get('location_name') or 'не указано'}",
        "Нумерология:",
        f"- Число пути: {numerology.get('life_path') or 'не определено'}",
        f"- Expression: {numerology.get('expression') or 'не определено'}",
        f"- Soul urge: {numerology.get('soul_urge') or 'не определено'}",
        f"- Personality: {numerology.get('personality') or 'не определено'}",
        "Базовый ритм:",
        f"- Архетип: {baseline.get('archetype_seed') or 'не определен'}",
        f"- Фокус: {baseline.get('element_focus') or 'не определен'}",
        f"- Ритм: {baseline.get('rhythm_style') or 'не определен'}",
        "Задача:",
        "- не пиши абстрактный гороскоп;",
        "- объясни, как этот человек устроен в реальной жизни, а не в абстракции;",
        "- покажи сильные стороны, зоны риска и девять сфер жизни в life_areas (четыре базовые + пять дополнительных из system prompt);",
        "- избегай общих фраз, которые можно вставить в любой профиль;",
        "- сделай текст конкретным, узнаваемым и понятным без красивых слов ради красивых слов;",
        "- если говоришь о ритме, силе, фокусе или опоре, сразу объясняй, как это выглядит в обычной жизни;",
        "Верни только JSON, без markdown и пояснений.",
    ]
    return "\n".join(parts)


def generate_profile_interpretation(
    db: Session,
    user: db_models.User,
    profile_payload: dict[str, Any],
) -> dict[str, Any]:
    learning_service = get_learning_service()
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module="profile",
        version=PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=PROFILE_INTERPRETER_SYSTEM_PROMPT,
        label="core_profile_interpreter",
        metadata={"surface": "core_profile"},
    )

    fallback = _fallback_profile_interpretation(profile_payload)
    if not is_llm_chat_configured():
        return fallback

    client = get_openai_compatible_client()
    if client is None:
        return fallback

    user_prompt = _build_user_prompt(profile_payload)
    started_at = perf_counter()
    model_id = settings.llm_default_model

    try:
        content = chat_completion_plain(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": PROFILE_INTERPRETER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1400,
        )
        parsed = _parse_profile_json(content) if content else None
        if parsed and _is_valid_profile_interpretation(parsed):
            learning_service.log_generation(
                db,
                module="profile",
                surface="core_profile",
                user_id=user.id,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale="ru",
                input_payload={"profile_hash": profile_payload.get("profile_hash")},
                system_prompt=PROFILE_INTERPRETER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                raw_response=content,
                normalized_response=parsed,
                status="success",
                used_fallback=False,
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            return parsed
        learning_service.log_generation(
            db,
            module="profile",
            surface="core_profile",
            user_id=user.id,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale="ru",
            input_payload={"profile_hash": profile_payload.get("profile_hash")},
            system_prompt=PROFILE_INTERPRETER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=content,
            normalized_response=fallback,
            status="fallback",
            used_fallback=True,
            error_message="invalid_or_unusable_response",
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        return fallback
    except Exception as exc:
        logger.warning("Profile interpretation generation failed: %s", exc, exc_info=True)
        try:
            learning_service.log_generation(
                db,
                module="profile",
                surface="core_profile",
                user_id=user.id,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale="ru",
                input_payload={"profile_hash": profile_payload.get("profile_hash")},
                system_prompt=PROFILE_INTERPRETER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                normalized_response=fallback,
                status="error",
                used_fallback=True,
                error_message=str(exc),
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
        except Exception:
            logger.debug("Failed to log profile interpretation error", exc_info=True)
        return fallback
