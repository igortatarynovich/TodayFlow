"""Editorial layer for natal-chart response with compact memory."""

from __future__ import annotations

import json
import logging
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import CoreProfileSnapshot
from todayflow_backend.services.learning import get_learning_service

logger = logging.getLogger(__name__)

MODULE = "natal_chart"
SURFACE = "natal_chart_editorial"
PROMPT_VERSION = "natal-chart-editorial-v2"

SYSTEM_PROMPT = """Ты пишешь короткий editorial layer для экрана Personal Map (натальная карта как источник данных), TodayFlow.

Роль слоя: это НЕ второй длинный портрет пользователя и НЕ экран «сегодня». Не дублируй развёрнутый личный портрет из профиля (identity, длинные life_areas) — только тезис по структуре карты.

Задача:
- собрать главную мысль карты человеческим языком на уровне опор и напряжений;
- опереться на дома, личные планеты, углы, аспекты и устойчивые черты профиля (baseline), без дневных линз;
- не пересказывать весь технический payload;
- использовать прошлую memory только как короткие тезисы, а не как текст для копирования.

Запрещено в тексте (headline, summary, gifts, tensions, next_step):
- «сегодня», «фокус дня», «перенеси в день», «в Today», призыв жить «этим днём», любой дневной ритуал;
- повторять один и тот же портретный абзац под разными углами;
- шаблонные пустые формулировки («знак X добавляет качества», «этот слой показывает устойчивую часть» без конкретики).

Правила:
- писать ясно, без эзотерического тумана;
- headline — 1 фраза;
- summary — 2-3 предложения про структуру карты, не про распорядок дня;
- gifts и tensions — короткие буллеты по 1 предложению;
- next_step — один следующий шаг в продукте (Guidance, совместимость, карьера/деньги, практика, Flow), но без слова «сегодня» и без Today;
- memory — короткие тезисы для следующего запроса.

Верни только JSON:
{
  "headline":"...",
  "summary":"...",
  "gifts":["...","..."],
  "tensions":["...","..."],
  "next_step":"...",
  "memory":{
    "chart_thesis":"...",
    "dominant_house":"...",
    "dominant_planet":"...",
    "growth_theme":"..."
  }
}"""


def _build_route_from_editorial(
    editorial: dict[str, Any],
    *,
    core_profile: dict[str, Any] | None,
    learning_context: dict[str, Any] | None = None,
) -> dict[str, str]:
    natal_memory = learning_context.get("natal_memory") if isinstance(learning_context, dict) and isinstance(learning_context.get("natal_memory"), dict) else {}
    preferred_targets = natal_memory.get("preferred_targets") if isinstance(natal_memory, dict) else []
    best_editorial_targets = natal_memory.get("best_editorial_targets") if isinstance(natal_memory, dict) else []

    def route_for_target(target: str) -> dict[str, str] | None:
        normalized = str(target or "").strip()
        if normalized == "compatibility":
            return {"href": "/compatibility", "label": "Посмотреть совместимость"}
        if normalized == "money_career":
            return {"href": "/questions/money-career", "label": "Открыть карьерный разбор"}
        if normalized == "practices":
            return {"href": "/practices", "label": "Подобрать практику"}
        if normalized == "today":
            return {"href": "/guidance", "label": "Разобрать в Guidance"}
        if normalized == "decision":
            return {"href": "/questions/decision", "label": "Разобрать следующий выбор"}
        if normalized == "state":
            return {"href": "/questions/state", "label": "Разобрать своё состояние"}
        if normalized == "pattern":
            return {"href": "/questions/pattern", "label": "Посмотреть свой паттерн"}
        if normalized == "questions":
            return {"href": "/questions", "label": "Задать вопрос по карте"}
        return None

    for entry in best_editorial_targets or []:
        if not isinstance(entry, dict) or int(entry.get("score") or 0) < 2:
            continue
        learned_route = route_for_target(str(entry.get("target") or ""))
        if learned_route:
            return learned_route

    for entry in preferred_targets or []:
        if not isinstance(entry, dict) or int(entry.get("score") or 0) < 3:
            continue
        learned_route = route_for_target(str(entry.get("target") or ""))
        if learned_route:
            return learned_route

    memory = editorial.get("memory") if isinstance(editorial.get("memory"), dict) else {}
    dominant_house = str(memory.get("dominant_house") or "").lower()
    dominant_planet = str(memory.get("dominant_planet") or "").lower()
    growth_theme = str(memory.get("growth_theme") or "").lower()
    next_step = str(editorial.get("next_step") or "").lower()
    summary = str(editorial.get("summary") or "").lower()
    haystack = " ".join([dominant_house, dominant_planet, growth_theme, next_step, summary])

    if any(token in haystack for token in ["партнер", "отнош", "люб", "венер", "7", "дом партн"]):
        return {"href": "/compatibility", "label": "Посмотреть совместимость"}
    if any(token in haystack for token in ["карьер", "работ", "деньг", "меркур", "марс", "сатур", "10", "6 дом"]):
        return {"href": "/questions/money-career", "label": "Открыть карьерный разбор"}
    if any(token in haystack for token in ["сем", "дом", "восстанов", "луна", "нептун", "12", "4 дом"]):
        return {"href": "/practices", "label": "Подобрать практику"}

    baseline = core_profile.get("baseline") if isinstance(core_profile, dict) and isinstance(core_profile.get("baseline"), dict) else {}
    focus = str(baseline.get("element_focus") or "").lower()
    if "ритм" in haystack or "темп" in haystack or "состоя" in haystack or "ритм" in focus:
        return {"href": "/guidance", "label": "Разобрать в Guidance"}

    return {"href": "/guidance", "label": "Разобрать в Guidance"}


def _safe_list(value: Any, *, limit: int = 4) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()][:limit]


def _trim(text: Any, fallback: str = "") -> str:
    value = str(text or "").strip()
    return value or fallback


def _top_natal_target(learning_context: dict[str, Any] | None) -> str:
    natal_memory = learning_context.get("natal_memory") if isinstance(learning_context, dict) and isinstance(learning_context.get("natal_memory"), dict) else {}
    preferred_targets = natal_memory.get("preferred_targets") if isinstance(natal_memory, dict) else []
    for entry in preferred_targets or []:
        if not isinstance(entry, dict) or int(entry.get("score") or 0) < 3:
            continue
        target = str(entry.get("target") or "").strip()
        if target:
            return target
    return ""


def _find_house_text(interpretations: dict[str, Any] | None, house_number: int) -> tuple[str, str] | None:
    houses = interpretations.get("houses") if isinstance(interpretations, dict) and isinstance(interpretations.get("houses"), dict) else {}
    item = houses.get(house_number) or houses.get(str(house_number)) if isinstance(houses, dict) else None
    if not isinstance(item, dict):
        return None
    name = _trim(item.get("name"), f"{house_number} дом")
    description = _trim(item.get("profile_lens") or item.get("description") or item.get("theme"))
    if not description:
        return None
    return name, description


def _find_planet_text(interpretations: dict[str, Any] | None, planet: str) -> tuple[str, str] | None:
    planets = interpretations.get("planets") if isinstance(interpretations, dict) and isinstance(interpretations.get("planets"), list) else []
    for item in planets:
        if not isinstance(item, dict):
            continue
        if _trim(item.get("planet")).lower() != planet.lower():
            continue
        title = _trim(item.get("planet"), planet)
        description = _trim(item.get("profile_lens") or item.get("in_house") or item.get("in_sign"))
        if not description:
            return None
        return title, description
    return None


def _find_aspect_text(aspects: dict[str, Any] | None, aspect_id: str) -> str | None:
    callouts = aspects.get("callouts") if isinstance(aspects, dict) and isinstance(aspects.get("callouts"), list) else []
    for item in callouts:
        if not isinstance(item, dict):
            continue
        if _trim(item.get("aspect_id")) != aspect_id:
            continue
        return _trim(item.get("integration") or item.get("description") or item.get("label"))
    return None


def _apply_natal_memory_editorial_bias(
    editorial: dict[str, Any],
    *,
    interpretations: dict[str, Any] | None,
    aspects: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(editorial, dict):
        return editorial

    natal_memory = learning_context.get("natal_memory") if isinstance(learning_context, dict) and isinstance(learning_context.get("natal_memory"), dict) else {}
    if not natal_memory:
        return editorial

    result = dict(editorial)
    gifts = _safe_list(result.get("gifts"), limit=3)
    tensions = _safe_list(result.get("tensions"), limit=3)
    next_step = _trim(result.get("next_step"))

    best_houses = natal_memory.get("best_houses") if isinstance(natal_memory, dict) else []
    best_planets = natal_memory.get("best_planets") if isinstance(natal_memory, dict) else []
    best_aspects = natal_memory.get("best_aspects") if isinstance(natal_memory, dict) else []
    top_target = _top_natal_target(learning_context)

    for entry in best_houses or []:
        if not isinstance(entry, dict) or int(entry.get("score") or 0) < 2:
            continue
        source_key = str(entry.get("source_key") or "").strip()
        if not source_key.isdigit():
            continue
        house_text = _find_house_text(interpretations, int(source_key))
        if not house_text:
            continue
        house_name, description = house_text
        line = f"{house_name} сейчас особенно живой для тебя: {description}"
        if str(entry.get("target") or "") in {"compatibility", "money_career", "today", "questions"}:
            if line not in gifts:
                gifts = [line, *gifts][:3]
        else:
            if line not in tensions:
                tensions = [line, *tensions][:3]
        break

    for entry in best_planets or []:
        if not isinstance(entry, dict) or int(entry.get("score") or 0) < 2:
            continue
        source_key = str(entry.get("source_key") or "").strip()
        planet_text = _find_planet_text(interpretations, source_key)
        if not planet_text:
            continue
        planet_name, description = planet_text
        line = f"{planet_name} в твоей карте лучше всего раскрывается так: {description}"
        if str(entry.get("target") or "") in {"practices", "state", "pattern"}:
            if line not in tensions:
                tensions = [line, *tensions][:3]
        else:
            if line not in gifts:
                gifts = [line, *gifts][:3]
        break

    for entry in best_aspects or []:
        if not isinstance(entry, dict) or int(entry.get("score") or 0) < 2:
            continue
        source_key = str(entry.get("source_key") or "").strip()
        aspect_text = _find_aspect_text(aspects, source_key)
        if not aspect_text:
            continue
        line = f"Одна из ключевых связей карты сейчас звучит особенно ясно: {aspect_text}"
        if line not in tensions and line not in gifts:
            if str(entry.get("target") or "") in {"practices", "state", "pattern"}:
                tensions = [line, *tensions][:3]
            else:
                gifts = [line, *gifts][:3]
        break

    if top_target == "compatibility":
        next_step = "Следующий шаг здесь лучше делать через совместимость: так быстрее видно, как твоя карта раскрывается в реальном контакте, а не только внутри тебя."
    elif top_target == "money_career":
        next_step = "Следующий шаг здесь лучше делать через карьерный разбор: так карта быстрее переводится в роль, деньги, решения и реальный вектор роста."
    elif top_target == "practices":
        next_step = "Следующий шаг здесь лучше переводить в практику: так карта помогает не только понимать себя, но и менять состояние действием."
    elif top_target == "today":
        next_step = "Следующий шаг лучше сформулировать в Guidance по конкретной теме: так опора карты переводится в вопрос или решение без дневного слоя на этом экране."
    elif top_target == "decision":
        next_step = "Следующий шаг здесь лучше делать через разбор выбора: так карта помогает не расплываться в смыслах, а сузить путь до проверяемого хода."

    result["gifts"] = gifts or _safe_list(editorial.get("gifts"), limit=3)
    result["tensions"] = tensions or _safe_list(editorial.get("tensions"), limit=3)
    result["next_step"] = next_step or _trim(editorial.get("next_step"))
    return result


def _fallback_editorial(
    *,
    core_profile: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None,
    interpretations: dict[str, Any] | None,
) -> dict[str, Any]:
    baseline = core_profile.get("baseline") if isinstance(core_profile, dict) and isinstance(core_profile.get("baseline"), dict) else {}
    interpretation = core_profile.get("interpretation") if isinstance(core_profile, dict) and isinstance(core_profile.get("interpretation"), dict) else {}
    life_areas = interpretation.get("life_areas") if isinstance(interpretation.get("life_areas"), dict) else {}
    angles = natal_summary.get("angles") if isinstance(natal_summary, dict) and isinstance(natal_summary.get("angles"), dict) else {}
    luminaries = natal_summary.get("luminaries") if isinstance(natal_summary, dict) and isinstance(natal_summary.get("luminaries"), list) else []
    houses = interpretations.get("houses") if isinstance(interpretations, dict) and isinstance(interpretations.get("houses"), dict) else {}
    first_house = houses.get(1) or houses.get("1") if isinstance(houses, dict) else None
    tenth_house = houses.get(10) or houses.get("10") if isinstance(houses, dict) else None

    dominant_planet = None
    if luminaries:
        first_luminary = luminaries[0] if isinstance(luminaries[0], dict) else {}
        dominant_planet = _trim(first_luminary.get("name"))

    return {
        "headline": _trim(
            baseline.get("archetype_seed"),
            "Карта показывает устойчивую личную линию, которую лучше читать не как набор фактов, а как живую систему твоих реакций.",
        ),
        "summary": _trim(
            interpretation.get("identity"),
            "В этой карте особенно важно, как сочетаются твой естественный ритм, способ входить в контакт и взрослая линия реализации. Когда эти части не спорят между собой, ты быстрее собираешься и точнее выбираешь, куда вкладывать силы.",
        ),
        "gifts": [
            _trim(
                angles.get("ascendant"),
                "Сильная сторона карты в том, что твой способ проявляться можно довольно быстро почувствовать и перевести в понятные решения.",
            ),
            _trim(
                life_areas.get("career"),
                "Реализация раскрывается лучше там, где у тебя есть своя роль, ответственность и ощущение, что ты двигаешь не чужую, а свою линию.",
            ),
        ],
        "tensions": [
            _trim(
                life_areas.get("family"),
                "Главное напряжение часто приходит там, где внешний темп забирает слишком много внутреннего ресурса и не остаётся пространства на восстановление.",
            ),
            _trim(
                life_areas.get("love"),
                "Связь с людьми сложнее всего держится на догадках, поэтому карте особенно нужна ясность и живой разговор вместо накопленного молчания.",
            ),
        ],
        "next_step": _trim(
            life_areas.get("money"),
            "Следующий шаг здесь — выбрать одну сферу карты, где сейчас нужен не общий анализ, а конкретное решение и живое действие.",
        ),
        "memory": {
            "chart_thesis": _trim(interpretation.get("identity"), "Карта держится на сочетании характера, темпа и главных жизненных сфер."),
            "dominant_house": _trim((first_house or {}).get("name"), "Дом личности"),
            "dominant_planet": dominant_planet or "Sun",
            "growth_theme": _trim((tenth_house or {}).get("theme"), "Линия реализации и зрелой роли"),
        },
    }


def _build_prior_memory(db: Session, *, user_id: int) -> dict[str, Any] | None:
    rows = (
        db.query(db_models.GenerationLog)
        .filter(
            db_models.GenerationLog.user_id == user_id,
            db_models.GenerationLog.module == MODULE,
            db_models.GenerationLog.surface == SURFACE,
            db_models.GenerationLog.status == "success",
        )
        .order_by(db_models.GenerationLog.created_at.desc())
        .limit(3)
        .all()
    )
    if not rows:
        return None

    history: list[dict[str, Any]] = []
    for row in rows:
        payload = row.normalized_response if isinstance(row.normalized_response, dict) else {}
        memory = payload.get("memory") if isinstance(payload.get("memory"), dict) else {}
        history.append(
            {
                "headline": payload.get("headline"),
                "chart_thesis": memory.get("chart_thesis") or payload.get("summary"),
                "dominant_house": memory.get("dominant_house"),
                "dominant_planet": memory.get("dominant_planet"),
                "growth_theme": memory.get("growth_theme"),
            }
        )
    latest = history[0]
    return {
        "headline": latest.get("headline"),
        "chart_thesis": latest.get("chart_thesis"),
        "dominant_house": latest.get("dominant_house"),
        "dominant_planet": latest.get("dominant_planet"),
        "growth_theme": latest.get("growth_theme"),
        "history": history,
    }


def _build_prompt(
    *,
    core_profile: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None,
    interpretations: dict[str, Any] | None,
    aspects: dict[str, Any] | None,
    prior_memory: dict[str, Any] | None,
    learning_context: dict[str, Any] | None,
) -> str:
    compact_payload = {
        "profile": {
            "baseline": (core_profile or {}).get("baseline"),
            "identity": ((core_profile or {}).get("interpretation") or {}).get("identity") if isinstance((core_profile or {}).get("interpretation"), dict) else None,
            "life_areas": ((core_profile or {}).get("interpretation") or {}).get("life_areas") if isinstance((core_profile or {}).get("interpretation"), dict) else None,
        },
        "natal_summary": natal_summary,
        "angles": (interpretations or {}).get("angles"),
        "life_houses": {
            key: value
            for key, value in ((interpretations or {}).get("houses") or {}).items()
            if str(key) in {"1", "4", "7", "10"} or key in {1, 4, 7, 10}
        },
        "personal_planets": [
            {
                "planet": item.get("planet"),
                "sign": item.get("sign"),
                "house": item.get("house"),
                "profile_lens": item.get("profile_lens"),
            }
            for item in ((interpretations or {}).get("planets") or [])[:7]
            if isinstance(item, dict)
        ],
        "top_aspects": [
            {
                "label": item.get("label"),
                "description": item.get("description"),
                "integration": item.get("integration"),
                "tension_level": item.get("tension_level"),
            }
            for item in ((aspects or {}).get("callouts") or [])[:5]
            if isinstance(item, dict)
        ],
        "prior_memory": prior_memory,
        "learning_summary": (learning_context or {}).get("summary"),
        "natal_memory": (learning_context or {}).get("natal_memory"),
    }
    return (
        "Собери editorial layer для натальной карты пользователя.\n"
        "Это Personal Map (источник), не экран дня и не дубликат длинного портрета из профиля.\n"
        "Не пересказывай подряд дома и планеты. Сначала собери суть карты, потом выдели сильные стороны, напряжения и один следующий шаг.\n"
        "Не используй дневной слой: никаких «сегодня», «фокус дня», призывов перейти в Today.\n"
        "Прошлую memory используй только как короткие тезисы.\n"
        "Если natal_memory показывает, через какие части карты пользователь чаще идёт дальше, подними эти части в gifts, tensions или next_step, но пиши естественно и без упоминания внутренних сигналов.\n"
        f"Данные:\n{json.dumps(compact_payload, ensure_ascii=False)}"
    )


def _parse_editorial_json(raw: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(raw.strip())
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if not isinstance(parsed.get("headline"), str) or not isinstance(parsed.get("summary"), str) or not isinstance(parsed.get("next_step"), str):
        return None
    if not isinstance(parsed.get("memory"), dict):
        return None
    return parsed


def generate_natal_chart_editorial(
    db: Session,
    *,
    user: db_models.User,
    core_profile: dict[str, Any] | None,
    natal_summary: dict[str, Any] | None,
    interpretations: dict[str, Any] | None,
    aspects: dict[str, Any] | None,
    locale: str = "ru",
) -> dict[str, Any]:
    fallback = _fallback_editorial(
        core_profile=core_profile,
        natal_summary=natal_summary,
        interpretations=interpretations,
    )
    learning_service = get_learning_service()
    prior_memory = _build_prior_memory(db, user_id=user.id)
    learning_context = learning_service.build_user_learning_context(db, user_id=user.id)
    fallback = _apply_natal_memory_editorial_bias(
        fallback,
        interpretations=interpretations,
        aspects=aspects,
        learning_context=learning_context,
    )
    fallback["route"] = _build_route_from_editorial(fallback, core_profile=core_profile, learning_context=learning_context)
    prompt_version = learning_service.get_or_create_prompt_version(
        db,
        module=MODULE,
        version=PROMPT_VERSION,
        prompt_kind="system",
        prompt_text=SYSTEM_PROMPT,
        label=SURFACE,
        metadata={"surface": SURFACE},
    )
    latest_snapshot = (
        db.query(CoreProfileSnapshot)
        .filter(CoreProfileSnapshot.user_id == user.id)
        .order_by(CoreProfileSnapshot.updated_at.desc())
        .first()
    )
    user_prompt = _build_prompt(
        core_profile=core_profile,
        natal_summary=natal_summary,
        interpretations=interpretations,
        aspects=aspects,
        prior_memory=prior_memory,
        learning_context=learning_context,
    )

    if not is_llm_chat_configured():
        generation = learning_service.log_generation(
            db,
            module=MODULE,
            surface=SURFACE,
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=resolve_default_chat_model(),
            locale=locale,
            input_payload={"prior_memory": prior_memory},
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="fallback",
            used_fallback=True,
            error_message="llm_key_missing",
            duration_ms=0,
        )
        fallback["generation_log_id"] = generation.id
        return fallback

    client = get_openai_compatible_client()
    if client is None:
        generation = learning_service.log_generation(
            db,
            module=MODULE,
            surface=SURFACE,
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=resolve_default_chat_model(),
            locale=locale,
            input_payload={"prior_memory": prior_memory},
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            normalized_response=fallback,
            status="fallback",
            used_fallback=True,
            error_message="openai_import_missing",
            duration_ms=0,
        )
        fallback["generation_log_id"] = generation.id
        return fallback

    model_id = resolve_default_chat_model()
    started_at = perf_counter()
    try:
        content = chat_completion_text(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.45,
            max_tokens=resolve_max_tokens(700),
            json_object=True,
        )
        parsed = _parse_editorial_json(content) if content else None
        if not parsed:
            generation = learning_service.log_generation(
                db,
                module=MODULE,
                surface=SURFACE,
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale=locale,
                input_payload={"prior_memory": prior_memory},
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                raw_response=content,
                normalized_response=fallback,
                status="fallback",
                used_fallback=True,
                error_message="invalid_or_unusable_response",
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            fallback["generation_log_id"] = generation.id
            return fallback

        editorial = {
            "headline": _trim(parsed.get("headline")),
            "summary": _trim(parsed.get("summary")),
            "gifts": _safe_list(parsed.get("gifts"), limit=3) or fallback["gifts"],
            "tensions": _safe_list(parsed.get("tensions"), limit=3) or fallback["tensions"],
            "next_step": _trim(parsed.get("next_step"), fallback["next_step"]),
            "memory": {
                "chart_thesis": _trim((parsed.get("memory") or {}).get("chart_thesis"), fallback["memory"]["chart_thesis"]),
                "dominant_house": _trim((parsed.get("memory") or {}).get("dominant_house"), fallback["memory"]["dominant_house"]),
                "dominant_planet": _trim((parsed.get("memory") or {}).get("dominant_planet"), fallback["memory"]["dominant_planet"]),
                "growth_theme": _trim((parsed.get("memory") or {}).get("growth_theme"), fallback["memory"]["growth_theme"]),
            },
        }
        editorial = _apply_natal_memory_editorial_bias(
            editorial,
            interpretations=interpretations,
            aspects=aspects,
            learning_context=learning_context,
        )
        editorial["route"] = _build_route_from_editorial(editorial, core_profile=core_profile, learning_context=learning_context)
        generation = learning_service.log_generation(
            db,
            module=MODULE,
            surface=SURFACE,
            user_id=user.id,
            core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
            prompt_version_id=prompt_version.id,
            model=model_id,
            locale=locale,
            input_payload={"prior_memory": prior_memory},
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            raw_response=content,
            normalized_response=editorial,
            status="success",
            used_fallback=False,
            duration_ms=int((perf_counter() - started_at) * 1000),
        )
        editorial["generation_log_id"] = generation.id
        return editorial
    except Exception as exc:
        logger.warning("Natal chart editorial generation failed: %s", exc, exc_info=True)
        try:
            generation = learning_service.log_generation(
                db,
                module=MODULE,
                surface=SURFACE,
                user_id=user.id,
                core_profile_snapshot_id=latest_snapshot.id if latest_snapshot else None,
                prompt_version_id=prompt_version.id,
                model=model_id,
                locale=locale,
                input_payload={"prior_memory": prior_memory},
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                normalized_response=fallback,
                status="error",
                used_fallback=True,
                error_message=str(exc),
                duration_ms=int((perf_counter() - started_at) * 1000),
            )
            fallback["generation_log_id"] = generation.id
        except Exception:
            logger.debug("Failed to log natal editorial fallback", exc_info=True)
        fallback["route"] = _build_route_from_editorial(fallback, core_profile=core_profile, learning_context=learning_context)
        return fallback
